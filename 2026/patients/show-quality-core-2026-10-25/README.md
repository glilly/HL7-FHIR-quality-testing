# US Quality Core showcase patients

Synthetic charts. No real person is represented.

These 34 bundles are what the public Show server returned for the
US Quality Core v0.5.0 run that passed every test and skipped none.
The suite was given all 34 patients in one session. No single chart
holds every example. Will Ford carries the medication administrations,
Vera Ellis the coverage, Ivy Ford the pediatric and not-done
immunization examples, and Nell Moss the remaining gap examples.

Inferno session: https://inferno.healthit.gov/suites/us_quality_core_v050/2yWbChvQkWt

Each file is the served collection Bundle for that patient,
`GET https://showfhir.vistaplex.org/fhir?dfn=` .
The browser link opens that same URL in the public FHIR browser
at https://worldvista.github.io/tjson-FHIR-browser/ .

The Cohorts column is the Show graph initial population for the six
measures we evaluate (CMS165, CMS122, CMS130, CMS125, CMS138, CMS2).
Ivy Ford is 8 years old and is outside every adult measure.
The Nye charts and a few others were built without hypertension,
diabetes, or a screening procedure, so they are outside those measures
on purpose. Official CQL counts for the whole Show load are in the
2026-10-26 showfhir quality card.

