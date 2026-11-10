# Inferno Scorecard Summary

- Session: `h8r8foXkQ5E`
- Run: `851f36b5-2573-4863-b573-801dd1200804`
- URL: `https://showfhir.vistaplex.org/fhir`
- Patient IDs: `101258,101259,101260,101261,101262,101263,101264,101265,101266,101267,101268,101269,101270,101271,101272,101273,101274,101275,101276,101277,101278,101279,101280,101281,101282,101283,101284,101285,101286,101287,101288,101289,101290,101291`
- Session URL: https://inferno.healthit.gov/suites/us_core_v610/h8r8foXkQ5E

## Result Counts

- pass: 499
- fail: 4
- skip: 2

## Non-Passing Results

- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v610_diagnostic_report_note-us_core_v610_diagnostic_report_note_reference_resolution_test: Could not resolve and validate any Must Support references for result element: Reference(http://hl7.org/fhir/us/core/StructureDefinition/us-core-observation-lab)
- `skip` us_core_v610-us_core_v610_fhir_api-us_core_v610_diagnostic_report_note: 
- `fail` us_core_v610-us_core_v610_fhir_api-us_core_v610_document_reference-us_core_v610_document_reference_patient_type_search_test: DocumentReference/note-11488-4 did not match the search parameters: * Expected: 11506-3 * Found: #<FHIR::R4::CodeableConcept:0x00007ff06691b870 @id=nil, @extension=[], @coding=[#<FHIR::R4::Coding:0x00007ff06691b820 @id=nil, @extension=[], @system="http://loinc.org", @version=nil, @code="11488-4", @display="Consult Note", @userSelected=nil, @source_hash={"code"=>"11488-4", "display"=>"Consult Note", "system"=>"http://loinc.org"}>], @text=nil, @source_hash={"coding"=>[{"code"=>"11488-4", "display"=>"Consult Note", "system"=>"http://loinc.org"}]}>
- `fail` us_core_v610-us_core_v610_fhir_api-us_core_v610_document_reference: 
- `fail` us_core_v610-us_core_v610_fhir_api: 
- `fail` us_core_v610-us_core_v610_fhir_api: 
