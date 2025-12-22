from ctgforge import CTG, F
from ctgforge.export import to_dataframe, to_property_graph
from ctgforge.flatten import flatten_core


def test_ctg():
    client = CTG()

    q = (
        F.condition.contains("lung cancer")
        & F.intervention.contains("pembrolizumab")
        & F.status.in_(["RECRUITING", "COMPLETED"])
        & F.phase.in_(["PHASE3", "PHASE4"])
    )

    raw = list(client.search(q, page_size=20, max_studies=40))

    client.close()

    assert len(raw) == 40

    trials = [flatten_core(study) for study in raw]
    for trial in trials:
        assert trial.nct_id is not None
        assert trial.brief_title is not None
    print(trials[0])

    df = to_dataframe(trials)
    print(df.head())
    assert df.shape[0] == 40

    nodes, edges = to_property_graph(trials)
    assert len(nodes) > 0
    assert len(edges) > 0
    print(f"Nodes: {len(nodes)}, Edges: {len(edges)}")
    print(nodes[:5])
    print(edges[:5])
