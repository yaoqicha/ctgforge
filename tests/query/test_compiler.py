import pytest

from ctgforge.query.compiler import QueryCompilerError, compile_to_params
from ctgforge.query.fields import F


def test_compile_simple_eq():
    expr = F.condition.eq("diabetes")
    params = compile_to_params(expr)
    assert params.params == {"query.cond": '"diabetes"'}

    expr = F.sponsor.eq("Acme Pharma")
    params = compile_to_params(expr)
    assert params.params == {"query.spons": '"Acme+Pharma"'}


def test_compile_simple_in():
    expr = F.intervention.in_(["drug A", "drug B"])
    params = compile_to_params(expr)
    assert params.params == {"query.intr": '("drug+A"+OR+"drug+B")'}

    expr = F.title.in_(["Cancer Study", "Heart Study"])
    params = compile_to_params(expr)
    assert params.params == {"query.titles": '("Cancer+Study"+OR+"Heart+Study")'}


def test_compile_simple_contains():
    expr = F.title.contains("Cancer")
    params = compile_to_params(expr)
    assert params.params == {"query.titles": "(Cancer)"}


def test_compile_simple_filter_list():
    expr = F.status.in_(["RECRUITING", "COMPLETED"])
    params = compile_to_params(expr)
    assert params.params == {"filter.overallStatus": "RECRUITING,COMPLETED"}


def test_compile_and_or():
    expr = (
        F.condition.eq("diabetes")
        & F.sponsor.eq("Acme Pharma")
        & F.intervention.eq("drug A")
        & F.title.contains("Study")
        & F.status.in_(["RECRUITING", "COMPLETED"])
    )
    params = compile_to_params(expr)
    assert params.params == {
        "query.cond": '"diabetes"',
        "query.spons": '"Acme+Pharma"',
        "query.intr": '"drug+A"',
        "query.titles": "(Study)",
        "filter.overallStatus": "RECRUITING,COMPLETED",
    }

    expr = F.condition.eq("diabetes") | F.condition.eq("hypertension")
    params = compile_to_params(expr)
    assert params.params == {
        "query.cond": '("diabetes")+OR+("hypertension")',
    }


def test_compile_or_across_different_fields_error():
    with pytest.raises(QueryCompilerError):
        expr = F.condition.eq("diabetes") | F.sponsor.eq("Acme Pharma")
        compile_to_params(expr)
