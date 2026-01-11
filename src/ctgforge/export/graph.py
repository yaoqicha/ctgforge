from collections.abc import Sequence

import pandas as pd

from ..models.core import TrialCore


def to_property_graph(trials: Sequence[TrialCore]) -> tuple[pd.DataFrame, pd.DataFrame]:
    nodes = []
    edges = []

    def normalize_id(name: str) -> str:
        return name.strip().lower().replace(" ", "_")

    def node(node_id, label, **props):
        nodes.append({"node_id": node_id, "label": label, "props": props})

    def edge(src, rel, dst):
        edges.append({"src": src, "rel": rel, "dst": dst})

    for t in trials:
        tid = f"Trial:{t.nct_id}"
        node(
            tid,
            "Trial",
            title=t.brief_title,
            study_type=t.study_type,
            overall_status=t.overall_status,
        )

        for c in t.conditions:
            cid = f"Condition:{normalize_id(c.name)}"
            node(cid, "Condition", mesh_uid=c.mesh_uid if c.mesh_uid else None)
            edge(tid, "HAS_CONDITION", cid)

        for i in t.interventions:
            iid = f"Intervention:{normalize_id(i.name)}"
            node(
                iid,
                "Intervention",
                mesh_uid=i.mesh_uid if i.mesh_uid else None,
                type=i.type,
                arm_group_types=set(
                    [ag.type for ag in t.arm_groups if ag.label in i.arm_group_labels]
                ),
            )
            edge(tid, "HAS_INTERVENTION", iid)

        if t.lead_sponsor:
            sid = f"Sponsor:{normalize_id(t.lead_sponsor.name)}"
            node(sid, "Sponsor", type=t.lead_sponsor.type)
            edge(tid, "SPONSORED_BY", sid)

        if t.collaborators:
            for collab in t.collaborators:
                collid = f"Sponsor:{normalize_id(collab.name)}"
                node(collid, "Sponsor", type=collab.type)
                edge(tid, "COLLABORATED_BY", collid)

    nodes_df = pd.DataFrame(nodes).drop_duplicates("node_id")
    edges_df = pd.DataFrame(edges)

    return nodes_df, edges_df
