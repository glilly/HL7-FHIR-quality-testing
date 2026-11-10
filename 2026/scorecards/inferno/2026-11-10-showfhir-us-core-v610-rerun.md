# Inferno Scorecard Summary

- Session: `kKbIwYshsz7`
- Run: `ec90939f-d713-4cfa-9d52-76a4de625eec`
- URL: `https://showfhir.vistaplex.org/fhir`
- Patient IDs: `101258,101259,101260,101261,101262,101263,101264,101265,101266,101267,101268,101269,101270,101271,101272,101273,101274,101275,101276,101277,101278,101279,101280,101281,101282,101283,101284,101285,101286,101287,101288,101289,101290,101291`
- Session URL: https://inferno.healthit.gov/suites/us_core_v610/kKbIwYshsz7

## Result Counts

- pass: 448
- fail: 4
- skip: 53

## Non-Passing Results

- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v610_patient-us_core_v610_patient_must_support_test: Could not find deceasedDateTime, extension:tribalAffiliation in the 34 provided resource(s)
- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v610_care_team-us_core_v610_care_team_reference_resolution_test: Could not resolve and validate any Must Support references for participant.member element: Reference(http://hl7.org/fhir/us/core/StructureDefinition/us-core-relatedperson)
- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v610_patient-us_core_v610_patient_death_date_family_search_test: Could not find values for all search params `death-date`, `family`
- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v610_patient: 
- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v610_care_plan-us_core_v610_care_plan_patient_category_status_date_search_test: Could not find values for all search params `patient`, `category`, `status`, `date`
- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v610_care_plan-us_core_v610_care_plan_patient_category_date_search_test: Could not find values for all search params `patient`, `category`, `date`
- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v610_care_team: 
- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v610_device: 
- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v610_condition_problems_health_concerns-us_core_v610_condition_problems_health_concerns_patient_category_encounter_search_test: Could not find values for all search params `patient`, `category`, `encounter`
- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v610_device-us_core_v610_device_patient_search_test: No Device resources appear to be available. Please use patients with more information
- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v610_device-us_core_v610_device_patient_type_search_test: Could not find values for all search params `patient`, `type`
- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v610_device-us_core_v610_device_patient_status_search_test: Could not find values for all search params `patient`, `status`
- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v610_device-us_core_v610_device_read_test: No Device resources appear to be available. Please use patients with more information.
- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v610_device-us_core_v610_device_provenance_revinclude_search_test: No Provenance resources appear to be available. Please use patients with more information
- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v610_device-us_core_v610_device_validation_test: No Device resources conforming to the http://hl7.org/fhir/us/core/StructureDefinition/us-core-implantable-device profile were returned
- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v610_device-us_core_v610_device_must_support_test: No Device resources were found
- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v610_device-us_core_v610_device_reference_resolution_test: No Device resources appear to be available. Please use patients with more information.
- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v610_diagnostic_report_note: 
- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v610_diagnostic_report_note-us_core_v610_diagnostic_report_note_reference_resolution_test: Could not resolve and validate any Must Support references for performer element: Reference(http://hl7.org/fhir/us/core/StructureDefinition/us-core-practitioner), result element: Reference(http://hl7.org/fhir/us/core/StructureDefinition/us-core-observation-lab)
- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v610_diagnostic_report_lab-us_core_v610_diagnostic_report_lab_reference_resolution_test: Could not resolve and validate any Must Support references for performer element: Reference(http://hl7.org/fhir/us/core/StructureDefinition/us-core-practitioner)
- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v610_immunization-us_core_v610_immunization_patient_date_search_test: No Immunization resources appear to be available. Please use patients with more information
- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v610_diagnostic_report_lab: 
- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v610_encounter: 
- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v610_encounter-us_core_v610_encounter_reference_resolution_test: Could not resolve and validate any Must Support references for reasonReference element: Reference(http://hl7.org/fhir/us/core/StructureDefinition/us-core-condition-problems-health-concerns)
- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v610_goal-us_core_v610_goal_patient_description_search_test: Could not find values for all search params `patient`, `description`
- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v610_observation_sexual_orientation-us_core_v610_observation_sexual_orientation_read_test: No Observation resources appear to be available. Please use patients with more information.
- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v610_observation_sexual_orientation-us_core_v610_observation_sexual_orientation_validation_test: No Observation resources conforming to the http://hl7.org/fhir/us/core/StructureDefinition/us-core-observation-sexual-orientation profile were returned
- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v610_observation_sexual_orientation-us_core_v610_observation_sexual_orientation_reference_resolution_test: No Observation resources appear to be available. Please use patients with more information.
- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v610_observation_sexual_orientation-us_core_v610_observation_sexual_orientation_patient_code_search_test: No Observation resources appear to be available. Please use patients with more information
- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v610_observation_sexual_orientation-us_core_v610_observation_sexual_orientation_patient_code_date_search_test: Could not find values for all search params `patient`, `code`, `date`
- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v610_observation_sexual_orientation-us_core_v610_observation_sexual_orientation_patient_category_status_search_test: Could not find values for all search params `patient`, `category`, `status`
- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v610_observation_sexual_orientation-us_core_v610_observation_sexual_orientation_patient_category_date_search_test: Could not find values for all search params `patient`, `category`, `date`
- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v610_observation_sexual_orientation-us_core_v610_observation_sexual_orientation_patient_category_search_test: Could not find values for all search params `patient`, `category`
- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v610_observation_sexual_orientation-us_core_v610_observation_sexual_orientation_provenance_revinclude_search_test: No Provenance resources appear to be available. Please use patients with more information
- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v610_observation_sexual_orientation-us_core_v610_observation_sexual_orientation_must_support_test: No Observation resources were found
- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v610_observation_sexual_orientation: 
- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v610_questionnaire_response: 
- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v610_questionnaire_response-us_core_v610_questionnaire_response_patient_search_test: No QuestionnaireResponse resources appear to be available. Please use patients with more information
- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v610_questionnaire_response-us_core_v610_questionnaire_response__id_search_test: Could not find values for all search params `_id`
- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v610_questionnaire_response-us_core_v610_questionnaire_response_patient_questionnaire_search_test: Could not find values for all search params `patient`, `questionnaire`
- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v610_questionnaire_response-us_core_v610_questionnaire_response_patient_authored_search_test: Could not find values for all search params `patient`, `authored`
- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v610_questionnaire_response-us_core_v610_questionnaire_response_patient_status_search_test: Could not find values for all search params `patient`, `status`
- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v610_questionnaire_response-us_core_v610_questionnaire_response_read_test: No QuestionnaireResponse resources appear to be available. Please use patients with more information.
- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v610_questionnaire_response-us_core_v610_questionnaire_response_provenance_revinclude_search_test: No Provenance resources appear to be available. Please use patients with more information
- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v610_questionnaire_response-us_core_v610_questionnaire_response_validation_test: No QuestionnaireResponse resources conforming to the http://hl7.org/fhir/us/core/StructureDefinition/us-core-questionnaireresponse profile were returned
- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v610_questionnaire_response-us_core_v610_questionnaire_response_must_support_test: No QuestionnaireResponse resources were found
- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v610_questionnaire_response-us_core_v610_questionnaire_response_reference_resolution_test: No QuestionnaireResponse resources appear to be available. Please use patients with more information.
- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v610_related_person-us_core_v610_related_person_read_test: No RelatedPerson resources appear to be available. Please use patients with more information.
- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v610_related_person: 
- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v400_clinical_notes_guidance-us_core_clinical_note_types: Could not find these DocumentReference types: 11488-4, 18842-5, 34117-2, 28570-0, 18748-4, 11502-2, 11526-1 and DiagnosticReport categories LP29708-2, LP7839-6.
- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v400_clinical_notes_guidance: 
- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v610_screening_assessment-us_core_screening_assessment_category: Could not find these Observation categories: http://hl7.org/fhir/us/core/CodeSystem/us-core-category|sdoh, http://hl7.org/fhir/us/core/CodeSystem/us-core-category|disability-status, http://hl7.org/fhir/us/core/CodeSystem/us-core-category|cognitive-status.
- `fail` us_core_v610-us_core_v610_fhir_api-us_core_311_data_absent_reason-us_core_311_data_absent_reason_extension: No resources using the DataAbsentReason Extension have been found
- `fail` us_core_v610-us_core_v610_fhir_api: 
- `fail` us_core_v610-us_core_v610_fhir_api: 
- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v610_screening_assessment: 
- `fail` us_core_v610-us_core_v610_fhir_api-us_core_311_data_absent_reason: 
