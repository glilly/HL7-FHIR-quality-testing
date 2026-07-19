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

function codingList(codeable) {
  if (!codeable) return [];
  const out = [];
  for (const coding of codeable.coding || []) {
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

function systemOid(system) {
  if (!system) return null;
  if (system.includes("snomed")) return "2.16.840.1.113883.6.96";
  if (system.includes("loinc")) return "2.16.840.1.113883.6.1";
  if (system.includes("icd-10")) return "2.16.840.1.113883.6.90";
  if (system.includes("cpt")) return "2.16.840.1.113883.6.12";
  return system;
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

function patientFrom(bundle) {
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
        prevalencePeriod: periodFrom(resource),
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
      const components = [];
      for (const comp of resource.component || []) {
        const cCodes = codingList(comp.code);
        const result = comp.valueQuantity?.value;
        if (!cCodes.length || result == null) continue;
        components.push({
          code: cCodes[0],
          result,
          _type: "QDM::Component",
        });
      }
      const result =
        resource.valueQuantity?.value != null
          ? resource.valueQuantity.value
          : null;
      dataElements.push({
        authorDatetime: instant(resource.effectiveDateTime) || instant(resource.issued),
        category: isLab ? "laboratory_test" : "physical_exam",
        components,
        dataElementCodes: codes,
        description: (isLab ? "Laboratory Test, Performed: " : "Physical Exam, Performed: ")
          + (resource.code?.text || codes[0].code),
        hqmfOid: isLab
          ? "2.16.840.1.113883.10.20.28.4.42"
          : "2.16.840.1.113883.10.20.28.4.47",
        relevantPeriod: periodFrom(resource),
        result,
        resultDatetime: instant(resource.effectiveDateTime) || instant(resource.issued),
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
  main();
}

module.exports = { patientFrom, resources };
