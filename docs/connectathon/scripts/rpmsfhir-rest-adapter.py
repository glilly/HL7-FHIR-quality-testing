#!/usr/bin/env python3
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, quote, urlencode, urlparse
from urllib.request import Request, urlopen

BACKEND = os.environ.get("BACKEND", "https://rpmsfhir.vistaplex.org").rstrip("/")
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "5177"))
RESOURCE_CACHE = {}
REFERENCE_PATIENT = {}


def read_json(url):
    req = Request(url, headers={"Accept": "application/fhir+json, application/json"})
    with urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def backend_json(path, query=""):
    url = "{}{}".format(BACKEND, path)
    if query:
        url = "{}?{}".format(url, query)
    body = read_json(url)
    remember_resources(body)
    return body


def remember_resources(body):
    if not isinstance(body, dict):
        return
    if body.get("resourceType") == "Bundle":
        for entry in body.get("entry", []):
            remember_resources(entry.get("resource"))
        return
    resource_type = body.get("resourceType")
    resource_id = body.get("id")
    if resource_type and resource_id:
        RESOURCE_CACHE[(resource_type, str(resource_id))] = body
    patient = patient_from_reference(
        body.get("subject", {}).get("reference", "")
    ) or patient_from_reference(body.get("patient", {}).get("reference", ""))
    if patient:
        remember_reference(resource_type, resource_id, patient)
        if resource_type == "DiagnosticReport":
            for result in body.get("result", []):
                remember_ref_string(result.get("reference", ""), patient)
            for performer in body.get("performer", []):
                remember_ref_string(performer.get("reference", ""), patient)
        if resource_type == "Condition":
            remember_ref_string(body.get("encounter", {}).get("reference", ""), patient)
        if resource_type == "Encounter":
            remember_ref_string(body.get("serviceProvider", {}).get("reference", ""), patient)
            for loc in body.get("location", []) or []:
                remember_ref_string((loc.get("location") or {}).get("reference", ""), patient)
            for part in body.get("participant", []) or []:
                remember_ref_string((part.get("individual") or {}).get("reference", ""), patient)


def remember_ref_string(reference, patient):
    parts = (reference or "").split("/")
    if len(parts) >= 2:
        remember_reference(parts[-2], parts[-1], patient)


def remember_reference(resource_type, resource_id, patient):
    if resource_type and resource_id and patient:
        REFERENCE_PATIENT[(str(resource_type), str(resource_id))] = str(patient)


def patient_from_reference(reference):
    marker = "Patient/"
    if marker not in (reference or ""):
        return ""
    return reference.split(marker, 1)[1].split("/", 1)[0]


def cached_or_bundle_resource(resource_type, resource_id):
    key = (resource_type, str(resource_id))
    cached = RESOURCE_CACHE.get(key)
    if cached:
        return cached
    patient = REFERENCE_PATIENT.get(key)
    if patient:
        remember_resources(patient_bundle(patient, refresh=True))
        return RESOURCE_CACHE.get(key)
    return None


def patient_bundle(dfn, refresh=False):
    url = "{}/fhir?dfn={}&format=json".format(BACKEND, quote(str(dfn)))
    if refresh:
        url = "{}&refresh=1".format(url)
    return read_json(url)


def bundle_resources(bundle, resource_type):
    return [
        entry.get("resource")
        for entry in bundle.get("entry", [])
        if entry.get("resource", {}).get("resourceType") == resource_type
    ]


def outcome(severity, diagnostic):
    return {
        "resourceType": "OperationOutcome",
        "issue": [
            {"severity": severity, "code": "processing", "diagnostics": diagnostic}
        ],
    }


def searchset(resources):
    return {
        "resourceType": "Bundle",
        "type": "searchset",
        "total": len(resources),
        "entry": [
            {"resource": resource, "search": {"mode": "match"}} for resource in resources
        ],
    }


