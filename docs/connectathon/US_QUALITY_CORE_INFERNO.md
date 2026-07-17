# US Quality Core Inferno Test Kit

This workspace uses the MITRE Inferno **US Quality Core Test Kit** to run draft
US Quality Core v0.5.0 checks against VistA/RPMS FHIR endpoints.

Source:

- `https://github.com/inferno-framework/us-quality-core-test-kit.git`

The test kit validates the 2026 US Quality Core Implementation Guide v0.5.0. Its
server suite simulates a client retrieving USCDI+ Quality V1 data from a FHIR R4
server. It is useful for finding conformance gaps, but it is not a quick
all-green smoke test for the current VistA/RPMS stack; the selected patients
must expose representative resources for the profile groups being tested.

## Local Clone

The helper scripts expect the Inferno kit as a sibling checkout:

```bash
~/work/vista-stack/us-quality-core-test-kit
```

Create or update that checkout from this repo:

```bash
./scripts/usqc-clone-or-update.sh
```

Override the location when needed:

```bash
KIT_DIR=/path/to/us-quality-core-test-kit ./scripts/usqc-clone-or-update.sh
```

## Start Inferno

The upstream kit supports `./setup.sh` and `./run.sh`, but those bind the web UI
to host port `80`. The wrappers here generate a Docker Compose override and use
`localhost:8088` by default.

```bash
./scripts/usqc-setup.sh
./scripts/usqc-start.sh
```

Open:

```text
http://localhost:8088
```

Stop it with:

```bash
./scripts/usqc-stop.sh
```

Useful port overrides:

```bash
INFERNO_HTTP_PORT=8090 REFERENCE_SERVER_PORT=8091 ./scripts/usqc-setup.sh
INFERNO_HTTP_PORT=8090 ./scripts/usqc-start.sh
```

The local Inferno reference server is available at:

```text
http://localhost:8089/reference-server/r4
```

## Run Against VistA/RPMS

First make sure the FHIR endpoint and Patient IDs are reachable:

```bash
./scripts/usqc-smoke-fhir.sh http://localhost:5177/fhir 14
./scripts/usqc-smoke-fhir.sh https://rpmsfhir.vistaplex.org/fhir 14
```

For an authenticated endpoint:

```bash
ACCESS_TOKEN=... ./scripts/usqc-smoke-fhir.sh https://example.test/fhir 14,21
```

Then write an Inferno preset into the cloned test kit.

When Inferno runs in Docker, do not use `localhost:5177` as the FHIR endpoint
inside the Inferno session. From inside the Inferno container, `localhost` means
the Inferno container itself. Use `host.docker.internal` for a local gateway
running on the WSL/host side:

```bash
./scripts/usqc-write-preset.sh http://host.docker.internal:5177/fhir 14
```

For the public RPMS demo:

```bash
TITLE="RPMSFHIR Public" ./scripts/usqc-write-preset.sh https://rpmsfhir.vistaplex.org/fhir 14
```

The preset is written to:

```text
../us-quality-core-test-kit/config/presets/vista_on_fhir_preset.json
```

Restart Inferno after changing presets if the UI does not pick up the new file.

In Inferno:

1. Start a new **US Quality Core Server v0.5.0** session.
2. Select the generated preset, usually **Vista/RPMS FHIR Server**.
3. Confirm:
   - **FHIR Endpoint** is the VistA/RPMS FHIR base URL.
   - **Patient IDs** is a comma-separated list of FHIR Patient resource IDs.
4. Run **US Quality Core FHIR API**, or start with narrower groups such as
   Patient, Encounter, Condition, Immunization, Observation, or vital-sign
   groups.
5. Treat failures as a conformance gap list, not as a binary go/no-go result.

## What The Server Suite Requires

The server suite ID is:

```text
us_quality_core_v050
```

Its main inputs are:

- `url`: FHIR endpoint base URL.
- `patient_ids`: comma-separated Patient resource IDs.
- `smart_auth_info`: optional OAuth/access-token configuration.

The tests check required FHIR REST interactions for the US Quality Core server
CapabilityStatement, including searches, reads, reference resolution, Provenance
`_revinclude` behavior where applicable, and profile validation through the HL7
FHIR Validator service.

## Interpreting Results For Current VistA/RPMS Work

Expect the first runs to produce failures. Common reasons:

- The endpoint exposes useful FHIR resources but does not yet claim or satisfy
  US Quality Core profiles.
- The selected synthetic patient does not contain enough data for every profile
  group.
- Some profile groups require search combinations or `_revinclude` behavior not
  implemented by the current server.
- Terminology/profile validation can fail even when basic readback looks good.

Use early runs to prioritize server features:

- CapabilityStatement declarations and profile URLs.
- Patient-scoped search coverage.
- Read support for resources discovered by search.
- Vital-sign Observation mapping.
- Condition, Encounter, Immunization, Procedure, DiagnosticReport, DocumentReference,
  Practitioner, Organization, Location, and Provenance coverage.

## Test Kit Notes

The cloned kit is Docker-first. Host Ruby is not required for normal use. The
gem itself requires Ruby `>= 3.3.6`, and Docker Compose starts:

- Inferno web app.
- Sidekiq worker.
- HL7 FHIR Validator service.
- FHIRPath service.
- Redis.
- Inferno Reference Server.
- PostgreSQL for the reference server.

The upstream README and wiki are the source of truth for advanced usage.
