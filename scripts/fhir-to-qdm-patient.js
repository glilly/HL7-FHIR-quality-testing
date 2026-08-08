#!/usr/bin/env node
/**
 * Convert a FHIR R4 Bundle (or transaction/collection) into a Project Tacoma
 * QDM patient JSON sketch suitable for later cqm-execution.
 *
 * Bridge slice for CMS165/CMS122/CMS125/CMS138: Patient, Conditions,
 * Encounters, Observations (BP / labs / tobacco), and mammography evidence as
 * Diagnostic Study, Performed. It does not invent value-set membership except
 * a small SNOMED→LOINC bridge for Synthea mammography Procedures (CMS125 VS is
 * LOINC-only).
 */
"use strict";

const fs = require("fs");
const path = require("path");

function resources(bundle) {
  return (bundle.entry || [])
    .map((e) => e && e.resource)
    .filter(Boolean);
}

function asBundle(input) {
  if (input && input.resourceType === "Bundle") {
    return input;
  }
  if (input && input.fhirBundle && input.fhirBundle.resourceType === "Bundle") {
    return input.fhirBundle;
  }
  throw new Error(
    "Input must be a FHIR Bundle. Codex updatepatient responses are not source bundles; use the original selected-18.tsv bundle path or a /fhir Bundle export."
  );
}

function codingList(codeable) {
  if (!codeable) return [];
  const rawCodings = codeable.code && codeable.system ? [codeable] : codeable.coding || [];
  const out = [];
  for (const coding of rawCodings) {
    if (!coding || !coding.code) continue;
    out.push({
      code: String(coding.code),
      system: systemOid(coding.system),
      display: coding.display || null,
      version: null,
      _type: "QDM::Code",
    });
  }
  return out;
}

function asUrnOid(oidOrUrn) {
  if (!oidOrUrn) return null;
  const s = String(oidOrUrn);
  if (s.startsWith("urn:oid:")) return s;
  if (/^\d+(\.\d+)+$/.test(s)) return `urn:oid:${s}`;
  return s;
}

function systemOid(system) {
  if (!system) return null;
  // ELM direct-code retrieves use urn:oid:... codesystem ids; keep that form
  // so Physical Exam LOINC SBP/DBP matches CMS165.
  if (system.includes("snomed")) return "urn:oid:2.16.840.1.113883.6.96";
  if (system.includes("loinc")) return "urn:oid:2.16.840.1.113883.6.1";
  if (system.includes("icd-10")) return "urn:oid:2.16.840.1.113883.6.90";
  if (system.includes("cpt")) return "urn:oid:2.16.840.1.113883.6.12";
  if (system.includes("administrative-gender")) return "urn:oid:2.16.840.1.113883.5.1";
  if (system.includes("race")) return "urn:oid:2.16.840.1.113883.6.238";
  if (system.includes("ethnicity")) return "urn:oid:2.16.840.1.113883.6.238";
  return asUrnOid(system);
}

function instant(value) {
  if (!value) return null;
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return null;
  return d.toISOString();
}

const SNOMED_OID = "urn:oid:2.16.840.1.113883.6.96";
const SEX_FINDING = {
  female: { code: "248152002", display: "Female (finding)" },
  male: { code: "248153007", display: "Male (finding)" },
};

function extensionCoding(patient, urlPart) {
  for (const ext of patient.extension || []) {
    if (!(ext.url || "").toLowerCase().includes(String(urlPart).toLowerCase())) continue;
    if (ext.valueCode) return { code: String(ext.valueCode) };
    const cc = ext.valueCodeableConcept;
    if (!cc) continue;
    const coding = (cc.coding || []).find((c) => c && c.code);
    if (coding) return coding;
    if (cc.text) return { code: String(cc.text) };
  }
  return null;
}

/** Map FHIR Patient sex → SNOMED finding codes used by CMS125/Federal Administrative Sex. */
function sexFindingFromPatient(patient) {
  const sex = extensionCoding(patient, "us-core-sex");
  if (sex && (sex.code === "248152002" || sex.code === "248153007")) {
    return {
      code: sex.code,
      display: sex.display || (sex.code === "248152002" ? SEX_FINDING.female.display : SEX_FINDING.male.display),
      system: SNOMED_OID,
    };
  }
  const birthsex = extensionCoding(patient, "us-core-birthsex") || extensionCoding(patient, "birthsex");
  const bs = String(birthsex?.code || "").toUpperCase();
  if (bs === "F" || bs === "FEMALE") return { ...SEX_FINDING.female, system: SNOMED_OID };
  if (bs === "M" || bs === "MALE") return { ...SEX_FINDING.male, system: SNOMED_OID };
  const g = String(patient.gender || "").toLowerCase();
  if (g === "female") return { ...SEX_FINDING.female, system: SNOMED_OID };
  if (g === "male") return { ...SEX_FINDING.male, system: SNOMED_OID };
  return null;
}

