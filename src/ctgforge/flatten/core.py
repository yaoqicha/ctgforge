from ..models.core import (
    Agency,
    Condition,
    DateStruct,
    Intervention,
    TrialCore,
)


def flatten_core(raw: dict) -> TrialCore:
    p = raw.get("protocolSection", {})
    d = raw.get("derivedSection", {})

    ident = p.get("identificationModule", {})
    status = p.get("statusModule", {})
    design = p.get("designModule", {})
    conds = p.get("conditionsModule", {})
    arms = p.get("armsInterventionsModule", {})
    sponsor = p.get("sponsorCollaboratorsModule", {})

    cond_browse = d.get("conditionBrowseModule", {})
    intr_browse = d.get("interventionBrowseModule", {})

    trial = TrialCore(
        nct_id=ident.get("nctId"),
        brief_title=ident.get("briefTitle"),
        official_title=ident.get("officialTitle"),
        study_type=design.get("studyType"),
        overall_status=status.get("overallStatus"),
        phases=design.get("phases", []),
        start_date=DateStruct(
            date=status.get("startDateStruct", {}).get("date"),
            type=status.get("startDateStruct", {}).get("type"),
        ),
        completion_date=DateStruct(
            date=status.get("completionDateStruct", {}).get("date"),
            type=status.get("completionDateStruct", {}).get("type"),
        ),
        primary_completion_date=DateStruct(
            date=status.get("primaryCompletionDateStruct", {}).get("date"),
            type=status.get("primaryCompletionDateStruct", {}).get("type"),
        ),
        lead_sponsor=Agency(
            name=sponsor.get("leadSponsor", {}).get("name"),
            type=sponsor.get("leadSponsor", {}).get("class"),
        ),
        collaborators=[
            Agency(
                name=collab.get("name"),
                type=collab.get("class"),
            )
            for collab in sponsor.get("collaborators", [])
        ],
        conditions=[
            Condition(
                name=c,
                mesh_uid=next(
                    iter([mesh for mesh in cond_browse.get("meshes", []) if mesh.get("term") == c]),
                    {},
                ).get("id"),
            )
            for c in conds.get("conditions", [])
        ],
        interventions=[
            Intervention(
                name=intr.get("name"),
                type=intr.get("type"),
                description=intr.get("description"),
                other_names=intr.get("otherNames", []),
                arm_group_types=[
                    next(
                        iter(
                            [ag for ag in arms.get("armGroups", []) if ag.get("label") == ag_label]
                        ),
                        {},
                    ).get("type", "OTHER")
                    for ag_label in intr.get("armGroupLabels", [])
                ],
                mesh_uid=next(
                    iter(
                        [
                            mesh
                            for mesh in intr_browse.get("meshes", [])
                            if mesh.get("term") == intr.get("name")
                        ]
                    ),
                    {},
                ).get("id"),
            )
            for intr in arms.get("interventions", [])
        ],
        has_results=raw.get("hasResults", False),
    )

    return trial