def capability():
    return {
        "resourceType": "CapabilityStatement",
        "status": "active",
        "kind": "instance",
        "fhirVersion": "4.0.1",
        "format": ["json"],
        "rest": [
            {
                "mode": "server",
                "resource": [
                    {
                        "type": "Patient",
                        "interaction": [{"code": "read"}, {"code": "search-type"}],
                        "searchParam": [{"name": "_id", "type": "token"}],
                    }
                ],
            }
        ],
    }


def patient_search_response(params):
    dfn = (params.get("_id") or params.get("id") or [""])[0].strip()
    if not dfn.isdigit():
        return 400, outcome("error", "Only Patient search by _id is supported")
    bundle = patient_bundle(dfn)
    patients = [
        patient
        for patient in bundle_resources(bundle, "Patient")
        if str(patient.get("id")) == str(dfn)
    ]
    return 200, searchset(patients)


def encoded_params(params):
    return urlencode(params, doseq=True)


class Handler(BaseHTTPRequestHandler):
    def send_fhir(self, status, body, include_body=True):
        payload = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/fhir+json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        if include_body:
            self.wfile.write(payload)

    def do_HEAD(self):
        parsed = urlparse(self.path)
        if parsed.path == "/fhir/metadata":
            self.send_fhir(200, capability(), include_body=False)
            return
        self.send_fhir(404, outcome("error", "Not found"), include_body=False)

    def do_POST(self):
        parsed = urlparse(self.path)
        try:
            length = int(self.headers.get("Content-Length") or "0")
            body = self.rfile.read(length).decode("utf-8") if length else ""
            if parsed.path == "/fhir/Patient/_search":
                status, response = patient_search_response(parse_qs(body))
                self.send_fhir(status, response)
                return
            if parsed.path.startswith("/fhir/") and parsed.path.endswith("/_search"):
                params = parse_qs(parsed.query)
                params.update(parse_qs(body))
                resource = parsed.path.split("/")[2]
                self.send_fhir(200, backend_json("/fhir/{}".format(resource), encoded_params(params)))
                return
            self.send_fhir(404, outcome("error", "Not found"))
        except Exception as exc:
            self.send_fhir(502, outcome("error", "Adapter error: {}".format(exc)))

    def do_GET(self):
        parsed = urlparse(self.path)
        try:
            if parsed.path == "/fhir/metadata":
                self.send_fhir(200, capability())
                return
            if parsed.path.startswith("/fhir/Patient/"):
                dfn = parsed.path.rsplit("/", 1)[1]
                bundle = patient_bundle(dfn)
                patients = [
                    patient
                    for patient in bundle_resources(bundle, "Patient")
                    if str(patient.get("id")) == str(dfn)
                ]
                if not patients:
                    self.send_fhir(
                        404, outcome("error", "Patient/{} not found".format(dfn))
                    )
                    return
                self.send_fhir(200, patients[0])
                return
            if parsed.path == "/fhir/Patient":
                status, body = patient_search_response(parse_qs(parsed.query))
                self.send_fhir(status, body)
                return
            if parsed.path.startswith("/fhir/"):
                parts = parsed.path.split("/")
                if len(parts) == 4 and parts[2] and parts[3]:
                    cached = cached_or_bundle_resource(parts[2], parts[3])
                    if cached:
                        self.send_fhir(200, cached)
                        return
            if parsed.path.startswith("/fhir/"):
                self.send_fhir(200, backend_json(parsed.path, parsed.query))
                return
            self.send_fhir(404, outcome("error", "Not found"))
        except Exception as exc:
            self.send_fhir(502, outcome("error", "Adapter error: {}".format(exc)))

    def log_message(self, fmt, *args):
        print(
            "%s - - [%s] %s"
            % (self.client_address[0], self.log_date_time_string(), fmt % args),
            flush=True,
        )


if __name__ == "__main__":
    print(
        "Serving RPMS FHIR REST adapter on {}:{}, backend {}".format(
            HOST, PORT, BACKEND
        ),
        flush=True,
    )
    HTTPServer((HOST, PORT), Handler).serve_forever()