function periodFrom(resource) {
  const start =
    resource.period?.start ||
    resource.performedDateTime ||
    resource.performedPeriod?.start ||
    resource.effectiveDateTime ||
    resource.effectivePeriod?.start ||
    resource.onsetDateTime ||
    resource.issued ||
    null;
  const end =
    resource.period?.end ||
    resource.performedPeriod?.end ||
    resource.performedDateTime ||
    resource.effectivePeriod?.end ||
    start;
  const low = instant(start);
  if (!low) return null;
  return {
    low,
    high: instant(end) || low,
    lowClosed: true,
    highClosed: true,
  };
}

function clinicalStatusCode(resource) {
  const coding =
    (resource.clinicalStatus && resource.clinicalStatus.coding) || [];
  return String((coding[0] && coding[0].code) || "").toLowerCase();
}

/** QDM/CQL Quantity result; normalize UCUM mmHg → mm[Hg] for CMS165. */
function quantityResult(vq) {
  if (!vq || vq.value == null || vq.value === "") return null;
  let unit = vq.code || vq.unit || null;
  if (!unit) return null;
  if (unit === "mmHg" || unit === "mm Hg") unit = "mm[Hg]";
  return { value: Number(vq.value), unit };
}

/** CMS138 Tobacco Use Screening LOINCs (VSAC oid 2.16.840.1.113883.3.526.3.1278). */
const TOBACCO_SCREENING_LOINC = new Set([
  "72166-2",
  "68535-4",
  "68536-2",
  "39240-7",
]);

/** QDM Code result from FHIR CodeableConcept (smoking status, etc.). */
function codeableResult(codeable) {
  const codes = codingList(codeable);
  return codes.length ? codes[0] : null;
}

/** Synthea mammography Procedures use SNOMED; CMS125 Mammography VS is LOINC. */
const MAMMO_SCT_TO_LOINC = {
  // CMS125 Mammography VS (2.16.840.1.113883.3.464.1003.108.12.1018) is LOINC-only.
  "71651007": { code: "24606-6", display: "MG Breast Screening" },
  "24623002": { code: "24606-6", display: "MG Breast Screening" },
};

function mammoLoincFromCodes(codes) {
  for (const c of codes || []) {
    if (!c || !c.code) continue;
    if ((c.system || "").includes("113883.6.1") || (c.system || "").toLowerCase().includes("loinc")) {
      return null; // already LOINC; caller keeps original codes
    }
    const bridge = MAMMO_SCT_TO_LOINC[String(c.code)];
    if (bridge) {
      return {
        code: bridge.code,
        system: "urn:oid:2.16.840.1.113883.6.1",
        display: bridge.display,
        version: null,
        _type: "QDM::Code",
      };
    }
  }
  return null;
}

function isMammoEvidence(resource, codes) {
  if (mammoLoincFromCodes(codes)) return true;
  for (const c of codes || []) {
    const sys = (c.system || "").toLowerCase();
    const disp = (c.display || "").toLowerCase();
    if (sys.includes("113883.6.1") || sys.includes("loinc")) {
      if (
        disp.includes("mg breast") ||
        disp.includes("mammograph") ||
        disp.includes("dbt breast") ||
        String(c.code).startsWith("2460") ||
        String(c.code).startsWith("2617") ||
        String(c.code).startsWith("10388")
      ) {
        return true;
      }
    }
  }
  return false;
}

function pushDiagnosticStudy(dataElements, resource, codes, bridgeHint) {
  const when =
    instant(resource.performedDateTime) ||
    instant(resource.performedPeriod?.start) ||
    instant(resource.performedPeriod?.end) ||
    instant(resource.effectiveDateTime) ||
    instant(resource.effectivePeriod?.start) ||
    instant(resource.issued);
  const period =
    periodFrom(resource) ||
    (when ? { low: when, high: when, _type: "QDM::Interval" } : null);
  if (!when && !period) return;
  const bridged = mammoLoincFromCodes(codes);
  const dataElementCodes = bridged ? [bridged, ...codes] : codes;
  dataElements.push({
    authorDatetime: when || (period && period.low) || null,
    category: "diagnostic_study",
    dataElementCodes,
    description:
      "Diagnostic Study, Performed: " +
      (resource.code?.text || dataElementCodes[0].display || dataElementCodes[0].code),
    hqmfOid: "2.16.840.1.113883.10.20.28.4.23",
    relevantDatetime: when || (period && period.low) || null,
    relevantPeriod: period,
    qdmStatus: "performed",
    qdmVersion: "5.6",
    _type: "QDM::DiagnosticStudyPerformed",
    _bridgeHint: bridgeHint,
  });
}

