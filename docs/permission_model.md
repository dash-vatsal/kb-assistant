# Permission model
Principles: every chunk carries access groups; the filter runs in the database before ranking; unknown permissions mean excluded; page-level restrictions mean not indexed.

## Groups
| Group | Meaning | Source of truth |
|---|---|---|
| all-staff | company-wide docs | Confluence space permissions |
| project:alpha | members of Project Alpha | Jira project role / Confluence space group |
| sales | pre-sales team | IdP group |

## Container -> groups
See `config/access_map.yaml` (reviewed by: ____ on ____).

## Test users
| user | groups | must see | must NOT see |
|---|---|---|---|
| alice_a | all-staff, project:alpha | handbook, Alpha | Beta, sales |
| bob_b | all-staff, project:beta | handbook, Beta | Alpha, sales |
| sales_sam | all-staff, sales | handbook, sales | Alpha, Beta |
| new_nina | all-staff | handbook | all project and sales content |
| admin_ada | all groups | everything | n/a |

## Known gaps / production work
- Group membership is static in `users`; production must sync from the IdP.
- Permission changes at the source apply on the next sync. Define the maximum staleness (e.g., 1 hour).
- Page-level restrictions are skipped. Document how many pages that affects.
