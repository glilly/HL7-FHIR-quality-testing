#!/usr/bin/env node
/**
 * Evaluate CQL for a manifest of FHIR Bundle paths (with DFN).
 *
 * Usage:
 *   node scripts/evaluate-cqm-manifest.js CMS165v14 --manifest path.tsv [--out-dir dir]
 *
 * Manifest TSV columns: bundle_path<TAB>dfn
 * --out-dir defaults to 2026/cohorts/{cms}/c0x-cql (historical devfhir lane).
 */
"use strict";

const fs = require("fs");
const path = require("path");
const { patientFrom } = require("./fhir-to-qdm-patient");

const ROOT = path.resolve(__dirname, "..");

function loadJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function readManifest(file) {
  const lines = fs.readFileSync(file, "utf8").trim().split("\n");
  const rows = [];
  for (const line of lines) {
    if (!line.trim() || line.startsWith("bundle_path")) continue;
    const [bundlePath, dfn] = line.split("\t");
    if (!bundlePath || !fs.existsSync(bundlePath)) {
      console.error(`skip missing bundle: ${bundlePath}`);
      continue;
    }
    rows.push({ bundlePath, dfn: String(dfn || "").trim() });
  }
  return rows;
}

function statementTrue(pc, names) {
  const srRoot = pc.statement_results || {};
  const sr = Object.values(srRoot)[0] || {};
  for (const name of names) {
    if (Number(pc[name] || 0)) return true;
    const st = sr[name];
    if (!st) continue;
    if (st === true || st === 1) return true;
    if (typeof st === "object" && (st.raw === true || st.final === "TRUE" || st.pretty === true)) return true;
  }
  return false;
}

function popsFromResult(result) {
  const patientResults = result.patientResults || result || {};
  const keys = Object.keys(patientResults);
  if (!keys.length) return { ipp: 0, denom: 0, numer: 0, denex: 0 };
  const pr = patientResults[keys[0]] || {};
  const pc = pr.PopulationCriteria1 || Object.values(pr)[0] || {};
  return {
    ipp: statementTrue(pc, ["IPP", "Initial Population"]) ? 1 : 0,
    // CMS138 is multi-rate (Denominator 1/2/3); accept any rate for cohort flags.
    denom: statementTrue(pc, ["DENOM", "Denominator", "Denominator 1", "Denominator 2", "Denominator 3"]) ? 1 : 0,
    numer: statementTrue(pc, ["NUMER", "Numerator", "Numerator 1", "Numerator 2", "Numerator 3"]) ? 1 : 0,
    denex: statementTrue(pc, ["DENEX", "Denominator Exclusion"]) ? 1 : 0,
  };
}

async function main() {
  const args = process.argv.slice(2);
  const cmsId = args.find((a) => !a.startsWith("--"));
  const mIdx = args.indexOf("--manifest");
  if (!cmsId || mIdx < 0 || !args[mIdx + 1]) {
    console.error("Usage: node scripts/evaluate-cqm-manifest.js CMS165v14 --manifest path.tsv");
    process.exit(2);
  }
  const manifest = args[mIdx + 1];
  const rows = readManifest(manifest);
  if (!rows.length) throw new Error("No bundles in manifest");

  const measureDir = path.join(ROOT, "2026/measures", cmsId, "cqm");
  const measurePath = path.join(measureDir, "measure.json");
  const valueSetsPath = path.join(measureDir, "value_sets.json");
  if (!fs.existsSync(measurePath) || !fs.existsSync(valueSetsPath)) {
    throw new Error(`Missing cqm package for ${cmsId}`);
  }
  const valueSetsRaw = loadJson(valueSetsPath);
  const valueSets = Array.isArray(valueSetsRaw)
    ? valueSetsRaw
    : valueSetsRaw.value_sets || valueSetsRaw.valueSets || [];
  const expanded = valueSets.filter((vs) => Array.isArray(vs.concepts) && vs.concepts.length > 0).length;
  if (!expanded) throw new Error(`value_sets.json for ${cmsId} has 0 expansions`);

  const { Calculator } = require("cqm-execution");
  const measure = loadJson(measurePath);
  const oIdx = args.indexOf("--out-dir");
  const outDir =
    oIdx >= 0 && args[oIdx + 1]
      ? path.resolve(args[oIdx + 1])
      : path.join(ROOT, "2026/cohorts", cmsId, "c0x-cql");
  fs.mkdirSync(outDir, { recursive: true });

  const outRows = ["dfn\tbundle_path\tipp\tdenom\tnumer\tdenex\telements\n"];
  let nIpp = 0,
    nDenom = 0,
    nNumer = 0;

  for (const row of rows) {
    const bundle = loadJson(row.bundlePath);
    const qdm = patientFrom(bundle);
    const qdmPath = path.join(outDir, `${row.dfn || "unknown"}.qdm.json`);
    fs.writeFileSync(qdmPath, JSON.stringify(qdm, null, 2) + "\n");
    const result = await Calculator.calculate(measure, [qdm], valueSets, {
      doPretty: true,
      includeClauseResults: false,
    });
    const pops = popsFromResult(result);
    nIpp += pops.ipp;
    nDenom += pops.denom;
    nNumer += pops.numer;
    outRows.push(
      `${row.dfn}\t${row.bundlePath}\t${pops.ipp}\t${pops.denom}\t${pops.numer}\t${pops.denex}\t${qdm.dataElements.length}\n`
    );
    console.log(
      JSON.stringify({
        dfn: row.dfn,
        ...pops,
        elements: qdm.dataElements.length,
      })
    );
  }

  const tsvPath = path.join(outDir, "cql-results.tsv");
  fs.writeFileSync(tsvPath, outRows.join(""));
  const summary = {
    cms_id: cmsId,
    patients: rows.length,
    expanded_value_sets: expanded,
    ipp: nIpp,
    denom: nDenom,
    numer: nNumer,
    results: tsvPath,
  };
  fs.writeFileSync(path.join(outDir, "cql-summary.json"), JSON.stringify(summary, null, 2) + "\n");
  console.log(JSON.stringify(summary));
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
