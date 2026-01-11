from ctgforge import CTG
from ctgforge.export import to_dataframe, to_property_graph
from ctgforge.flatten import flatten_core


def test_exports():
    client = CTG()

    raw = list(client.search(None, page_size=10, max_studies=10))

    client.close()

    assert len(raw) == 10

    trials = [flatten_core(study) for study in raw]
    for trial in trials:
        assert trial.nct_id is not None
        assert trial.brief_title is not None
    print(trials[0])

    df = to_dataframe(trials)
    print(df.head())
    assert df.shape[0] == 10

    nodes, edges = to_property_graph(trials)
    assert len(nodes) > 0
    assert len(edges) > 0
    print(f"Nodes: {len(nodes)}, Edges: {len(edges)}")
    print(nodes[:5])
    print(edges[:5])
