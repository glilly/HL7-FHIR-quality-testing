#!/usr/bin/env node
/**
 * Generalized Bonnie/cqm-models package builder for 2026 shortlist QDM measures.
 *
 * Usage:
 *   VSAC_API_KEY=... node scripts/build-cqm-package.js CMS122v14
 *   node scripts/build-cqm-package.js --all
 */
"use strict";

const fs = require("fs");
const path = require("path");
const https = require("https");

const ROOT = path.resolve(__dirname, "..");
const ARTIFACTS = path.join(ROOT, "2026/artifacts/extracted-shortlist");

const MEASURES = {
  CMS165v14: {
    dir: "CMS165-v14.0.000-QDM",
    title: "Controlling High Blood Pressure",
    mainPrefix: "CMS165",
  },
  CMS122v14: {
    dir: "CMS122-v14.0.000-QDM",
    title: "Diabetes: Glycemic Status Assessment Greater Than 9%",
    mainPrefix: "CMS122",
  },
  CMS125v14: {
    dir: "CMS125-v14.0.000-QDM",
    title: "Breast Cancer Screening",
    mainPrefix: "CMS125",
  },
  CMS130v14: {
    dir: "CMS130-v14.0.000-QDM",
    title: "Colorectal Cancer Screening",
    mainPrefix: "CMS130",
  },
  CMS131v14: {
    dir: "CMS131-v14.0.000-QDM",
    title: "Diabetes: Eye Exam",
    mainPrefix: "CMS131",
  },
  CMS138v14: {
    dir: "CMS138-v14.0.000-QDM",
    title: "Tobacco Use: Screening and Cessation Intervention",
    mainPrefix: "CMS138",
  },
  CMS2v15: {
    dir: "CMS2-v15.0.000-QDM",
    title: "Screening for Depression and Follow-Up Plan",
    mainPrefix: "CMS2",
  },
  CMS22v14: {
    dir: "CMS22-v14.0.000-QDM",
    title: "Preventive Care and Screening: Screening for High Blood Pressure and Follow-Up Documented",
    mainPrefix: "CMS22",
  },
  CMS68v15: {
    dir: "CMS68-v15.0.000-QDM",
    title: "Documentation of Current Medications in the Medical Record",
    mainPrefix: "CMS68",
  },
};

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

function discoverLibs(srcDir, mainPrefix) {
  const resources = path.join(srcDir, "resources");
  const files = fs
    .readdirSync(resources)
    .filter((f) => f.endsWith(".json"))
    .map((f) => f.replace(/\.json$/, ""));
  const main = files.find((f) => f.startsWith(mainPrefix));
  if (!main) {
    throw new Error(`No main library starting with ${mainPrefix} in ${resources}`);
  }
  const others = files.filter((f) => f !== main);
  return [{ file: main, isMain: true }, ...others.map((file) => ({ file, isMain: false }))];
}

function buildCqlLibrary(srcDir, meta) {
  const resPath = path.join(srcDir, "resources", `${meta.file}.json`);
  const cqlPath = path.join(srcDir, "cql", `${meta.file}.cql`);
  const elmWrap = loadJson(resPath);
  const elm = elmWrap.library ? { library: elmWrap.library } : elmWrap;
  const library = elm.library || elm;
  const ident = library.identifier || {};
  const names = statementNames(library);
  const cql = fs.existsSync(cqlPath) ? fs.readFileSync(cqlPath, "utf8") : "";
  return {
    library_name: ident.id || meta.file,
    library_version: ident.version || "0.0.000",
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
    const urn = oid.startsWith("urn:oid:") ? oid : `urn:oid:${oid}`;
    out.push({
      _id: urn,
      oid: urn,
      display_name,
      version: "",
      concepts,
    });
  }
  return { valueSets: out, expanded, total: byOid.size };
}

function pickStatement(names, candidates, fallback) {
  for (const c of candidates) {
    if (names.includes(c)) return c;
  }
  return fallback;
}

