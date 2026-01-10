from collections.abc import Sequence

import pandas as pd

from ..models.core import TrialCore


def to_property_graph(trials: Sequence[TrialCore]) -> tuple[pd.DataFrame, pd.DataFrame]:
    nodes = []
    edges = []

    def node(node_id, label, **props):
        nodes.append({"node_id": node_id, "label": label, "props": props})

    def edge(src, rel, dst):
        edges.append({"src": src, "rel": rel, "dst": dst})

    for t in trials:
        tid = f"Trial:{t.nct_id}"
        node(tid, "Trial", **t.model_dump(exclude={"prov"}))

        for c in t.conditions:
            cid = f"Condition:{c.name.lower()}"
            node(cid, "Condition", name=c.name, mesh_uid=c.mesh_uid if c.mesh_uid else None)
            edge(tid, "HAS_CONDITION", cid)

        for i in t.interventions:
            name = i.name
            if not name:
                continue
            iid = f"Intervention:{name.lower()}"
            node(iid, "Intervention", **i.model_dump())
            edge(tid, "HAS_INTERVENTION", iid)

        if t.lead_sponsor:
            sid = f"Sponsor:{t.lead_sponsor.name.lower()}"
            node(sid, "Sponsor", name=t.lead_sponsor.name, type=t.lead_sponsor.type)
            edge(tid, "SPONSORED_BY", sid)

    nodes_df = pd.DataFrame(nodes).drop_duplicates("node_id")
    edges_df = pd.DataFrame(edges)

    return nodes_df, edges_df