function isTobaccoScreeningObservation(resource, codes) {
  if (codes.some((c) => TOBACCO_SCREENING_LOINC.has(String(c.code)))) return true;
  const categories = (resource.category || [])
    .flatMap((c) => (c.coding || []).map((x) => String(x.code || "").toLowerCase()));
  if (categories.includes("social-history") && codes.some((c) => String(c.code).startsWith("72166"))) {
    return true;
  }
  return false;
}

/**
 * QDM Diagnosis prevalencePeriod.
 * FHIR Conditions often have onset without abatement; treating that as a
 * point-in-time interval makes CMS165 "overlaps MP" fail. Ongoing /
 * active (or unspecified) conditions use high=null + highClosed=true, which
 * cql-execution treats as +infinity.
 */
function prevalencePeriodFrom(resource) {
  const start =
    resource.onsetDateTime ||
    resource.onsetPeriod?.start ||
    resource.recordedDate ||
    null;
  const abatement =
    resource.abatementDateTime ||
    resource.abatementPeriod?.end ||
    resource.abatementPeriod?.start ||
    null;
  const low = instant(start);
  if (!low) return null;

  if (abatement) {
    return {
      low,
      high: instant(abatement) || low,
      lowClosed: true,
      highClosed: true,
    };
  }

  const status = clinicalStatusCode(resource);
  const ended = status === "resolved" || status === "inactive" || status === "remission";
  if (ended) {
    // No abatement timestamp: keep a closed point at onset/recorded.
    return {
      low,
      high: low,
      lowClosed: true,
      highClosed: true,
    };
  }

  return {
    low,
    high: null,
    lowClosed: true,
    highClosed: true,
  };
}

