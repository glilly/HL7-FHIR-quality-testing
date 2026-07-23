#!/usr/bin/env node
/**
 * Best-effort Bonnie/cqm-models package builder for CMS165v14.
 *
 * Builds measure.json from the official eCQI QDM ELM/CQL libraries.
 * value_sets.json still needs VSAC expansions (or a Bonnie/MADiE export):
 *   - set VSAC_API_KEY to attempt SVS download, or
 *   - drop a Bonnie export into 2026/measures/CMS165v14/cqm/
 *
 * Usage:
 *   node scripts/build-cms165-cqm-package.js
 */
"use strict";

const fs = require("fs");
const path = require("path");
const https = require("https");

const ROOT = path.resolve(__dirname, "..");
const SRC = path.join(
  ROOT,
  "2026/artifacts/extracted-shortlist/CMS165-v14.0.000-QDM"
);
const OUT = path.join(ROOT, "2026/measures/CMS165v14/cqm");

const LIBS = [
  {
    file: "CMS165ControllingHighBloodPressure-14.0.000",
    isMain: true,
  },
  { file: "AdultOutpatientEncountersQDM-4.0.000", isMain: false },
  { file: "AdvancedIllnessandFrailtyQDM-10.0.000", isMain: false },
  { file: "CQMCommonQDM-9.0.000", isMain: false },
  { file: "HospiceQDM-7.0.000", isMain: false },
  { file: "PalliativeCareQDM-5.0.000", isMain: false },
];

function loadJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function statementNames(elmLibrary) {
  const defs = (((elmLibrary || {}).statements || {}).def) || [];
  return defs.map((d) => d.name).filter(Boolean);
}

function valueSetRefs(elmLibrary) {
  const defs = (((elmLibrary || {}).valueSets || {}).def) || [];
  return defs
    .map((d) => ({
      name: d.name,
      oid: String(d.id || "").replace(/^urn:oid:/, ""),
    }))
    .filter((d) => d.oid);
}

function buildCqlLibrary(meta) {
  const resPath = path.join(SRC, "resources", `${meta.file}.json`);
  const cqlPath = path.join(SRC, "cql", `${meta.file}.cql`);
  const elmWrap = loadJson(resPath);
  const elm = elmWrap.library ? { library: elmWrap.library } : elmWrap;
  const library = elm.library || elm;
  const ident = library.identifier || {};
  const names = statementNames(library);
  const cql = fs.existsSync(cqlPath) ? fs.readFileSync(cqlPath, "utf8") : "";
  return {
    library_name: ident.id || meta.file,
    library_version: ident.version || "14.0.000",
    is_main_library: !!meta.isMain,
    is_top_level: !!meta.isMain,
    cql,
    elm,
    elm_annotations: {
      statements: names.map((name) => ({
        children: [{ children: [{ text: `define "${name}":\n  ` }] }],
      })),
      identifier: { id: ident.id, version: ident.version },
    },
    statement_dependencies: names.map((statement_name) => ({ statement_name })),
  };
}

function collectValueSetIds(cqlLibraries) {
  const byOid = new Map();
  for (const lib of cqlLibraries) {
    for (const vs of valueSetRefs(lib.elm.library || lib.elm)) {
      if (!byOid.has(vs.oid)) byOid.set(vs.oid, vs.name);
    }
  }
  return byOid;
}

function httpsGet(url, headers) {
  return new Promise((resolve, reject) => {
    const req = https.get(url, { headers }, (res) => {
      let body = "";
      res.on("data", (c) => (body += c));
      res.on("end", () => resolve({ status: res.statusCode, body }));
    });
    req.on("error", reject);
  });
}

async function fetchVsacConcepts(oid, apiKey) {
  // VSAC SVS RetrieveMultipleValueSets
  const url =
    "https://vsac.nlm.nih.gov/vsac/svs/RetrieveMultipleValueSets?" +
    `id=${encodeURIComponent(oid)}`;
  const auth = Buffer.from(`apikey:${apiKey}`).toString("base64");
  const { status, body } = await httpsGet(url, {
    Authorization: `Basic ${auth}`,
    Accept: "application/xml",
  });
  if (status !== 200) {
    throw new Error(`VSAC ${oid} HTTP ${status}`);
  }
  const concepts = [];
  // VSAC SVS XML uses a namespace prefix (e.g. <ns0:Concept .../>).
  const re = /<(?:[\w.-]+:)?Concept\b([^>]*)\/?>/g;
  let m;
  while ((m = re.exec(body))) {
    const attrs = m[1];
    const get = (name) => {
      const am = attrs.match(new RegExp(`\\b${name}="([^"]*)"`));
      return am ? am[1] : "";
    };
    const code = get("code");
    if (!code) continue;
    const codeSystem = get("codeSystem");
    concepts.push({
      code,
      // Match ELM / patient codes that use urn:oid:... systems
      code_system_oid: codeSystem.startsWith("urn:oid:")
        ? codeSystem
        : codeSystem
          ? `urn:oid:${codeSystem}`
          : codeSystem,
      code_system_name: get("codeSystemName"),
      display_name: get("displayName"),
    });
  }
  if (!concepts.length) {
    throw new Error(`VSAC ${oid} returned 200 but parsed 0 concepts`);
  }
  return concepts;
}

