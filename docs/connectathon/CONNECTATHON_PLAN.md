# HL7 FHIR Connectathon — Attendance Analysis and Prep Plan

Status date: 2026-06-13

This document captures the analysis of HL7 FHIR Connectathon options for the
VistA-on-FHIR program, the fit assessment for the event we are registered
for, and a concrete preparation plan. It covers the two requests:

1. Which July tracks fit testing our read-bundle conformance, and
2. A prep plan: what to have running so we can actually test rather than
   observe.

## Event landscape (as of 2026-06-13)

HL7 runs three main international FHIR Connectathons per year (typically the
weekend before a Working Group Meeting), plus specialized events such as the
US Realm and CMS connectathons.

| Event | Dates | Format | Status for us |
|---|---|---|---|
| US Realm Connectathon | Mar 31 – Apr 2, 2026 | Virtual | Past |
| Connectathon 42 (Rotterdam) | May 16–17, 2026 | In-person + virtual | Past |
| **CMS HL7 FHIR Connectathon 7** | **Jul 14–16, 2026** | **Virtual, free** | **Registered** |
| Connectathon 43 (40th Annual Plenary + WGM) | Sep 19–25, 2026 (Connectathon weekend at the start) | In-person (Bethesda North Marriott, Rockville, MD) + virtual | Recommended target for our stack |

Sources: HL7 Confluence Connectathon pages and the CMS event page
(`confluence.hl7.org`, page 453905739) and HL7 International events listing.

## Fit assessment — CMS Connectathon 7 (July)

The CMS event is **payer- and CMS-policy oriented**: prior authorization
(Da Vinci CRD/DTR/PAS), Patient Access / payer-to-payer (PDex), cost
transparency (PCT), provider directories (NDH), and quality reporting
(DEQM). None of this maps directly onto our provider-native VistA writeback,
CPRS-succession, or ordering work.

That said, three tracks are genuinely useful to us, in priority order, and
the event is a low-cost way to exercise our **read output's conformance**
and learn the connectathon tooling and rhythm before the September event
where we would put VistA-native writeback/ordering in front of the spec
authors.

### Recommended primary: US Quality Core (USCDI+ Quality on FHIR)

- **Why:** This track ships an **Inferno Test Kit** for clients and servers.
  Inferno is the standard ONC FHIR conformance harness; running our `/fhir`
  server against it is exactly the conformance measurement our funding
  proposal commits to under **Aim 2 (make correctness mechanical and
  publishable)**. It directly tests whether our VistA-generated resources
  are US Core / USCDI conformant.
- **What we test:** server conformance of the bundles we already emit
  (Patient, Encounter, Condition, Observation, DocumentReference, etc.).
- **Payoff:** a concrete, third-party-tool conformance score we do not have
  today, plus early signal on which domains need profile work.

### Recommended secondary: PIQI (Patient Information Quality Improvement)

- **Why:** Format-agnostic **data-quality scoring** against real FHIR data
  exchanges. Complements Inferno: Inferno asks "is it conformant?"; PIQI
  asks "is it good/usable data?" Our VistA reads are a strong real-world
  specimen.
- **Payoff:** an external read on data-quality gaps in our read output that
  feeds the same Aim 2 work and the CPRS-on-FHIR spec evidence base.

### Optional scouting: SMART Scheduling Links

- **Why:** Touches our deferred **SCH** domain (CPRS-on-FHIR `CFH-SCH-*`).
  Low cost to observe and scope what a future scheduling surface needs.
- **Payoff:** reconnaissance only; no implementation expected in July.

### Tracks to skip for our purposes

Da Vinci Burden Reduction (CRD/DTR/PAS), PDex / PDex Plan-Net, PCT, NDH,
DEQM, EOM, IPF-PAI, PACIO, ACCESS API, CARIN RTPBC, Cancer Clinical Trial
Matching, Physical Activity, CMS Aligned Networks IAS. These are payer- or
program-specific and outside our provider-native scope. Worth a glance at
Thursday Track Highlights, not active testing.

## July key dates

| Date | Item |
|---|---|
| Jun 16–26, 2026 | Track Kick-Off Calls (per-track; registered participants invited) |
| Jun 30, 2026 | Registration closes (we are already registered) |
| Jun 30, 2026, 12:00 PM ET | Participant Information Session (for anyone bringing a system to test) |
| Jul 14–16, 2026 | Connectathon (virtual); Track Highlights on Thursday |

Action: once the US Quality Core and PIQI track pages publish their
Kick-Off Call details, attend both calls — that is where the test scenario
and the required testing environment are explained.

## Prep plan — bring a testable system, not just attendance

Goal: arrive with a disposable VistA FHIR endpoint serving synthetic
patients that we can point Inferno (US Quality Core) and PIQI at, plus our
own conformance baseline already captured so connectathon time is spent on
findings, not setup.

### What we already have to build on

- `VistA-FHIR-Server-Codex/scripts/synthea-one-patient.sh` — generate one
  Synthea FHIR R4 bundle (Docker + JDK).
