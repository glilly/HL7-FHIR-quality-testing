#!/usr/bin/env node
/**
 * CMS165 QDM evaluation entrypoint.
 *
 * 1) Convert FHIR Bundle(s) to QDM patients via fhir-to-qdm-patient.js
 * 2) If a Bonnie/cqm-models measure package is present, run cqm-execution
 * 3) Otherwise write converted patients and explain the missing package
 *
 * Expected measure package layout (not shipped in the eCQI QDM ZIP):
 *   2026/measures/CMS165v14/cqm/measure.json
 *   2026/measures/CMS165v14/cqm/value_sets.json
 */
"use strict";

const fs = require("fs");
const path = require("path");
const { patientFrom } = require("./fhir-to-qdm-patient");

const ROOT = path.resolve(__dirname, "..");
const MEASURE_DIR = path.join(ROOT, "2026/measures/CMS165v14/cqm");
const OUT_DIR = path.join(ROOT, "2026/cohorts/CMS165v14/qdm-patients");

function loadJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function listInputs(argv) {
  if (argv.length) return argv;
  const selected = path.join(ROOT, "2026/cohorts/CMS165v14/numer/selected-18.tsv");
  if (!fs.existsSync(selected)) {
    throw new Error("Pass FHIR bundle paths, or create selected-18.tsv first");
  }
  const lines = fs.readFileSync(selected, "utf8").trim().split("\n").slice(1);
  return lines
    .map((line) => line.split("\t")[0])
    .filter((p) => p && fs.existsSync(p));
}

function main() {
  const inputs = listInputs(process.argv.slice(2));
  if (!inputs.length) {
    throw new Error("No FHIR bundle inputs found");
  }
  fs.mkdirSync(OUT_DIR, { recursive: true });
  const patients = [];
  for (const file of inputs) {
    const bundle = loadJson(file);
    const qdm = patientFrom(bundle);
    const base = path.basename(file, path.extname(file));
    const out = path.join(OUT_DIR, `${base}.qdm.json`);
    fs.writeFileSync(out, JSON.stringify(qdm, null, 2) + "\n");
    patients.push(qdm);
    console.log(`converted ${file} -> ${out} (${qdm.dataElements.length} elements)`);
  }

  const measurePath = path.join(MEASURE_DIR, "measure.json");
  const valueSetsPath = path.join(MEASURE_DIR, "value_sets.json");
  if (!fs.existsSync(measurePath) || !fs.existsSync(valueSetsPath)) {
    console.log("");
    console.log("FHIR→QDM bridge wrote patient files, but cqm-execution was not run.");
    console.log("Add a Bonnie / MAT / cqm-models export here:");
    console.log(`  ${measurePath}`);
    console.log(`  ${valueSetsPath}`);
    console.log("The eCQI QDM ZIP only contains CQL/ELM libraries, not that package.");
    console.log(`Converted patients: ${OUT_DIR}`);
    process.exit(0);
  }

  const valueSets = loadJson(valueSetsPath);
  const expanded = (Array.isArray(valueSets) ? valueSets : []).filter(
    (vs) => Array.isArray(vs.concepts) && vs.concepts.length > 0
  ).length;
  if (!expanded) {
    console.log("");
    console.log("measure.json / value_sets.json present, but no expanded concepts.");
    console.log("Run: VSAC_API_KEY=... node scripts/build-cms165-cqm-package.js");
    console.log("Or replace value_sets.json with a Bonnie/MADiE export.");
    console.log(`Converted patients: ${OUT_DIR}`);
    process.exit(0);
  }

  const Calculator = require("cqm-execution").Calculator;
  const measure = loadJson(measurePath);
  let results;
  try {
    results = Calculator.calculate(measure, patients, valueSets, {
      doPretty: true,
    });
  } catch (err) {
    console.error("cqm-execution failed:", err.message || err);
    process.exit(1);
  }
  const reportPath = path.join(ROOT, "2026/cohorts/CMS165v14/reports/cqm-execution-batch.json");
  fs.mkdirSync(path.dirname(reportPath), { recursive: true });
  fs.writeFileSync(reportPath, JSON.stringify(results, null, 2) + "\n");
  console.log(`Wrote ${reportPath}`);
}

try {
  main();
} catch (err) {
  console.error(err.message || err);
  process.exit(1);
}
