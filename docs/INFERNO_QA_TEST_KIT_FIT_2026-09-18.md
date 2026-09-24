# Inferno QA test kits — fit for VistaPlex

Status date: **2026-09-18** (expanded the same day with plain-English kit notes and Bulk)  
Source: [inferno-qa.healthit.gov/test-kits](https://inferno-qa.healthit.gov/test-kits/) (ASTP / MITRE staging)  
Production Inferno (cite this, not QA): [inferno.healthit.gov/test-kits](https://inferno.healthit.gov/test-kits/)

This note records which Inferno kits on the QA catalog we can use, later, or skip — and, for each kit, what the names mean, what Inferno is actually checking, and what we would have to build before a run is honest.

Fit is against two products:

- **Quality Workbench** — live. DEQM MeasureReports, hosted Inferno US Quality Core scorecards, fhirdev / rpmsfhir / altfhir.
- **Coding Workbench** — proposed. Strategy and Sept 18 talk live in [AI-FHIR-CLAIMS](https://github.com/glilly/AI-FHIR-CLAIMS). No Claim profile or PAS client yet.

Related:

- Hosted USQC scorecards and remaining-error plan: [`INFERNO_FHIRDEV_CMS165_REMAINING_ERRORS_AND_PLAN.md`](./INFERNO_FHIRDEV_CMS165_REMAINING_ERRORS_AND_PLAN.md)
- Local USQC wrappers: `Vista-on-FHIR/docs/US_QUALITY_CORE_INFERNO.md` and `Vista-on-FHIR/scripts/usqc-*.sh`
- Coding / claims IGs we would prove against: `AI-FHIR-CLAIMS/docs/CODING_WORKBENCH_DEMO.md`

Words used throughout:

| Short name | English |
| --- | --- |
| **Inferno** | MITRE’s public FHIR test harness for ASTP/ONC. You point it at a URL; it plays the other side of the conversation and scores pass / fail / skip. |
| **FHIR** | Fast Healthcare Interoperability Resources. The JSON (or XML) model for Patient, Observation, Claim, and the rest. |
| **IG** | Implementation Guide. A published profile on top of FHIR (US Core, CARIN Blue Button, Bulk Data, and so on). Inferno tests the IG, not “FHIR in general.” |
| **ASTP / ONC** | Assistant Secretary for Technology Policy / Office of the National Coordinator. The federal office that runs Health IT certification. People still say ONC. |
| **USCDI** | United States Core Data for Interoperability. The federal list of data classes an API is expected to expose. US Core is the FHIR shape of that list. |
| **SMART** | Substitutable Medical Applications, Reusable Technologies. OAuth 2 login so an app can launch and get a token, instead of open HTTP. |
| **Must Support** | Fields the IG says the server must fill when it has the data. Inferno fails you if the field is missing on a resource it retrieved. |

## How to use the QA host

Inferno QA is a **staging demo**. Sessions vanish. It is **not for PHI** or protected data. Data is periodically removed.

Use QA to see **new kits** before standing them up locally. As of this snapshot:

- US Quality Core kit **0.2.0** (2026-09-10) covers **2026 USQC v0.5.0** and **USQC v1.0.0-ballot**.
- ONC **(g)(33) PAS** appeared as version **0.0.0** draft (2026-09-09). Not for certification.

Keep published scorecards on **inferno.healthit.gov** against `https://devfhir.vistaplex.org/fhir` (and `/altfhir`, rpmsfhir). Do not treat a QA session URL as Connectathon or funding evidence.

## Verdict

**Quality is already on the right kit.** Keep US Quality Core as the daily Inferno. An optional US Core 6/7 run on the same synthetic patients is cheap extra evidence. Do not open the full (g)(10) kit until SMART App Launch and Bulk `$export` exist.

**Coding's first Inferno benefit is CARIN Blue Button**, once there is a real FHIR Claim — not a screenshot. PAS, then CRD and DTR, become useful when the workbench can act as a **provider client** against Inferno's reference server. Do not try to make VistA a payer.

**(g)(10), (g)(31), and (g)(33) are a map**, not a pass/fail this month. They tell funders where ONC certification is going. WorldVistA cannot pass them as an EHR API today. A coding-firm product is more often the **client** side of those suites.

## What to do, in order

| Order | Action | Kit | Why now |
| ---: | --- | --- | --- |
| 1 | Keep running. Note kit 0.2.0 now includes the USQC 1.0.0-ballot. | US Quality Core | Same evidence we already take to CMS / Inferno / January Connectathon |
| 2 | Optional second scorecard on fhirdev patients. Skip SMART-only groups. | US Core | Cheap proof that Quality Core Must Support is real US Core |
| 3 | Profile one synthetic Claim, then run server tests. | CARIN Blue Button | Turns the Sept 18 Claim slide into the same Inferno honesty as DEQM |
| 4 | After a Claim exists: act as provider client vs Inferno reference. | PAS, then CRD / DTR | Burden Reduction path from the coding strategy, not a VistA server rewrite |
| 5 | Funded only: SMART launch + `$export`, then open (g)(10). | (g)(10), SMART, Bulk | Epic-in-EHR launch and certified patient/population API |

## PAS, CRD, and DTR — what they are

These three are the Da Vinci **Burden Reduction** set: FHIR instead of a payer portal and a fax when a service might need **prior authorization**. Da Vinci is the HL7 group that writes payer–provider guides. **Burden Reduction** means less phone-and-fax work for the clinic.

They are three different conversations, in this order on a real clinic day:

1. **CRD — Coverage Requirements Discovery.**  
   The clinician is about to order something (an MRI, a drug, a procedure). The EHR asks the payer: “Does this need prior auth? Do we need extra paperwork?” The answer comes back as a **CDS Hook** card — a short on-screen note, not a claim. **CDS Hooks** is a JSON callback into the workflow (the same family as our Quality AI Consult). CRD does **not** submit the auth. It only says whether you have to.

2. **DTR — Documentation Templates and Rules.**  
   If CRD said “yes, we need more,” DTR opens a **Questionnaire** (a form). Rules, often written in **CQL** (Clinical Quality Language — the same language as our eCQMs), pull facts from the chart so the clinician does not retype the whole story. The result is a filled **QuestionnaireResponse**: structured answers the payer asked for. Still not the auth itself.

3. **PAS — Prior Authorization Support.**  
   Now the clinic actually **asks for permission to bill**. That ask is a FHIR **Claim** (type: prior auth, not a bill). The payer answers with a **ClaimResponse**: approved, denied, or pended. This is the object closest to what a coding workbench already talks about.

**Clinic-day order** is CRD → DTR → PAS. **Our Inferno order** is PAS first, then CRD and DTR. PAS is first for us because we already show a Claim in the browser; CRD and DTR need a hooks/questionnaire client we have not built for payers. We act as the **provider client** (clinic asking). We do not host the payer.

The ONC drafts **(g)(31)** and **(g)(33)** are these same two ideas written as certification exams: (g)(31) is CRD, (g)(33) is PAS. They are not extra products.

## (g)(10), (g)(31), and (g)(33) — what they are

These are **not** FHIR implementation guides and **not** Inferno inventions. They are paragraph numbers in the US **Health IT Certification Program** — the federal exam an EHR vendor sits if they want to be a “certified” Health IT module.

The “(g)” is the section of the regulation that covers **APIs and quality**. The full cites are:

| Short name | Regulation | English |
| --- | --- | --- |
| **(g)(10)** | § 170.315(g)(10) Standardized API for Patient and Population Services | The patient-and-population API exam. An app can log in (**SMART**), read the chart as **US Core**, and a system can pull a population (**Bulk `$export`**). This kit is **approved** and used for real certification. Inferno’s (g)(10) kit is those three kits glued together. |
| **(g)(31)** | § 170.315(g)(31) Coverage Requirements Discovery API | The **CRD** exam: can the certified EHR ask the payer, at order time, whether prior auth or extra docs are required? Inferno marks this **draft — not for certification yet**. |
| **(g)(33)** | § 170.315(g)(33) Prior Authorization Support API | The **PAS** exam: can the certified EHR submit the prior-auth Claim and receive the ClaimResponse? Also **draft — not for certification yet**. |

There is no “(g)(32)” on the Inferno QA page. DTR does not have its own (g) number here.

**Who sits these exams.** The **EHR** (or a Health IT module sold as the API), not a coding workbench and not Inferno. We would only take (g)(10) if WorldVistA / RPMS were offered as certified patient/population API software. A coding firm using our workbench is usually the **app** or the **Bulk client**, not the certified module.

**What they are not.** They are not extra clinical products. (g)(10) is SMART + US Core + Bulk with a federal stamp. (g)(31) is CRD with a federal stamp. (g)(33) is PAS with a federal stamp. Passing US Quality Core Inferno is **not** passing (g)(10).

**For us today.** Cite them as the map of where ONC is going. Do not run the full (g)(10) kit until SMART and `$export` exist. Do not claim (g)(31) or (g)(33) at all while Inferno still says draft.

## Hard limits if you click Run on QA today

- Codex answers **open HTTP**. SMART, UDAP, and (g)(10) suites fail on launch, not on Observation shape.
- Server suites need Patient IDs that actually have the profiles under test — the same constraint as USQC. See below.
- For PAS / CRD / DTR, the useful first role is **client against Inferno's reference server**, not “make VistA a payer.”
- Inferno QA does **not** list DEQM, CDex, Risk Adjustment, or PCT. Quality already uses the HL7 validator plus the DEQM reference receiver for that job. Coding should do the same for CDex attachments and AEOB / HCC artifacts until MITRE publishes kits.

### “Patient IDs that actually have the profiles under test”

Inferno’s **server** suites are not a paper test of the CapabilityStatement. You type in one or more **Patient IDs**. Inferno then searches and reads **those people** and checks whatever resources come back against the IG **profile** (the detailed shape: which fields, which codes).

If that patient has no DocumentReference, Inferno cannot score “US Quality Core DocumentReference Must Support.” Those tests **skip** (nothing to look at) or **fail** (the search returned empty when the suite expected at least one). A green CapabilityStatement that says “we support DocumentReference” does not save you. Inferno never opens that document family if none of the IDs you gave have a note.

That is why USQC work picked the **CMS165 selected-18** (and extras like DFN 101090): those charts actually contain blood pressures, labs, encounters, and notes. A random VEHU patient with only a name will produce a scorecard that is almost all skips. The same rule applies to every other server kit: CARIN needs a patient who has a Claim / EOB; US Core allergy tests need an AllergyIntolerance on that ID; Bulk Group export needs Group members who have the types you asked for.

“The same constraint as USQC” means: we already learned this the hard way on Quality Core. Do not point a new server kit at an empty or thin DFN and treat the skip wall as a product failure.

---

## Bulk Data, NDJSON, and running both ends

This is the kit people mean by “Bulk.” Inferno’s page calls it the **Bulk Data Access Test Kit** (version 0.13.1, maturity Low). It tests the HL7 **Bulk Data Access Implementation Guide** — STU1 (v1.0.1) and STU2 (v2.0.0). STU means Standard for Trial Use: published, not the newest ballot.

### What Bulk is, in English

Ordinary FHIR is one patient at a time: `GET /fhir?dfn=101090` or `GET /Patient/101090`. A coding firm or a quality warehouse that needs a thousand charts would have to click a thousand times. That is slow, and it ties up the web listener.

**Bulk Data** is the agreed way to say: “give me this whole population, in the background, as files I can download when they are ready.”

The client sends one kickoff (usually `GET` or `POST` to `$export`). The server answers **202 Accepted** and a **Content-Location** URL. The client polls that URL. When the job is done, the status JSON lists file URLs. The client downloads those files.

Three flavors Inferno names:

| Flavor | URL shape | English |
| --- | --- | --- |
| All patients | `/Patient/$export` | Every patient the token is allowed to see |
| Group of patients | `/Group/{id}/$export` | Only the members of that Group (a named list) |
| System | `/$export` | Everything on the server, including things that are not about a patient (practitioners, locations, …) |

`$export` is a FHIR **operation** — a named action on the server, not a resource type.

For us, **Group `$export`** is the honest first flavor. A quality SETPOP or a C0X cohort is already a named list of DFNs. That list is a Group. “All patients” and “system” can wait.

### What NDJSON is

**NDJSON** means **Newline Delimited JSON** (also called JSON Lines). Inferno and the IG write the media type as `application/fhir+ndjson`.

It is **not** a FHIR Bundle. A Bundle is one JSON object with an `entry` array of resources. NDJSON is a **text file**: one complete JSON object per line, and a newline after each line. No wrapping `[` `]`, no commas between objects.

A tiny Patient file looks like this:

```text
{"resourceType":"Patient","id":"101090","name":[{"family":"HARBER"}]}
{"resourceType":"Patient","id":"101091","name":[{"family":"SMITH"}]}
```

Each line must parse as one FHIR resource. A Bulk export usually makes **one file per resource type** (`Patient.ndjson`, `Condition.ndjson`, `Observation.ndjson`, …). A client reads line 1, files or stores that Patient, reads line 2, and so on. That is why Bulk uses NDJSON: you can stream a million Observations without loading a million-entry Bundle into memory.

If someone emails a `.ndjson` file, you can open it in a text editor. Each line is ordinary JSON. If you see `"resourceType":"Bundle"` and an `entry` array, that is **not** Bulk output.

### What Inferno’s Bulk kit actually tests

Inferno ships **separate suites** for the two sides. You do not get both ends in one click.

| Inferno suite | Inferno plays | Your system must be |
| --- | --- | --- |
| Bulk Data Access v1.0.1 **Server** | The client | A server that accepts `$export`, polls, and serves NDJSON, judged by the **STU1** guide (IG version 1.0.1) |
| Bulk Data Access v2.0.0 **Server** | The client | Still you as the server, Inferno as the client — but judged by the **STU2** guide (IG version 2.0.0) |
| Bulk Data Access v2.0.0 **Client** | The server (reference exporter) | A client that kickoffs, polls, downloads, and reads NDJSON |

“Same, against the STU2 rules” only means: **same job, newer edition of the spec.** Inferno is still pretending to be the downloader. You are still the exporter. The checklist is the **second** published Bulk Data IG, not the first.

**STU** is Standard for Trial Use — a numbered, published HL7 guide. It is not a draft scribble, and it is not “FHIR R4 vs R5.” Bulk Data STU1 is IG **1.0.1**. Bulk Data STU2 is IG **2.0.0**. Inferno keeps both server suites because some certified products still claim the old edition (early (g)(10) work used STU1) and newer ones claim STU2. STU2 adds things STU1 did not require, such as a **POST** kickoff (not only GET), clearer delete/cancel of a job, and `_typeFilter` (export only some profiles, not only some resource types). The kickoff → 202 → poll → NDJSON files story is the same in both.

If we build Bulk now, target **STU2** (`v2.0.0 Server`). Do not run both suites and treat STU1 fails as a second product.

The **server** suite checks, among other things:

- Kickoff returns 202 and a status URL.
- Status moves from in-progress to a completion **manifest** (a JSON list of output files).
- Files are `application/fhir+ndjson`, and each line is a valid resource of the promised type.
- Optional filters (`_type`, `_since`) are honored if advertised.
- On production Inferno, **SMART Backend Services** — a machine-to-machine token using a signed JWT (JSON Web Token), not a human login. Open HTTP fails here even if `$export` works.

The **client** suite checks that **your** software can talk to **Inferno’s** exporter: request the export, follow the poll, download the files, and treat each NDJSON line as a resource.

The QA catalog also mentions preliminary **Bulk Submit** tests (ballot Bulk Data v4): a Data Provider sending a bulk package, and a Data Consumer receiving it. That is a later, different operation from `$export`. Ignore it until `$export` exists.

### Requirements before a server-suite run is honest

1. A **Group** Inferno can name (for us: SETPOP / C0X cohort published as `Group/{id}`), or a Patient/`$export` you actually support.
2. **Async job** handling. Caddy cuts public requests around 61 seconds. Kickoff must return 202 and do the work off the request thread. TaskMan is the queue we already use for quality validate/submit. Not `$JOB`.
3. **NDJSON files** on a URL the client can GET (we already serve frozen JSON from `/filesystem`).
4. Prefer **cached** patient Bundles (`cache` CID), not a live `GETBNDLA` per DFN. A thousand HARBER-class charts on the request path will not finish.
5. For a **green Inferno scorecard**: SMART Backend Services (register a client, validate its JWT, issue a token). An open-HTTP `$export` can still be a real demo. Inferno will not call it conformant.

### Requirements before a client-suite run is honest

A program that can:

1. Call someone else’s `$export` with a token.
2. Poll `Content-Location` until the manifest appears.
3. Download each NDJSON file.
4. Split on newlines and parse each line as FHIR JSON.
5. Do something useful with the resources (store, `POST /addpatient`, build a coding worklist).

That client does **not** have to be Codex. cds1, a small Node/Python worker, or a second container is enough.

### Can we run both ends, on two of our servers?

**Yes.** Inferno tests each side in its own session. You point one session at the producer and another session at the consumer. You do not put both roles on one FHIR base URL and expect one suite to score “both ends.”

**Preferred house loop: rpmsfhir produces, fhirdev imports via `/addpatient`.**

That is the right design. RPMS already has the ~1,000-patient Synthea population. fhirdev already has the intake door we use for every Synthea load. Bulk is then only a **delivery wrapper** around the import we already trust — the same story as a coding firm pulling Epic Bulk and filing it into the workbench.

fhirdev is the **import target**, not the Bulk client by itself. Something has to kick off `$export` on RPMS, download the NDJSON, rebuild **one Bundle per patient**, and `POST` those Bundles to fhirdev. That worker can live on fhirdev, next to it, or on cds1. Codex `/addpatient` does not read NDJSON.

| Role | Host | Job |
| --- | --- | --- |
| **Bulk server (producer)** | rpmsfhir (`https://rpmsfhir.vistaplex.org/fhir`) | `Group/{id}/$export` → TaskMan → NDJSON files |
| **Bulk client (worker)** | small service on or beside fhirdev (or cds1) | Kickoff RPMS, poll, split NDJSON, one Bundle per patient |
| **Import target** | fhirdev (`https://devfhir.vistaplex.org/addpatient`) | Existing intake: `load=0` graph only, then `load=1` to file |

`/addpatient` is appropriate **after** that rebuild. It wants a FHIR Bundle (the Synthea / C0FW transaction we already POST), not a `.ndjson` file and not one giant file of every Patient plus every Observation. Group the Condition / Observation / Encounter lines back under the Patient they belong to, then POST **one patient at a time**, serial, same as today’s cohort loads.

Start with `load=0` on a **small Group** (a handful of DFNs), not the whole thousand. Then `load=1` once the Bundles look right. Watch **ICN / Synthea UUID dedupe**: RPMS and fhirdev often hold the same synthetic people. A re-import should hit the existing “duplicate ICN, refuse” path, not mint a second DFN. If the point is “prove RPMS charts can land on VistA,” pick patients fhirdev does not already have, or a dedicated Group.

Inferno still does **not** score this loop as one test:

1. Inferno **Server** suite → rpmsfhir. That answers “can RPMS produce Bulk?”
2. Inferno **Client** suite → the worker (not `/addpatient`). Inferno pretends to be the exporter. `/addpatient` is our filing step after a successful download; Inferno never POSTs there.
3. House loop: worker calls rpmsfhir, then fhirdev. Dual-stack demo. No Inferno in the middle.

Is it possible **without** SMART? For the house loop, yes — these hosts already trust each other. For a green Inferno Server scorecard on RPMS, SMART Backend Services still have to exist on the producer.

What we would have to build:

| Piece | Where | Needed for |
| --- | --- | --- |
| `Group` read + `$export` kickoff / status / NDJSON | Codex on **rpmsfhir** | Inferno Server + house loop |
| TaskMan worker that writes NDJSON from cache/Group | Codex on RPMS | Same |
| NDJSON → per-patient Bundle → serial `/addpatient` | worker targeting **fhirdev** | House loop (this is the “Bulk as import”) |
| Optional Inferno-shaped client API on that worker | same worker | Inferno Client suite only |
| SMART Backend Services | Codex on RPMS | Green Inferno Server / (g)(10), not the first house demo |

What we should **not** do: POST NDJSON to `/addpatient`; dump all 1,000 RPMS patients onto fhirdev in one night; use fhirdev’s Inferno scorecard patients as the import target without a separate Group; implement system `$export` of all of File 2 to “finish Bulk”; or run Inferno Bulk against open HTTP and call the red scorecard a surprise.

The earlier pairing (fhirdev produces, cds1 only holds files) is still valid if we want Bulk without touching File 2. It is a weaker story than RPMS → VistA intake.

---

## Every kit on the page

Maturity is Inferno's label (High / Medium / Low). Fit is ours. After each kit: the names in English, what Inferno is testing, what you need before you can use it, and our call.

### Use now

#### US Quality Core — 0.2.0 (2026-09-10), maturity Low

**Names.** **US Quality Core** (USQC) is the FHIR IG for **USCDI+ Quality**: the extra data CMS and quality programs want on top of ordinary US Core (encounters, labs, documents, and so on, shaped for eCQMs). **eCQM** is an electronic clinical quality measure. Kit 0.2.0 covers the 2026 IG v0.5.0 and the v1.0.0-ballot.

**What it tests.** Inferno pretends to be a client pulling USCDI+ Quality data from **your** FHIR R4 server. It searches and reads Patient, Encounter, Observation, DocumentReference, Condition, Procedure, Organization, Practitioner, Location, and related profiles. It checks search parameters, Must Support fields, and whether the JSON validates against the USQC profiles.

**Requirements to use it.** A public FHIR base Inferno can reach (`https://devfhir.vistaplex.org/fhir`). Patient IDs that actually have the resource families under test. We already run this; the remaining work is more families and staying current when the 1.0.0-ballot suites appear on **production** Inferno.

**Our fit.** **Use now.** This is the live Inferno lane. fhirdev / rpmsfhir / altfhir already publish scorecards.

#### US Core — 1.1.6 (2026-09-03), maturity High

**Names.** **US Core** is the base US patient-access FHIR IG (versions 3.1.1 through 8.0.0). It is how a certified EHR is supposed to look when an app asks for the chart. US Quality Core **profiles** US Core; it does not replace it. The kit also touches **SMART App Launch** because many US Core searches assume a token.

**What it tests.** Same idea as USQC: Inferno is the client. It retrieves US Core profiles (Patient, AllergyIntolerance, vitals, labs, …) and checks Must Support, search combinations, and reference resolution. SMART-only groups check login and scopes, not Observation shape.

**Requirements to use it.** Same public `/fhir` and representative patients. Skip SMART groups until we have OAuth. Pick one IG version (6.1.0 or 7.0.0 matches how we talk about USQC) and stay there.

**Our fit.** **Use now**, selected suites only. Cheap second scorecard on the same patients.

### Later if funded

#### CARIN Blue Button — 0.16.3 (2026-09-03), maturity Medium

**Names.** **CARIN** is the Coalition for Affordable and Reliable Information Now, an HL7 accelerator. **Blue Button** here means the CARIN IG for Blue Button: how a **payer** shows a member their claims and explanation-of-benefit data as FHIR (`ExplanationOfBenefit`, `Coverage`, related Patient demographics). Versions on the kit: v1.1.0 (server only), v2.0.0 (server and client), plus a non-financial proposal.

**What it tests.** Does the server (or client) expose claims the way CARIN says — profiles, search, required identifiers — not “is there a Claim in the browser.”

**Requirements to use it.** At least one **profiled** FHIR Claim / EOB that matches CARIN, on a FHIR endpoint Inferno can read. A screenshot of a Claim is not enough. For client tests, software that can fetch those resources from a CARIN server.

**Our fit.** **Later.** First Inferno kit that tests the object the coding talk already shows. Run it when a synthetic Claim is profiled.

#### Da Vinci PAS — 0.15.2 (2026-09-08), maturity Low

**Names.** **Da Vinci** is the HL7 accelerator for payer–provider use cases. **PAS** is Prior Authorization Support: submit a prior-auth as a FHIR **Claim**, get a **ClaimResponse**, instead of a portal and a fax. Kit covers PAS v2.0.1 and v2.2.1. Client and server.

**What it tests.** Can a provider system submit a PAS Claim, and can a payer system answer, with the right profiles and operations.

**Requirements to use it.** A **Claim** we can POST, and a partner or Inferno reference that will answer. We should be the **provider client**, not a VistA payer server. SMART or some token appears once you leave the reference sandbox.

**Our fit.** **Later.** Connectathon Burden Reduction analogue. After a Claim exists.

#### Da Vinci CRD — 0.14.2 (2026-09-08), maturity Low

**Names.** **CRD** is Coverage Requirements Discovery. At order time, the EHR asks the payer: “does this need prior auth or extra documentation?” The answer comes back as **CDS Hooks** (Clinical Decision Support Hooks — a JSON “card” in the workflow). Kit covers CRD STU 2.0.1 and 2.2.1.

**What it tests.** Client and server conformance to those CRD versions: hook request shape, coverage cards, and related US Core context.

**Requirements to use it.** A CDS Hooks endpoint (cds1 is the start) and an EHR or test harness that can fire `order-sign` / `order-select`. Not a DEQM MeasureReport problem.

**Our fit.** **Later.** Maps to `cds-hooks-on-fhir` plus a future Coding Consult.

#### Da Vinci DTR — 0.18.0 (2026-09-08), maturity Low

**Names.** **DTR** is Documentation Templates and Rules. After CRD says “we need more,” DTR walks the clinician through a **Questionnaire** (often driven by **CQL**, Clinical Quality Language — the same language as our eCQMs) and returns structured answers the payer asked for. Kit covers DTR v2.0.1 and v2.2.0.

**What it tests.** Can the provider side launch the questionnaire, run the rules, and return a completed QuestionnaireResponse; can the payer side serve the template.

**Requirements to use it.** Questionnaire render + CQL (we have CQL on the quality path) and a human-accept step. Same “AI or rules propose, person accepts” pattern as Quality AI Consult.

**Our fit.** **Later.** Provider client first.

#### ONC (g)(33) PAS API — 0.0.0 draft (2026-09-09), maturity Low

**Names.** **(g)(33)** is certification criterion **§ 170.315(g)(33)** — Prior Authorization Support API in the ONC Health IT Certification Program. It is PAS plus SMART, written as a **certification exam**, not a Connectathon track. Inferno marks this **DRAFT, not for certification**.

**What it tests.** Whether a Health IT module can submit prior auth the way the draft test procedure says.

**Requirements to use it.** PAS + SMART App Launch, as an EHR API. WorldVistA does not have this. A coding firm product would more often be the client.

**Our fit.** **Later** as a funding map. Do not claim a score.

#### ONC (g)(31) CRD API — 0.9.0 draft (2026-09-08), maturity Low

**Names.** **(g)(31)** is **§ 170.315(g)(31)** — Coverage Requirements Discovery API. CRD as a certification exam. Also **DRAFT**.

**What it tests.** Certified CRD behavior plus US Core context.

**Requirements to use it.** SMART + a CRD server on the EHR. We do not have that.

**Our fit.** **Later** as a map, same as (g)(33).

#### Da Vinci PDex — 0.13.2 (2026-09-03), maturity Low

**Names.** **PDex** is Payer Data Exchange. CMS-facing APIs so a member, a provider, or another payer can get the payer’s clinical and claims data. Kit is PDex v2.0.0.

**What it tests.** PDex client and server profiles and operations (member access, provider access, payer-to-payer). Often needs Bulk and SMART on the payer side.

**Requirements to use it.** A payer-shaped FHIR server, or a client that consumes one. Not a VistA chart API.

**Our fit.** **Later**, only if a coding firm must pull payer data.

#### ONC (g)(10) Standardized API — 8.0.7 (2026-09-08), maturity High

**Names.** **(g)(10)** is **§ 170.315(g)(10)** — Standardized API for Patient and Population Services. This is the **approved** ONC certification kit. It is three kits in one: **SMART App Launch**, **US Core**, and **Bulk Data**.

**What it tests.** Can a patient-facing app log in (SMART), read the USCDI chart (US Core), and can an authorized system pull a population (Bulk `$export`).

**Requirements to use it.** All three pieces, working, with tokens. Codex has US Core-shaped **reads**. It does not have SMART or `$export`. Running the full kit today fails at the front door.

**Our fit.** **Later.** Do not open until SMART and Bulk exist.

#### SMART App Launch — 1.0.3 (2026-08-26), maturity Medium

**Names.** **SMART App Launch** is the OAuth 2 / OpenID Connect IG so an app can launch from an EHR (or stand-alone) and get scoped access. STU1, STU2, STU2.2. The kit also tests **User-access Brands and Endpoints** (how a publisher lists “here is my patient portal / API”).

**What it tests.** Authorization server and clients: authorize, token, PKCE, refresh, scopes. Not clinical resource shape.

**Requirements to use it.** An OAuth authorization server in front of `/fhir`, registered clients, launch URLs. Required for Epic-in-EHR launch and for (g)(10).

**Our fit.** **Later.** Coding 90-day pilot is export-only.

#### Bulk Data — 0.13.1 (2026-06-01), maturity Low

**Names.** **Bulk Data Access** (sometimes “Flat FHIR”). Population export via `$export` and **NDJSON** files. See [Bulk Data, NDJSON, and running both ends](#bulk-data-ndjson-and-running-both-ends) above.

**What it tests.** Server suites: kickoff, poll, NDJSON, usually SMART Backend Services. Client suite: your software as the downloader against Inferno’s exporter. Flavors: all patients, Group, system. Preliminary Bulk Submit (v4 ballot) is extra.

**Requirements to use it.** For produce: Group + async job + NDJSON files; SMART for a green scorecard. For consume: a client that polls and reads NDJSON. Two of our servers can play the two roles; Inferno still scores them as two sessions.

**Our fit.** **Later.** First useful produce: Group `$export` on **rpmsfhir**. First useful consume: rebuild per-patient Bundles and serial `POST /addpatient` on **fhirdev**.

#### UDAP Security — 0.12.2 (2026-05-26), maturity Low

**Names.** **UDAP** is Unified Data Access Profiles (HL7 Security for Scalable Registration, Authentication and Authorization, STU 1.0). B2B (business-to-business) registration and tokens so a payer and a provider can trust each other without a human clicking “Allow.”

**What it tests.** Client and server conformance to that UDAP IG (registration, signed metadata, JWT client auth).

**Requirements to use it.** A registration/token path. Only after SMART or another B2B token exists. Needed later for PAS/PDex between organizations.

**Our fit.** **Later.**

### Skip

#### Service Base URL — 0.13.0 (2025-07-22), maturity Medium

**Names.** **Service Base URL** is ONC’s required public list of FHIR endpoint URLs (Conditions and Maintenance of Certification / HTI-1). **HTI** is Health Data, Technology, and Interoperability — the ONC rule series.

**What it tests.** Is your published endpoint list in the mandated format.

**Requirements.** A certified URL list we intend to publish. We do not.

**Our fit.** **Skip** unless VistaPlex publishes that list.

#### International Patient Access — 0.7.2 (2026-05-18), maturity Medium

**Names.** **IPA** is International Patient Access: a world-wide, thinner cousin of US Core so a patient app can read a chart in FHIR R4.

**What it tests.** Inferno simulates an IPA requestor and checks the IPA IG.

**Requirements.** An IPA-conformant patient API. US Core / USQC already cover this job for us.

**Our fit.** **Skip.**

#### Da Vinci Plan Net — 0.13.4 (2026-06-01), maturity Low

**Names.** **Plan Net** is the PDex **Plan Network** directory: which practitioners and organizations are in a payer’s network (PDEX Plan Net IG v1.1.0).

**What it tests.** Directory resources and searches, not a chart or a Claim we create.

**Our fit.** **Skip.** Payer directory, not our workbench.

#### Da Vinci US Drug Formulary — 0.13.3 (2026-06-01), maturity Low

**Names.** **Formulary** is the payer’s covered-drug list (PDex US Drug Formulary IG v2.0.1).

**What it tests.** Formulary profiles on a server.

**Our fit.** **Skip.**

#### Subscriptions — 0.12.2 (2026-05-27), maturity Low

**Names.** **Subscriptions** are FHIR’s “notify me when this changes” framework (R5, or the R4 **Backport** IG).

**What it tests.** Subscribe, handshake, notifications.

**Requirements.** A Subscription implementation. Codex is request/response R4.

**Our fit.** **Skip.**

#### UDS+ — 1.3.0 (2025-07-22), maturity Low

**Names.** **UDS+** is Uniform Data System Plus — HRSA’s FHIR reporting for community health centers (IG v2.0.0). Inferno plays a crude **data receiver**: you hand it an Import Manifest; it checks the manifest and the files it points at.

**What it tests.** Manifest shape and the data behind it, not USQC search.

**Our fit.** **Skip** for now. Interesting later for IHS/FQHC, not DEQM or coding.

#### Central Cancer Registry Reporting — 0.10.2 (2026-06-01), maturity Low

**Names.** **CCRR** is the HL7 FHIR Central Cancer Registry Reporting IG (STU 1.0.0): sending cancer case data to a registry.

**What it tests.** Those cancer-report Bundles and profiles.

**Our fit.** **Skip.** Separate program.

#### Cancer Pathology Data Sharing — 0.10.2 (2026-06-01), maturity Low

**Names.** **CPDS** is Cancer Pathology Data Sharing (STU 1.0.0): pathology reports as FHIR for cancer programs.

**What it tests.** Those pathology Bundles.

**Our fit.** **Skip.**

#### SMART-UDAP Harmonization — 0.12.0 (2025-07-22), maturity Low

**Names.** Experimental kit for servers that try to satisfy **both** SMART App Launch and **UDAP** at once.

**What it tests.** Combined authorization options. Not a clinical IG.

**Our fit.** **Skip.**

#### SMART Scheduling Links — 0.4.0 (2025-07-22), maturity Medium

**Names.** **SMART Scheduling Links** is a draft IG: publish a bulk **manifest** of slots/schedules so a consumer can find open appointments.

**What it tests.** Fetch the manifest, fetch the files, validate the resources.

**Our fit.** **Skip.** No scheduling-links product.

#### SMART Health Cards — 0.11.0 (2025-07-22), maturity Low

**Names.** **SMART Health Cards** are signed, portable vaccination/lab cards (a QR / download, not an EHR API). Framework v1.4.0.

**What it tests.** Inferno downloads and validates a card.

**Our fit.** **Skip.**

#### SMART Health Cards: Vaccination and Testing — 0.5.0 (2025-07-22), maturity Low

**Names.** The vaccination-and-testing **profile** on Health Cards (IG v0.5.0-rc).

**What it tests.** Same as above, for that profile.

**Our fit.** **Skip.**

#### International Patient Summary — 0.12.0 (2025-07-22), maturity Low

**Names.** **IPS** is International Patient Summary: a cross-border clinical summary (IG v1.1.0), different from IPA (which is an API style).

**What it tests.** Inferno acts as an IPS requestor and checks the summary Bundle.

**Our fit.** **Skip.**

#### At-Home In-Vitro — 0.13.0 (2025-07-22), maturity Medium

**Names.** **AHI / At-Home In-Vitro** is the IG for home test results (COVID-style kits) as FHIR Bundles (v1.0.0).

**What it tests.** Those Bundles and entry resources.

**Our fit.** **Skip.**

## Not on this page — still our test loop

Inferno QA does not list these. We already have (or will copy) another tool.

| Gap | Names in English | What we use instead |
| --- | --- | --- |
| **DEQM** MeasureReport | **DEQM** is Data Exchange for Quality Measures. The FHIR report that replaces QRDA (Quality Reporting Document Architecture) Category I / III. | HL7 validator + DEQM reference receiver (`cds1` / `fhir:3000/4_0_1`). Packets in `docs/deqm-summary/`. |
| **CDex** attachments | **CDex** is Clinical Data Exchange: sending chart attachments with a claim or a prior auth. | HL7 validator + Connectathon receiver when one exists. |
| **Risk Adjustment (HCC)** | **HCC** is Hierarchical Condition Category — the diagnosis groups Medicare Advantage uses for risk scores. | No Inferno kit. Validator + payer sandbox later. |
| **PCT / AEOB** | **PCT** is Patient Cost Transparency. **AEOB** is Advanced Explanation of Benefits: a good-faith estimate, then the payer’s answer. | Same: validator / sandbox, no Inferno kit on this page. |

Quality already treats Inferno as “is the chart USQC-shaped?” and the DEQM receiver as “will a program accept the report?” Coding should copy that split: CARIN/PAS Inferno for the Claim object, validator/receiver for attachments and AEOB.

## Revisit

- Re-read the QA catalog when USQC 1.0.0-ballot suites show up on **production** Inferno.
- Re-open (g)(31)/(g)(33) only after a SMART path exists, or when MITRE marks them ready for certification.
- Re-open Bulk when rpmsfhir can Group-`$export` and a worker can turn that NDJSON into fhirdev `/addpatient` Bundles. Inferno Server points at RPMS; Inferno Client points at the worker, not at `/addpatient`.
- Do not cite Inferno QA session URLs in Connectathon packets or funding text.
