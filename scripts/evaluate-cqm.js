#!/usr/bin/env node
/**
 * Generalized QDM evaluation for a shortlist measure.
 *
 * Usage:
 *   node scripts/evaluate-cqm.js CMS122v14
 *   node scripts/evaluate-cqm.js CMS122v14 --limit 5
 */
"use strict";

const fs = require("fs");
const path = require("path");
const { patientFrom } = require("./fhir-to-qdm-patient");

const ROOT = path.resolve(__dirname, "..");

function loadJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function listInputs(cmsId, limit) {
  const selected = path.join(ROOT, `2026/cohorts/${cmsId}/numer/selected-18.tsv`);
  const showcase = path.join(ROOT, `2026/cohorts/${cmsId}/numer/showcase-1.tsv`);
  const src = fs.existsSync(selected) ? selected : showcase;
  if (!fs.existsSync(src)) {
    throw new Error(`No selected-18/showcase TSV for ${cmsId}`);
  }
  const lines = fs.readFileSync(src, "utf8").trim().split("\n").slice(1);
  let paths = lines.map((line) => line.split("\t")[0]).filter((p) => p && fs.existsSync(p));
  if (limit > 0) paths = paths.slice(0, limit);
  return paths;
}

async function main() {
  const args = process.argv.slice(2);
  const cmsId = args.find((a) => !a.startsWith("--"));
  if (!cmsId) {
    console.error("Usage: node scripts/evaluate-cqm.js CMS122v14 [--limit N]");
    process.exit(2);
  }
  const limitIdx = args.indexOf("--limit");
  const limit = limitIdx >= 0 ? Number(args[limitIdx + 1] || 0) : 0;

  const measureDir = path.join(ROOT, "2026/measures", cmsId, "cqm");
  const outDir = path.join(ROOT, "2026/cohorts", cmsId, "qdm-patients");
  const inputs = listInputs(cmsId, limit);
  if (!inputs.length) throw new Error("No FHIR bundle inputs");

  fs.mkdirSync(outDir, { recursive: true });
  const patients = [];
  for (const file of inputs) {
    const bundle = loadJson(file);
    const qdm = patientFrom(bundle);
    const base = path.basename(file, path.extname(file));
    const out = path.join(outDir, `${base}.qdm.json`);
    fs.writeFileSync(out, JSON.stringify(qdm, null, 2) + "\n");
    patients.push(qdm);
    console.log(`converted ${file} -> ${out} (${qdm.dataElements.length} elements)`);
  }

  const measurePath = path.join(measureDir, "measure.json");
  const valueSetsPath = path.join(measureDir, "value_sets.json");
  if (!fs.existsSync(measurePath) || !fs.existsSync(valueSetsPath)) {
    console.log(`No cqm package for ${cmsId}; wrote QDM patients only.`);
    process.exit(0);
  }
  const valueSetsRaw = loadJson(valueSetsPath);
  // cqm-execution expects a value-set array, not { value_sets: [...] }.
  const valueSets = Array.isArray(valueSetsRaw)
    ? valueSetsRaw
    : valueSetsRaw.value_sets || valueSetsRaw.valueSets || [];
  const expanded = valueSets.filter(
    (vs) => Array.isArray(vs.concepts) && vs.concepts.length > 0
  ).length;
  if (!expanded) {
    console.log(`value_sets.json for ${cmsId} has 0 expansions; skip cqm-execution.`);
    process.exit(0);
  }

  const { Calculator } = require("cqm-execution");
  const measure = loadJson(measurePath);
  const result = await Calculator.calculate(measure, patients, valueSets, {
    doPretty: true,
    includeClauseResults: false,
  });
  const reportDir = path.join(ROOT, "2026/cohorts", cmsId, "reports");
  fs.mkdirSync(reportDir, { recursive: true });
  const batchPath = path.join(reportDir, "cqm-execution-batch.json");
  fs.writeFileSync(batchPath, JSON.stringify(result, null, 2) + "\n");

  // Summarize IPP/DENOM/NUMER counts when present
  let ipp = 0,
    denom = 0,
    numer = 0;
  const patientResults = result.patientResults || result || {};
  for (const key of Object.keys(patientResults)) {
    const pr = patientResults[key] || {};
    const pops = pr.population_sets || pr;
    // cqm-execution shapes vary; count statement results if available
    const statement = pr.statement_results || pr;
    const mainLib = Object.values(statement || {})[0] || {};
    if (mainLib["Initial Population"]) ipp += 1;
    if (mainLib.Denominator || mainLib["Denominator"]) denom += 1;
    if (mainLib.Numerator || mainLib["Numerator"]) numer += 1;
  }
  const summary = {
    cms_id: cmsId,
    patients: patients.length,
    expanded_value_sets: expanded,
    batch: batchPath,
    note: "See batch JSON for per-patient population results",
  };
  fs.writeFileSync(path.join(reportDir, "cqm-execution-summary.json"), JSON.stringify(summary, null, 2) + "\n");
  console.log(JSON.stringify(summary));
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