async function buildValueSets(byOid) {
  const apiKey = process.env.VSAC_API_KEY || process.env.UMLS_API_KEY || "";
  const out = [];
  let expanded = 0;
  for (const [oid, display_name] of byOid.entries()) {
    let concepts = [];
    if (apiKey) {
      try {
        concepts = await fetchVsacConcepts(oid, apiKey);
        if (concepts.length) expanded += 1;
        console.log(`VSAC expanded ${oid} (${concepts.length} concepts)`);
      } catch (err) {
        console.warn(`VSAC failed for ${oid}: ${err.message}`);
      }
    }
    // cqm-execution / cql-execution look up ELM ids as urn:oid:...
    const urn = oid.startsWith("urn:oid:") ? oid : `urn:oid:${oid}`;
    out.push({
      _id: urn,
      oid: urn,
      display_name,
      // Empty version: ELM refs omit version; CodeService then picks any expansion.
      version: "",
      concepts,
    });
  }
  return { valueSets: out, expanded, total: byOid.size };
}

async function main() {
  if (!fs.existsSync(path.join(SRC, "resources"))) {
    throw new Error(`Missing eCQI extract at ${SRC}`);
  }
  fs.mkdirSync(OUT, { recursive: true });

  const cql_libraries = LIBS.map(buildCqlLibrary);
  const main = cql_libraries.find((l) => l.is_main_library);
  const byOid = collectValueSetIds(cql_libraries);
  const { valueSets, expanded, total } = await buildValueSets(byOid);

  const measure = {
    cms_id: "CMS165v14",
    title: "Controlling High Blood Pressure",
    description:
      "Assembled from eCQI 2026 QDM ELM (CMS165-v14.0.000-QDM). Not a Bonnie/MADiE export.",
    hqmf_id: "CMS165v14",
    hqmf_set_id: "CMS165v14",
    hqmf_version_number: "14",
    main_cql_library: main.library_name,
    measure_scoring: "PROPORTION",
    calculation_method: "PATIENT",
    calculate_sdes: true,
    composite: false,
    component: false,
    component_hqmf_set_ids: [],
    measure_period: {
      type: "IVL_TS",
      low: { type: "TS", value: "20260101000000", inclusive: true },
      high: { type: "TS", value: "20261231235959", inclusive: true },
    },
    population_criteria: {
      IPP: {},
      DENOM: {},
      NUMER: {},
      DENEX: {},
    },
    population_sets: [
      {
        population_set_id: "PopulationCriteria1",
        title: "Population Criteria Section",
        populations: {
          _type: "CQM::ProportionPopulationMap",
          IPP: {
            library_name: main.library_name,
            statement_name: "Initial Population",
          },
          DENOM: {
            library_name: main.library_name,
            statement_name: "Denominator",
          },
          NUMER: {
            library_name: main.library_name,
            statement_name: "Numerator",
          },
          DENEX: {
            library_name: main.library_name,
            statement_name: "Denominator Exclusions",
          },
        },
        supplemental_data_elements: [
          "SDE Ethnicity",
          "SDE Payer",
          "SDE Race",
          "SDE Sex",
        ].map((statement_name) => ({
          library_name: main.library_name,
          statement_name,
        })),
      },
    ],
    source_data_criteria: [],
    value_set_ids: [...byOid.keys()],
    cql_libraries,
    measure_attributes: [],
  };

  const measurePath = path.join(OUT, "measure.json");
  const valueSetsPath = path.join(OUT, "value_sets.json");
  fs.writeFileSync(measurePath, JSON.stringify(measure, null, 2) + "\n");
  fs.writeFileSync(valueSetsPath, JSON.stringify(valueSets, null, 2) + "\n");

  console.log(`Wrote ${measurePath}`);
  console.log(`Wrote ${valueSetsPath}`);
  console.log(`Value sets: ${expanded}/${total} expanded from VSAC`);
  if (expanded === 0) {
    console.log("");
    console.log("No VSAC expansions loaded. cqm-execution will not be meaningful yet.");
    console.log("Set VSAC_API_KEY (UMLS API key) and re-run, or replace value_sets.json");
    console.log("with a Bonnie/MADiE export.");
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