- `VistA-FHIR-Server-Codex/scripts/vehu10-fhir-sync.sh` and
  `local-fhir-container-sync.sh` — sync routines into a container and smoke
  the `/fhir` listener (vehu10 on host `9085`).
- `VistA-FHIR-Server-Codex/scripts/local-vehu-to-fhir-intake.sh` /
  `fhirdev-addpatient.sh` — load a patient via `/addpatient`.
- `CPRS-on-FHIR/harness/lib/cfh-smoke.sh` — read-only live smoke helper,
  gated by `CFH_ENDPOINT`, `CFH_ALLOW_LIVE_READ=1`,
  `CFH_I_ACK_TRAINING_SYSTEM=1`; already probes `/metadata` and resource
  paths.

### Step 1 — Stand up a disposable endpoint with synthetic patients (by Jul 7)

1. Bring up the test container (vehu10) and restart the M web listener
   (`stop^%webreq` / `go^%webreq`) per the container developer guide.
2. Generate a small synthetic cohort and load it:
   - `scripts/synthea-one-patient.sh -o /tmp/syn-cohort` (repeat or seed a
     handful of patients across ages/conditions for coverage).
   - Load each via the `/addpatient` intake path.
3. Confirm reads: `curl -sfS http://127.0.0.1:9085/fhir/metadata` returns a
   CapabilityStatement, and a patient `$everything`/bundle read returns the
   expected multi-domain resources.

Success criterion: `/metadata` plus at least one full patient bundle return
200 with the resource types US Quality Core / US Core care about
(Patient, Encounter, Condition, Observation incl. vitals + labs,
MedicationRequest, AllergyIntolerance, DocumentReference, Immunization).

### Step 2 — Capture our own conformance baseline (by Jul 9)

1. Run the existing CPRS-on-FHIR read-only smokes against the endpoint:
   ```bash
   export CFH_ENDPOINT=http://127.0.0.1:9085/fhir
   export CFH_ALLOW_LIVE_READ=1
   export CFH_I_ACK_TRAINING_SYSTEM=1
   # run the seven live-read-capable harnesses
   ```
2. Run the resources through a standard validator (the FHIR R4 / US Core
   validator) and record failures by resource type. This is the pre-event
   baseline; it makes connectathon Inferno runs a comparison, not a
   discovery.

Success criterion: a short written baseline — per-resource-type
pass/fail against US Core — committed alongside this plan or in
CPRS-on-FHIR. This is also the first concrete artifact for funding-proposal
Aim 2.

### Step 3 — Get the endpoint reachable for the track tooling (by Jul 13)

Inferno and PIQI tooling may run hosted (pointed at our server) or locally
(we point at their fixtures). Decide per the Kick-Off Calls:

- If the tooling must reach our server, expose the disposable endpoint
  (e.g. the remote `devfhir` deploy via `fhirdev-codex-sync.sh`, or a
  tunnel to the local container) — **synthetic data only; no PHI ever**.
- If we run the tooling locally (preferred when possible), install the
  Inferno US Quality Core Test Kit ahead of time and dry-run it against the
  local endpoint.

Success criterion: a green Inferno "smoke" run against our endpoint before
Day 1, even if many tests fail — connection and auth working is the gate.

### Step 4 — During the event (Jul 14–16)

- Join US Quality Core: run the Inferno suite against our endpoint; log
  every failure with the resource/profile and likely VistA-side cause.
- Join PIQI: submit representative read bundles; capture the quality score
  and the specific deductions.
- Scout SMART Scheduling Links for the SCH domain.
- Thursday: watch Track Highlights for US Quality Core and PIQI.

### Step 5 — After the event

- Write a short trip report: conformance gaps found, data-quality
  deductions, and how they reprioritize C0FW domain work and the
  CPRS-on-FHIR profile package.
- Fold the findings into the Aim 2 conformance backlog and decide the
  September (Connectathon 43) plan: participate on a write/order track or
  propose a VistA-native writeback track.

## Why this is worth the time despite the payer focus

- It converts "we should measure conformance" (a funding-proposal promise)
  into an actual Inferno score and PIQI assessment, at zero event cost.
- It rehearses the connectathon tooling, environment exposure, and rhythm
  before the higher-stakes September event in the VA's backyard.
- Every artifact produced (baseline, trip report) is reusable evidence for
  the funding proposal and the CPRS-on-FHIR spec work.

## September (Connectathon 43) — the real target for our stack

Bethesda North Marriott, Rockville, MD, Sep 19–25, 2026 (Connectathon
weekend at the start). In-person attendance is recommended: it is the
largest US event, it is in the VA/DC corridor relevant to the HMP-veteran
staffing thesis, and prior years ran tracks directly aligned with our work
(e.g. Clinical Order Workflows, US Core / testing). Decision to make by
late July: join an existing write/order track as a participant, or submit a
track proposal (proposals open ~12 to ~6 weeks before the event, reviewed
by the FHIR Management Group) putting VistA-native FHIR writeback in front
of the spec authors.
