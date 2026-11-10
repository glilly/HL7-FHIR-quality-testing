# Inferno Scorecard Summary

- Session: `2dHYeBHIZVl`
- Run: `5e86fcbd-8943-4b2f-828f-ed0c3abcb848`
- URL: `https://showfhir.vistaplex.org/fhir`
- Patient IDs: `101258,101259,101260,101261,101262,101263,101264,101265,101266,101267,101268,101269,101270,101271,101272,101273,101274,101275,101276,101277,101278,101279,101280,101281,101282,101283,101284,101285,101286,101287,101288,101289,101290,101291`
- Session URL: https://inferno.healthit.gov/suites/g10_certification/2dHYeBHIZVl

## Result Counts

- pass: 4
- fail: 7
- skip: 46

## Non-Passing Results

- `fail` g10_certification-g10_smart_standalone_patient_app-smart_discovery_stu2_2-well_known_endpoint: `Content-Type` must be `application/json`, but received: `application/fhir+json`
- `fail` g10_certification-g10_smart_standalone_patient_app-smart_discovery_stu2_2-well_known_capabilities_stu2: Well-known configuration does not include `authorization_endpoint`
- `skip` g10_certification-g10_smart_standalone_patient_app-smart_standalone_launch_stu2_2-standalone_auth_tls: Could not verify when no url provided.
- `fail` g10_certification-g10_smart_standalone_patient_app-smart_standalone_launch_stu2_2-smart_app_redirect_stu2: OAuth2 Authorization Endpoint '' is not a valid URI
- `skip` g10_certification-g10_smart_standalone_patient_app-smart_standalone_launch_stu2_2-smart_token_response_headers: Request `standalone_token` was not made in a previous test as expected.
- `skip` g10_certification-g10_smart_standalone_patient_app-smart_standalone_launch_stu2_2-smart_cors_token_exchange: Request `standalone_token` was not made in a previous test as expected.
- `skip` g10_certification-g10_smart_standalone_patient_app-smart_openid_connect_stu2_2-smart_openid_decode_id_token: Input 'standalone_id_token' is nil, skipping test.
- `skip` g10_certification-g10_smart_standalone_patient_app-smart_openid_connect_stu2_2-smart_openid_required_configuration_fields: Input 'openid_configuration_json' is nil, skipping test.
- `skip` g10_certification-g10_smart_standalone_patient_app-g10_smart_standalone_token_refresh-g10_token_refresh_with_scopes: Input 'standalone_received_scopes' is nil, skipping test.
- `fail` g10_certification-g10_smart_standalone_patient_app-smart_discovery_stu2_2: 
- `skip` g10_certification-g10_smart_standalone_patient_app-smart_standalone_launch_stu2_2-standalone_token_tls: Could not verify when no url provided.
- `skip` g10_certification-g10_smart_standalone_patient_app-smart_standalone_launch_stu2_2-g10_unauthorized_access: Input 'standalone_patient_id' is nil, skipping test.
- `skip` g10_certification-g10_smart_standalone_patient_app-smart_standalone_launch_stu2_2-g10_patient_context: Input 'standalone_patient_id' is nil, skipping test.
- `skip` g10_certification-g10_smart_standalone_patient_app-smart_openid_connect_stu2_2-smart_openid_retrieve_configuration: Input 'id_token_payload_json' is nil, skipping test.
- `skip` g10_certification-g10_smart_standalone_patient_app-smart_openid_connect_stu2_2-smart_openid_retrieve_jwks: Input 'openid_jwks_uri' is nil, skipping test.
- `skip` g10_certification-g10_smart_standalone_patient_app-smart_openid_connect_stu2_2-smart_openid_token_payload: Input 'standalone_id_token' is nil, skipping test.
- `fail` g10_certification-g10_smart_standalone_patient_app-smart_discovery_stu2_2-g10_smart_well_known_capabilities: Expected the well-known capabilities to be an Array, but found NilClass
- `skip` g10_certification-g10_smart_standalone_patient_app-smart_standalone_launch_stu2_2-smart_code_received: Request `standalone_redirect` was not made in a previous test as expected.
- `skip` g10_certification-g10_smart_standalone_patient_app-smart_standalone_launch_stu2_2-smart_token_exchange_stu2_2: Input 'standalone_code' is nil, skipping test.
- `skip` g10_certification-g10_smart_standalone_patient_app-smart_standalone_launch_stu2_2-smart_token_response_body_stu2_2: Request `standalone_token` was not made in a previous test as expected.
- `skip` g10_certification-g10_smart_standalone_patient_app-smart_standalone_launch_stu2_2-g10_smart_scopes: Input 'standalone_received_scopes' is nil, skipping test.
- `skip` g10_certification-g10_smart_standalone_patient_app-g10_smart_standalone_token_refresh-g10_token_refresh_body_with_scopes: Input 'standalone_received_scopes' is nil, skipping test.
- `skip` g10_certification-g10_smart_standalone_patient_app-g10_smart_standalone_token_refresh-g10_patient_context: Input 'standalone_patient_id' is nil, skipping test.
- `skip` g10_certification-g10_smart_standalone_patient_app-g10_unrestricted_resource_type_access-g10_care_plan_unrestricted_access: Input 'standalone_patient_id' is nil, skipping test.
- `skip` g10_certification-g10_smart_standalone_patient_app-g10_unrestricted_resource_type_access-g10_diagnostic_report_unrestricted_access: Input 'standalone_patient_id' is nil, skipping test.
- `fail` g10_certification-g10_smart_standalone_patient_app-smart_standalone_launch_stu2_2: 
- `skip` g10_certification-g10_smart_standalone_patient_app-smart_openid_connect_stu2_2-smart_openid_token_header: Input 'id_token_header_json' is nil, skipping test.
- `skip` g10_certification-g10_smart_standalone_patient_app-smart_openid_connect_stu2_2: 
- `skip` g10_certification-g10_smart_standalone_patient_app-g10_smart_standalone_token_refresh-g10_token_refresh_body_without_scopes: Input 'standalone_received_scopes' is nil, skipping test.
- `skip` g10_certification-g10_smart_standalone_patient_app-g10_smart_standalone_token_refresh: 
- `skip` g10_certification-g10_smart_standalone_patient_app-g10_unrestricted_resource_type_access-g10_patient_unrestricted_access: Input 'standalone_patient_id' is nil, skipping test.
- `skip` g10_certification-g10_smart_standalone_patient_app-g10_unrestricted_resource_type_access-g10_condition_unrestricted_access: Input 'standalone_patient_id' is nil, skipping test.
- `skip` g10_certification-g10_smart_standalone_patient_app-g10_unrestricted_resource_type_access-g10_goal_unrestricted_access: Input 'standalone_patient_id' is nil, skipping test.
- `skip` g10_certification-g10_smart_standalone_patient_app-g10_unrestricted_resource_type_access-g10_procedure_unrestricted_access: Input 'standalone_patient_id' is nil, skipping test.
- `skip` g10_certification-g10_smart_standalone_patient_app-smart_openid_connect_stu2_2-smart_openid_fhir_user_claim: Input 'id_token_payload_json' is nil, skipping test.
- `skip` g10_certification-g10_smart_standalone_patient_app-smart_openid_connect_stu2_2-smart_cors_openid_fhir_user_claim: Input 'id_token_fhir_user' is nil, skipping test.
- `skip` g10_certification-g10_smart_standalone_patient_app-g10_smart_standalone_token_refresh-g10_token_refresh_without_scopes: Input 'standalone_received_scopes' is nil, skipping test.
- `skip` g10_certification-g10_smart_standalone_patient_app-g10_smart_standalone_token_refresh-g10_invalid_token_refresh: Input 'standalone_received_scopes' is nil, skipping test.
- `skip` g10_certification-g10_smart_standalone_patient_app-g10_unrestricted_resource_type_access-g10_allergy_intolerance_unrestricted_access: Input 'standalone_patient_id' is nil, skipping test.
- `skip` g10_certification-g10_smart_standalone_patient_app-g10_unrestricted_resource_type_access-g10_device_unrestricted_access: Input 'standalone_patient_id' is nil, skipping test.
- `skip` g10_certification-g10_smart_standalone_patient_app-g10_unrestricted_resource_type_access-g10_immunization_unrestricted_access: Input 'standalone_patient_id' is nil, skipping test.
- `skip` g10_certification-g10_smart_standalone_patient_app-g10_unrestricted_resource_type_access-g10_us_core_6_encounter_unrestricted_access: Input 'standalone_patient_id' is nil, skipping test.
- `skip` g10_certification-g10_smart_standalone_patient_app-g10_unrestricted_resource_type_access-Test01: Input 'standalone_patient_id' is nil, skipping test.
- `skip` g10_certification-g10_smart_standalone_patient_app-g10_unrestricted_resource_type_access-g10_care_team_unrestricted_access: Input 'standalone_patient_id' is nil, skipping test.
- `skip` g10_certification-g10_smart_standalone_patient_app-g10_unrestricted_resource_type_access-g10_document_reference_unrestricted_access: Input 'standalone_patient_id' is nil, skipping test.
- `skip` g10_certification-g10_smart_standalone_patient_app-g10_unrestricted_resource_type_access-g10_observation_unrestricted_access: Input 'standalone_patient_id' is nil, skipping test.
- `skip` g10_certification-g10_smart_standalone_patient_app-g10_unrestricted_resource_type_access-g10_us_core_6_coverage_unrestricted_access: Input 'standalone_patient_id' is nil, skipping test.
- `skip` g10_certification-g10_smart_standalone_patient_app-g10_unrestricted_resource_type_access: 
- `fail` g10_certification-g10_smart_standalone_patient_app: 
- `skip` g10_certification-g10_smart_standalone_patient_app-g10_unrestricted_resource_type_access-g10_medication_request_access: Input 'standalone_patient_id' is nil, skipping test.
- `skip` g10_certification-g10_smart_standalone_patient_app-g10_unrestricted_resource_type_access-g10_us_core_6_service_request_unrestricted_access: Input 'standalone_patient_id' is nil, skipping test.
- `skip` g10_certification-g10_smart_standalone_patient_app-g10_unrestricted_resource_type_access-g10_us_core_6_medication_dispense_unrestricted_access: Input 'standalone_patient_id' is nil, skipping test.
- `skip` g10_certification-g10_smart_standalone_patient_app-g10_standalone_credentials_export: Input 'standalone_patient_id' is nil, skipping test.