function patientFrom(bundle) {
  bundle = asBundle(bundle);
  const all = resources(bundle);
  const patient = all.find((r) => r.resourceType === "Patient") || {};
  const name = (patient.name && patient.name[0]) || {};
  const given = name.given || [];
  const family = name.family || "UNKNOWN";
  const birth = instant(patient.birthDate) || "1970-01-01T00:00:00.000Z";
  const dataElements = [];

  dataElements.push({
    birthDatetime: birth,
    category: "patient_characteristic",
    dataElementCodes: [
      {
        code: "21112-8",
        display: null,
        system: "2.16.840.1.113883.6.1",
        version: null,
        _type: "QDM::Code",
      },
    ],
    description: null,
    hqmfOid: "2.16.840.1.113883.10.20.28.3.54",
    qdmStatus: "birthdate",
    qdmVersion: "5.6",
    _type: "QDM::PatientCharacteristicBirthdate",
  });

  const sexFinding = sexFindingFromPatient(patient);
  if (sexFinding) {
    dataElements.push({
      authorDatetime: birth,
      category: "patient_characteristic",
      dataElementCodes: [
        {
          code: sexFinding.code,
          display: sexFinding.display,
          system: sexFinding.system,
          version: null,
          _type: "QDM::Code",
        },
      ],
      description: "Patient Characteristic Sex",
      hqmfOid: "2.16.840.1.113883.10.20.28.4.55",
      qdmStatus: "gender",
      qdmVersion: "5.6",
      _type: "QDM::PatientCharacteristicSex",
    });
  }

  for (const resource of all) {
    if (resource.resourceType === "Condition") {
      const codes = codingList(resource.code);
      if (!codes.length) continue;
      dataElements.push({
        authorDatetime: instant(resource.recordedDate) || instant(resource.onsetDateTime),
        category: "condition",
        dataElementCodes: codes,
        description: "Diagnosis: " + (resource.code?.text || codes[0].code),
        hqmfOid: "2.16.840.1.113883.10.20.28.4.110",
        prevalencePeriod: prevalencePeriodFrom(resource),
        qdmVersion: "5.6",
        _type: "QDM::Diagnosis",
      });
    }
    if (resource.resourceType === "Encounter") {
      const codes = codingList((resource.type && resource.type[0]) || resource.class);
      const period = periodFrom(resource);
      if (!period) continue;
      dataElements.push({
        authorDatetime: period.low,
        category: "encounter",
        dataElementCodes: codes.length
          ? codes
          : [
              {
                code: "AMB",
                system: "2.16.840.1.113883.5.4",
                display: "ambulatory",
                version: null,
                _type: "QDM::Code",
              },
            ],
        description: "Encounter, Performed",
        hqmfOid: "2.16.840.1.113883.10.20.28.4.5",
        relevantPeriod: period,
        qdmStatus: "performed",
        qdmVersion: "5.6",
        _type: "QDM::EncounterPerformed",
      });
    }
    if (resource.resourceType === "Procedure" || resource.resourceType === "DiagnosticReport") {
      const codes = codingList(resource.code);
      if (codes.length && isMammoEvidence(resource, codes)) {
        pushDiagnosticStudy(
          dataElements,
          resource,
          codes,
          resource.resourceType === "Procedure" ? "procedure-mammo" : "diagnosticreport-mammo"
        );
      }
    }
    if (resource.resourceType === "Observation") {
      const codes = codingList(resource.code);
      if (!codes.length) continue;
      const categories = (resource.category || [])
        .flatMap((c) => (c.coding || []).map((x) => String(x.code || "").toLowerCase()));
      const isVital = categories.includes("vital-signs") || codes.some((c) => c.code === "85354-9");
      const isLab = categories.includes("laboratory");
      const when =
        instant(resource.effectiveDateTime) ||
        instant(resource.effectivePeriod?.start) ||
        instant(resource.issued);
      const period = periodFrom(resource);
      const components = [];

      // CMS138: Tobacco Use Screening is Assessment, Performed (not Physical Exam).
      if (isTobaccoScreeningObservation(resource, codes)) {
        const result = codeableResult(resource.valueCodeableConcept);
        dataElements.push({
          authorDatetime: when,
          category: "assessment",
          dataElementCodes: codes,
          description:
            "Assessment, Performed: " + (resource.code?.text || codes[0].display || codes[0].code),
          hqmfOid: "2.16.840.1.113883.10.20.28.4.117",
          relevantDatetime: when,
          relevantPeriod: period,
          result,
          qdmStatus: "performed",
          qdmVersion: "5.6",
          _type: "QDM::AssessmentPerformed",
          _bridgeHint: "tobacco-screening",
        });
        continue;
      }

      // CMS165 retrieves SBP/DBP as distinct Physical Exam, Performed codes
      // (8480-6 / 8462-4) with Quantity result.unit = 'mm[Hg]'. Synthea stores
      // those as components of a blood-pressure panel — expand them.
      for (const comp of resource.component || []) {
        const cCodes = codingList(comp.code);
        const q = quantityResult(comp.valueQuantity);
        if (!cCodes.length || !q) continue;
        components.push({
          code: cCodes[0],
          result: q,
          _type: "QDM::Component",
        });
        if (!isLab) {
          dataElements.push({
            authorDatetime: when,
            category: "physical_exam",
            dataElementCodes: cCodes,
            description: "Physical Exam, Performed: " + (cCodes[0].display || cCodes[0].code),
            hqmfOid: "2.16.840.1.113883.10.20.28.4.62",
            relevantDatetime: when,
            relevantPeriod: period,
            result: q,
            qdmStatus: "performed",
            qdmVersion: "5.6",
            _type: "QDM::PhysicalExamPerformed",
            _bridgeHint: "observation-component",
          });
        }
      }

      const result = quantityResult(resource.valueQuantity);
      dataElements.push({
        authorDatetime: when,
        category: isLab ? "laboratory_test" : "physical_exam",
        components,
        dataElementCodes: codes,
        description: (isLab ? "Laboratory Test, Performed: " : "Physical Exam, Performed: ")
          + (resource.code?.text || codes[0].code),
        hqmfOid: isLab
          ? "2.16.840.1.113883.10.20.28.4.42"
          : "2.16.840.1.113883.10.20.28.4.62",
        relevantDatetime: when,
        relevantPeriod: period,
        result,
        qdmStatus: "performed",
        qdmVersion: "5.6",
        _type: isLab
          ? "QDM::LaboratoryTestPerformed"
          : "QDM::PhysicalExamPerformed",
        _bridgeHint: isVital ? "vital-signs" : isLab ? "laboratory" : "observation",
      });
    }
  }

  return {
    birthDatetime: birth,
    bundleId: patient.id || null,
    dataElements,
    extendedData: {
      medical_record_number: patient.id || null,
      source: "fhir-to-qdm-patient.js",
    },
    familyName: family,
    givenNames: given.length ? given : ["UNKNOWN"],
    qdmVersion: "5.6",
  };
}

function main() {
  const args = process.argv.slice(2);
  if (args.length < 1) {
    console.error("Usage: fhir-to-qdm-patient.js <fhir-bundle.json> [out.json]");
    process.exit(2);
  }
  const input = JSON.parse(fs.readFileSync(args[0], "utf8"));
  const qdm = patientFrom(input);
  const out = args[1] || "-";
  const text = JSON.stringify(qdm, null, 2) + "\n";
  if (out === "-") {
    process.stdout.write(text);
  } else {
    fs.mkdirSync(path.dirname(out), { recursive: true });
    fs.writeFileSync(out, text);
    console.error(`Wrote ${out} with ${qdm.dataElements.length} dataElements`);
  }
}

if (require.main === module) {
  try {
    main();
  } catch (error) {
    console.error(error.message || String(error));
    process.exit(1);
  }
}

module.exports = { patientFrom, resources, prevalencePeriodFrom, periodFrom };