| Patient | FHIR | Browser | Cohorts |
| --- | --- | --- | --- |
| ZZAda Keene | [dfn 101258](https://showfhir.vistaplex.org/fhir?dfn=101258) | [open](https://worldvista.github.io/tjson-FHIR-browser/?url=https%3A%2F%2Fshowfhir.vistaplex.org%2Ffhir%3Fdfn%3D101258) | 165 122 130 125 138 2 |
| ZZBea Keene | [dfn 101259](https://showfhir.vistaplex.org/fhir?dfn=101259) | [open](https://worldvista.github.io/tjson-FHIR-browser/?url=https%3A%2F%2Fshowfhir.vistaplex.org%2Ffhir%3Fdfn%3D101259) | 165 122 130 125 138 2 |
| ZZCara Lopez | [dfn 101260](https://showfhir.vistaplex.org/fhir?dfn=101260) | [open](https://worldvista.github.io/tjson-FHIR-browser/?url=https%3A%2F%2Fshowfhir.vistaplex.org%2Ffhir%3Fdfn%3D101260) | 165 122 130 125 138 2 |
| ZZDina Lopez | [dfn 101261](https://showfhir.vistaplex.org/fhir?dfn=101261) | [open](https://worldvista.github.io/tjson-FHIR-browser/?url=https%3A%2F%2Fshowfhir.vistaplex.org%2Ffhir%3Fdfn%3D101261) | 165 122 130 125 138 2 |
| ZZEva Okonkwo | [dfn 101262](https://showfhir.vistaplex.org/fhir?dfn=101262) | [open](https://worldvista.github.io/tjson-FHIR-browser/?url=https%3A%2F%2Fshowfhir.vistaplex.org%2Ffhir%3Fdfn%3D101262) | 165 122 130 125 138 2 |
| ZZFiona Okonkwo | [dfn 101263](https://showfhir.vistaplex.org/fhir?dfn=101263) | [open](https://worldvista.github.io/tjson-FHIR-browser/?url=https%3A%2F%2Fshowfhir.vistaplex.org%2Ffhir%3Fdfn%3D101263) | 165 122 130 125 138 2 |
| ZZGina Park | [dfn 101264](https://showfhir.vistaplex.org/fhir?dfn=101264) | [open](https://worldvista.github.io/tjson-FHIR-browser/?url=https%3A%2F%2Fshowfhir.vistaplex.org%2Ffhir%3Fdfn%3D101264) | 165 122 130 125 138 2 |
| ZZHana Park | [dfn 101265](https://showfhir.vistaplex.org/fhir?dfn=101265) | [open](https://worldvista.github.io/tjson-FHIR-browser/?url=https%3A%2F%2Fshowfhir.vistaplex.org%2Ffhir%3Fdfn%3D101265) | 165 122 130 125 138 2 |
| ZZIris Quinn | [dfn 101266](https://showfhir.vistaplex.org/fhir?dfn=101266) | [open](https://worldvista.github.io/tjson-FHIR-browser/?url=https%3A%2F%2Fshowfhir.vistaplex.org%2Ffhir%3Fdfn%3D101266) | 165 122 130 125 138 2 |
| ZZJune Quinn | [dfn 101267](https://showfhir.vistaplex.org/fhir?dfn=101267) | [open](https://worldvista.github.io/tjson-FHIR-browser/?url=https%3A%2F%2Fshowfhir.vistaplex.org%2Ffhir%3Fdfn%3D101267) | 165 122 130 125 138 2 |
| ZZKira Shaw | [dfn 101268](https://showfhir.vistaplex.org/fhir?dfn=101268) | [open](https://worldvista.github.io/tjson-FHIR-browser/?url=https%3A%2F%2Fshowfhir.vistaplex.org%2Ffhir%3Fdfn%3D101268) | 165 122 130 125 138 2 |
| ZZLeah Shaw | [dfn 101269](https://showfhir.vistaplex.org/fhir?dfn=101269) | [open](https://worldvista.github.io/tjson-FHIR-browser/?url=https%3A%2F%2Fshowfhir.vistaplex.org%2Ffhir%3Fdfn%3D101269) | 165 122 130 125 138 2 |
| ZZMaya Vasquez | [dfn 101270](https://showfhir.vistaplex.org/fhir?dfn=101270) | [open](https://worldvista.github.io/tjson-FHIR-browser/?url=https%3A%2F%2Fshowfhir.vistaplex.org%2Ffhir%3Fdfn%3D101270) | 165 122 130 125 138 2 |
| ZZNina Vasquez | [dfn 101271](https://showfhir.vistaplex.org/fhir?dfn=101271) | [open](https://worldvista.github.io/tjson-FHIR-browser/?url=https%3A%2F%2Fshowfhir.vistaplex.org%2Ffhir%3Fdfn%3D101271) | 165 122 130 125 138 2 |
| ZZOra Walsh | [dfn 101272](https://showfhir.vistaplex.org/fhir?dfn=101272) | [open](https://worldvista.github.io/tjson-FHIR-browser/?url=https%3A%2F%2Fshowfhir.vistaplex.org%2Ffhir%3Fdfn%3D101272) | 165 122 130 125 138 2 |
| ZZPia Walsh | [dfn 101273](https://showfhir.vistaplex.org/fhir?dfn=101273) | [open](https://worldvista.github.io/tjson-FHIR-browser/?url=https%3A%2F%2Fshowfhir.vistaplex.org%2Ffhir%3Fdfn%3D101273) | 165 122 130 125 138 2 |
| ZZQuinn Young | [dfn 101274](https://showfhir.vistaplex.org/fhir?dfn=101274) | [open](https://worldvista.github.io/tjson-FHIR-browser/?url=https%3A%2F%2Fshowfhir.vistaplex.org%2Ffhir%3Fdfn%3D101274) | 165 122 130 125 138 2 |
| ZZRuth Young | [dfn 101275](https://showfhir.vistaplex.org/fhir?dfn=101275) | [open](https://worldvista.github.io/tjson-FHIR-browser/?url=https%3A%2F%2Fshowfhir.vistaplex.org%2Ffhir%3Fdfn%3D101275) | 165 122 130 125 138 2 |
| ZZSam Brant | [dfn 101276](https://showfhir.vistaplex.org/fhir?dfn=101276) | [open](https://worldvista.github.io/tjson-FHIR-browser/?url=https%3A%2F%2Fshowfhir.vistaplex.org%2Ffhir%3Fdfn%3D101276) | 165 138 2 |
| ZZTom Brant | [dfn 101277](https://showfhir.vistaplex.org/fhir?dfn=101277) | [open](https://worldvista.github.io/tjson-FHIR-browser/?url=https%3A%2F%2Fshowfhir.vistaplex.org%2Ffhir%3Fdfn%3D101277) | 122 130 138 2 |
| ZZUna Ellis | [dfn 101278](https://showfhir.vistaplex.org/fhir?dfn=101278) | [open](https://worldvista.github.io/tjson-FHIR-browser/?url=https%3A%2F%2Fshowfhir.vistaplex.org%2Ffhir%3Fdfn%3D101278) | 165 138 2 |
| ZZVera Ellis | [dfn 101279](https://showfhir.vistaplex.org/fhir?dfn=101279) | [open](https://worldvista.github.io/tjson-FHIR-browser/?url=https%3A%2F%2Fshowfhir.vistaplex.org%2Ffhir%3Fdfn%3D101279) | 165 122 130 125 138 2 |
| ZZWill Ford | [dfn 101280](https://showfhir.vistaplex.org/fhir?dfn=101280) | [open](https://worldvista.github.io/tjson-FHIR-browser/?url=https%3A%2F%2Fshowfhir.vistaplex.org%2Ffhir%3Fdfn%3D101280) | 138 2 |
| ZZIvy Ford | [dfn 101281](https://showfhir.vistaplex.org/fhir?dfn=101281) | [open](https://worldvista.github.io/tjson-FHIR-browser/?url=https%3A%2F%2Fshowfhir.vistaplex.org%2Ffhir%3Fdfn%3D101281) |  |
| ZZNell Moss | [dfn 101282](https://showfhir.vistaplex.org/fhir?dfn=101282) | [open](https://worldvista.github.io/tjson-FHIR-browser/?url=https%3A%2F%2Fshowfhir.vistaplex.org%2Ffhir%3Fdfn%3D101282) | 165 122 130 125 138 2 |
| ZZNia Moss | [dfn 101283](https://showfhir.vistaplex.org/fhir?dfn=101283) | [open](https://worldvista.github.io/tjson-FHIR-browser/?url=https%3A%2F%2Fshowfhir.vistaplex.org%2Ffhir%3Fdfn%3D101283) | 165 122 130 125 138 2 |
| ZZNora Moss | [dfn 101284](https://showfhir.vistaplex.org/fhir?dfn=101284) | [open](https://worldvista.github.io/tjson-FHIR-browser/?url=https%3A%2F%2Fshowfhir.vistaplex.org%2Ffhir%3Fdfn%3D101284) | 165 130 125 138 2 |
| ZZNola Nye | [dfn 101285](https://showfhir.vistaplex.org/fhir?dfn=101285) | [open](https://worldvista.github.io/tjson-FHIR-browser/?url=https%3A%2F%2Fshowfhir.vistaplex.org%2Ffhir%3Fdfn%3D101285) | 130 125 138 2 |
| ZZNyx Nye | [dfn 101286](https://showfhir.vistaplex.org/fhir?dfn=101286) | [open](https://worldvista.github.io/tjson-FHIR-browser/?url=https%3A%2F%2Fshowfhir.vistaplex.org%2Ffhir%3Fdfn%3D101286) | 130 125 138 2 |
| ZZOpal Nye | [dfn 101287](https://showfhir.vistaplex.org/fhir?dfn=101287) | [open](https://worldvista.github.io/tjson-FHIR-browser/?url=https%3A%2F%2Fshowfhir.vistaplex.org%2Ffhir%3Fdfn%3D101287) | 130 125 138 2 |
| ZZOna Nye | [dfn 101288](https://showfhir.vistaplex.org/fhir?dfn=101288) | [open](https://worldvista.github.io/tjson-FHIR-browser/?url=https%3A%2F%2Fshowfhir.vistaplex.org%2Ffhir%3Fdfn%3D101288) | 130 125 138 2 |
| ZZOda Nye | [dfn 101289](https://showfhir.vistaplex.org/fhir?dfn=101289) | [open](https://worldvista.github.io/tjson-FHIR-browser/?url=https%3A%2F%2Fshowfhir.vistaplex.org%2Ffhir%3Fdfn%3D101289) | 130 125 138 2 |
| ZZOra Nye | [dfn 101290](https://showfhir.vistaplex.org/fhir?dfn=101290) | [open](https://worldvista.github.io/tjson-FHIR-browser/?url=https%3A%2F%2Fshowfhir.vistaplex.org%2Ffhir%3Fdfn%3D101290) | 130 125 138 2 |
| ZZOla Nye | [dfn 101291](https://showfhir.vistaplex.org/fhir?dfn=101291) | [open](https://worldvista.github.io/tjson-FHIR-browser/?url=https%3A%2F%2Fshowfhir.vistaplex.org%2Ffhir%3Fdfn%3D101291) | 130 125 138 2 |

