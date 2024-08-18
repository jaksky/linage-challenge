import sys

from linage import MAX_NODES
from linage.tst import SynqTST


def test_tst():
    tst = SynqTST()

    def gen_resource(i) -> (str, int):
        return f"looker-be40cd52-fae2-11ed-8c85-3ed3943fecdc::ds-synq-ops.explore.fct_workspace_metrics::e-PROD::{i}", i

    for i in range(MAX_NODES):
        resource, value = gen_resource(i)
        tst.insert(resource, value)

    for i in range(MAX_NODES):
        resource, value = gen_resource(i)
        assert tst.get(resource) == value


def test_duplicate_insertion():
    tst = SynqTST()
    RESOURCE = "looker-be40cd52-fae2-11ed-8c85-3ed3943fecdc::ds-synq-ops.explore.fct_workspace_metrics::e-PROD"

    tst.insert(RESOURCE, 1)
    s = sys.getsizeof(tst)
    tst.insert(RESOURCE, 1)
    assert sys.getsizeof(tst) == s, "No insertion should happen"


    tst.insert(RESOURCE, 10000)
    assert sys.getsizeof(tst) == s, "No branch should be created"

    assert tst.get(RESOURCE) == 10000


def test_missing_resource():
    tst = SynqTST()
    RESOURCE = "looker-be40cd52-fae2-11ed-8c85-3ed3943fecdc::ds-synq-ops.explore.fct_workspace_metrics::e-PROD"

    assert tst.get("Not existing resource") is None

    tst.insert(RESOURCE, 1)

    assert tst.get("Not existing resource") is None
    assert tst.get(RESOURCE) == 1

