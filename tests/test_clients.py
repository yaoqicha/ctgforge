from ctgforge import CTG, F


def _run_ctg(client=None):
    client = client or CTG()

    trial = client.get("NCT04633122")
    assert trial is not None

    q = (
        F.condition.contains("lung cancer")
        & F.intervention.contains("pembrolizumab")
        & F.status.in_(["RECRUITING", "COMPLETED"])
        & F.phase.in_(["PHASE3", "PHASE4"])
    )

    raw = list(client.search(q, page_size=20, max_studies=40))

    client.close()

    assert len(raw) == 40


def test_httpx_client():
    _run_ctg()


def test_requests_client():
    from ctgforge.client.requests_client import CTGRequestsClient

    _run_ctg(client=CTG(client=CTGRequestsClient()))