async function buildOne(cmsId) {
  const cfg = MEASURES[cmsId];
  if (!cfg) throw new Error(`Unknown measure ${cmsId}`);
  const srcDir = path.join(ARTIFACTS, cfg.dir);
  if (!fs.existsSync(path.join(srcDir, "resources"))) {
    throw new Error(`Missing eCQI extract at ${srcDir}`);
  }
  const outDir = path.join(ROOT, "2026/measures", cmsId, "cqm");
  fs.mkdirSync(outDir, { recursive: true });

  const libs = discoverLibs(srcDir, cfg.mainPrefix);
  const cql_libraries = libs.map((meta) => buildCqlLibrary(srcDir, meta));
  const main = cql_libraries.find((l) => l.is_main_library);
  const names = statementNames(main.elm.library || main.elm);
  const byOid = collectValueSetIds(cql_libraries);
  const { valueSets, expanded, total } = await buildValueSets(byOid);

  const measure = {
    cms_id: cmsId,
    title: cfg.title,
    description: `Assembled from eCQI 2026 QDM ELM (${cfg.dir}). Not a Bonnie/MADiE export.`,
    hqmf_id: cmsId,
    hqmf_set_id: cmsId,
    hqmf_version_number: cmsId.includes("v15") ? "15" : "14",
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
    population_criteria: { IPP: {}, DENOM: {}, NUMER: {}, DENEX: {} },
    population_sets: [
      {
        population_set_id: "PopulationCriteria1",
        title: "Population Criteria Section",
        populations: {
          _type: "CQM::ProportionPopulationMap",
          IPP: {
            library_name: main.library_name,
            statement_name: pickStatement(names, ["Initial Population"], "Initial Population"),
          },
          DENOM: {
            library_name: main.library_name,
            statement_name: pickStatement(names, ["Denominator"], "Denominator"),
          },
          NUMER: {
            library_name: main.library_name,
            statement_name: pickStatement(names, ["Numerator"], "Numerator"),
          },
          DENEX: {
            library_name: main.library_name,
            statement_name: pickStatement(
              names,
              ["Denominator Exclusions", "Denominator Exclusion"],
              names.find((n) => /exclusion/i.test(n)) || "Denominator Exclusions"
            ),
          },
        },
        supplemental_data_elements: ["SDE Ethnicity", "SDE Payer", "SDE Race", "SDE Sex"]
          .filter((n) => names.includes(n))
          .map((statement_name) => ({
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

  fs.writeFileSync(path.join(outDir, "measure.json"), JSON.stringify(measure, null, 2) + "\n");
  const vsPath = path.join(outDir, "value_sets.json");
  if (expanded === 0 && fs.existsSync(vsPath)) {
    try {
      const prev = JSON.parse(fs.readFileSync(vsPath, "utf8"));
      const prevArr = Array.isArray(prev) ? prev : prev.value_sets || prev.valueSets || [];
      const prevExpanded = prevArr.filter((v) => v && Array.isArray(v.concepts) && v.concepts.length).length;
      if (prevExpanded > 0) {
        console.warn(
          `Keeping existing ${cmsId} value_sets.json (${prevExpanded} expanded); refusing empty VSAC overwrite`
        );
        return { cmsId, expanded: prevExpanded, total, outDir, keptExisting: true };
      }
    } catch (err) {
      console.warn(`Could not inspect existing value_sets.json: ${err.message}`);
    }
  }
  fs.writeFileSync(vsPath, JSON.stringify(valueSets, null, 2) + "\n");
  console.log(`Wrote ${cmsId}: value sets ${expanded}/${total}`);
  return { cmsId, expanded, total, outDir };
}

async function main() {
  const args = process.argv.slice(2).filter((a) => a !== "--all");
  const all = process.argv.includes("--all");
  const ids = all ? Object.keys(MEASURES) : args;
  if (!ids.length) {
    console.error("Usage: node scripts/build-cqm-package.js CMS122v14 [| --all]");
    process.exit(2);
  }
  const results = [];
  for (const id of ids) {
    try {
      results.push(await buildOne(id));
    } catch (err) {
      console.error(`FAILED ${id}: ${err.message}`);
      results.push({ cmsId: id, error: err.message });
    }
  }
  const summaryPath = path.join(ROOT, "2026/measures/OVERNIGHT_CQM_BUILD_SUMMARY.json");
  fs.writeFileSync(summaryPath, JSON.stringify(results, null, 2) + "\n");
  console.log(`SUMMARY=${summaryPath}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
