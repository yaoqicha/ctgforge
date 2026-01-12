from ctgforge import CTG, F


def _run_ctg(client=None):
    client = client or CTG()

    trial = client.get("NCT04633122")
    assert trial is not None

    total = client.count(
        None, extra={"query.term": "AREA[LastUpdatePostDate]RANGE[2025-01-01,MAX]"}
    )
    assert total > 0
    print(f"Total studies updated since 2025-01-01: {total}")

    q = (
        F.sponsor.eq("pfizer")
        & F.condition.contains("lung cancer")
        & F.phase.in_(["PHASE3", "PHASE4"])
        & F.status.in_(["RECRUITING", "COMPLETED"])
    )
    total = client.count(q)
    assert total >= 0
    print(f"Total matching studies: {total}")

    q = (
        F.condition.contains("lung cancer")
        & F.intervention.contains("pembrolizumab")
        & F.status.in_(["RECRUITING", "COMPLETED"])
        & F.phase.in_(["PHASE3", "PHASE4"])
    )

    total = client.count(q)
    assert total > 40
    print(f"Total matching studies: {total}")

    raw = list(client.search(q, limit=40))

    raw_offset = list(client.search(q, offset=20, limit=20))

    client.close()

    assert len(raw) == 40
    assert len(raw_offset) == 20

    assert (
        raw[0]["protocolSection"]["identificationModule"]["nctId"]
        != raw[20]["protocolSection"]["identificationModule"]["nctId"]
    )
    print("Sample NCT IDs:")
    for study in raw[:3]:
        print(study["protocolSection"]["identificationModule"]["nctId"])
    print("...")
    for study in raw[20:23]:
        print(study["protocolSection"]["identificationModule"]["nctId"])
    print("...")
    for study in raw[-3:]:
        print(study["protocolSection"]["identificationModule"]["nctId"])

    for i in range(20):
        assert (
            raw[i + 20]["protocolSection"]["identificationModule"]["nctId"]
            == raw_offset[i]["protocolSection"]["identificationModule"]["nctId"]
        )


def test_httpx_client():
    _run_ctg()


def test_requests_client():
    from ctgforge.client.requests_client import CTGRequestsClient

    _run_ctg(client=CTG(client=CTGRequestsClient()))
