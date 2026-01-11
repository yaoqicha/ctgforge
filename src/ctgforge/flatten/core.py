from ..models.core import (
    Agency,
    ArmGroup,
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
            date=status.get("startDateStruct").get("date"),
            type=status.get("startDateStruct").get("type"),
        )
        if status.get("startDateStruct")
        else None,
        completion_date=DateStruct(
            date=status.get("completionDateStruct").get("date"),
            type=status.get("completionDateStruct").get("type"),
        )
        if status.get("completionDateStruct")
        else None,
        primary_completion_date=DateStruct(
            date=status.get("primaryCompletionDateStruct").get("date"),
            type=status.get("primaryCompletionDateStruct").get("type"),
        )
        if status.get("primaryCompletionDateStruct")
        else None,
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
                    iter(
                        [
                            mesh
                            for mesh in cond_browse.get("meshes", [])
                            if mesh.get("term").lower() == c.lower()
                        ]
                    ),
                    {},
                ).get("id"),
            )
            for c in conds.get("conditions", [])
        ],
        arm_groups=[
            ArmGroup(
                label=ag.get("label"),
                type=ag.get("type"),
                description=ag.get("description"),
                intervention_names=ag.get("interventionNames", []),
            )
            for ag in arms.get("armGroups", [])
        ],
        interventions=[
            Intervention(
                name=intr.get("name"),
                type=intr.get("type"),
                description=intr.get("description"),
                other_names=intr.get("otherNames", []),
                arm_group_labels=intr.get("armGroupLabels", []),
                mesh_uid=next(
                    iter(
                        [
                            mesh
                            for mesh in intr_browse.get("meshes", [])
                            if mesh.get("term").lower() == intr.get("name").lower()
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
