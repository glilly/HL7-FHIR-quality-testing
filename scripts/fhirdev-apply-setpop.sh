#!/usr/bin/env bash
# Apply 2026/cohorts/SETPOP_MANIFEST.tsv onto fhirdev22 (^C0FQUAL POP + SEED).
# Requires: SSH to root@devfhir.vistaplex.org, container fhirdev22, Codex C0FQUAL already synced.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MAN="${1:-$ROOT/2026/cohorts/SETPOP_MANIFEST.tsv}"
FHIRDEV_SSH="${FHIRDEV_SSH:-root@devfhir.vistaplex.org}"
FHIRDEV_CONTAINER="${FHIRDEV_CONTAINER:-fhirdev22}"
VEHU_ENV="${VEHU_ENV:-/home/vehu/etc/env}"
HTTP_BASE="${FHIRDEV_HTTP_BASE:-https://devfhir.vistaplex.org}"

[[ -f "$MAN" ]] || { echo "missing manifest: $MAN" >&2; exit 1; }

TMP="$(mktemp)"
python3 - "$MAN" >"$TMP" <<'PY'
import sys
from pathlib import Path
lines = Path(sys.argv[1]).read_text().splitlines()[1:]
print('S U="^"')
print('ZL "C0FQUAL"')
print('D SEED^C0FQUAL')
for line in lines:
    if not line.strip():
        continue
    cms, dfn, ipp, denom, numer, denex, evid, mode = line.split("\t")
    evid = evid.replace('"', '""')
    mode = mode.replace('"', '""')
    print(f'DO SETPOP^C0FQUAL("{cms}",{dfn},{ipp},{denom},{numer},{denex},"{evid}","{mode}")')
print('S N=0,D="" F  S D=$O(^C0FQUAL("POP","CMS165v14",D)) Q:D=""  S N=N+1')
print('W "VER=",$G(^C0FQUAL(0))," POP165=",N,!')
print('H')
PY

ssh -o BatchMode=yes "$FHIRDEV_SSH" \
  "docker exec -i -u vehu '$FHIRDEV_CONTAINER' bash -lc 'source $VEHU_ENV >/dev/null 2>&1; cd /home/vehu/p; mumps -dir'" \
  <"$TMP"
rm -f "$TMP"

echo "==> Smoke: $HTTP_BASE/fhir-quality-dashboards"
curl -sS -o /dev/null -w "HTTP %{http_code}\n" "$HTTP_BASE/fhir-quality-dashboards"
echo "Done."
