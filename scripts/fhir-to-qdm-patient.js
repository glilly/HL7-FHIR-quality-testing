#!/usr/bin/env node
/**
 * Convert a FHIR R4 Bundle (or transaction/collection) into a Project Tacoma
 * QDM patient JSON sketch suitable for later cqm-execution.
 *
 * This is the first bridge slice for CMS165/CMS122: Patient, Conditions,
 * Encounters, and Observations (BP / labs). It does not invent value-set
 * membership; codes are copied through for the evaluator/value-set layer.
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

function periodFrom(resource) {
  const start =
    resource.period?.start ||
    resource.effectiveDateTime ||
    resource.effectivePeriod?.start ||
    resource.onsetDateTime ||
    resource.issued ||
    null;
  const end =
    resource.period?.end ||
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

  if (patient.gender) {
    dataElements.push({
      authorDatetime: birth,
      category: "patient_characteristic",
      dataElementCodes: [
        {
          code: patient.gender[0].toUpperCase(),
          display: patient.gender,
          system: "2.16.840.1.113883.5.1",
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
