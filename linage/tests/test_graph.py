from pathlib import Path

from linage import MAX_NODES
from linage.py_graph import PyGraph
from linage.rust_graph import RustGraph
from time import perf_counter
import pytest
import pyarrow.parquet as pq
import daggen as dg

PARQUET = Path(__file__).parents[1] / "resources" / "synq-lineage.parquet"

@pytest.mark.parametrize("cls", [PyGraph, RustGraph])
def test_load_graph(cls) -> None:
    g = cls()
    g.add("A", "B")
    g.add("A", "B")
    g.add("A", "C")
    g.add("B", "C")
    g.add("AA", "B")
    g.add("AAA", "AA")
    g.add("AAAA", "AA")
    g.add("B", "CC")
    g.add("CC", "C")
    g.add("C", "D")

    start = perf_counter()
    assert g.upstream({"B"}) == {"A", "AAA", "AA", "AAAA"}
    assert g.downstream({"B"}) == {"C", "CC", "D"}
    end = perf_counter()
    assert end - start < 1e-3


@pytest.mark.parametrize("cls", [PyGraph, RustGraph])
def test_self_loop(cls) -> None:
    g = cls()
    g.add("A", "A")

    assert len(g.upstream({"A"})) == 0


@pytest.mark.parametrize("cls", [PyGraph, RustGraph])
def test_two_sources(cls) -> None:
    g = cls()
    g.add("A1", "B")
    g.add("A2", "B")

    assert g.upstream({"B"}) == {"A1", "A2"}


@pytest.mark.timeout(1)
# @pytest.mark.xfail(reason="Not validating the inputs, Not a valid DAG -> infinite loop")
@pytest.mark.parametrize("cls", [PyGraph])  # RustGraph is capable of detecting cycle
def test_cycle_graph(cls) -> None:
    g = cls()
    g.add("A", "B")
    g.add("B", "C")
    g.add("C", "A")
    start = perf_counter()
    assert g.upstream({"A"}) == {"A", "B", "C"}
    assert g.downstream({"A"}) == {"A", "B", "C"}
    end = perf_counter()
    assert end - start < 1e-3


@pytest.mark.parametrize("cls", [PyGraph, RustGraph])
def test_synq_lineage(cls) -> None:
    parquet_file = pq.ParquetFile(PARQUET)
    table = parquet_file.read()
    df = table.to_pandas()

    g = cls()
    for _, row in df.iterrows():
        # print(f"{row['source']} -> {row['target']}")
        g.add(row["source"], row["target"])

    assert g.upstream({"dbt-sh-d577b364-a867-11ed-b4b2-fe8020e7ba25::model.ops.stg_runs"}) == {'ch-prod::default::runs',
                                                                                               'dbt-sh-d577b364-a867-11ed-b4b2-fe8020e7ba25::source.ops.default.runs'}
    start = perf_counter()
    q = g.downstream({"dbt-sh-d577b364-a867-11ed-b4b2-fe8020e7ba25::model.ops.stg_runs"})
    end = perf_counter()
    assert end - start < 10.e-5
    assert len(q) > 0


def test_performance_on_large_dag() -> None:
    dag = dg.DAG(seed=42, num_tasks=MAX_NODES, min_data=0, max_data=0, min_alpha=0, max_alpha=0)
    tasks, edges = dag.task_n_edge_dicts()

    rust_graph = RustGraph()
    python_graph = PyGraph()

    for edge in edges:
        rust_graph.add(str(edge["source"]), str(edge["target"]))
        python_graph.add(str(edge["source"]), str(edge["target"]))

    rust_upstream_start = perf_counter()
    rust_upstream = rust_graph.upstream({"5000"})
    rust_upstream_delta = perf_counter() - rust_upstream_start

    rust_downstream_start = perf_counter()
    rust_downstream = rust_graph.downstream({"5000"})
    rust_downstream_delta = perf_counter() - rust_downstream_start

    py_upstream_start = perf_counter()
    py_upstream = python_graph.upstream({"5000"})
    py_upstream_delta = perf_counter() - py_upstream_start

    py_downstream_start = perf_counter()
    py_downstream = python_graph.downstream({"5000"})
    py_downstream_delta = perf_counter() - py_downstream_start

    print(rust_upstream_delta / py_upstream_delta)
    print(rust_upstream_delta)
    print(py_upstream_delta)

    print(rust_downstream_delta / py_downstream_delta)
    print(rust_downstream_delta)
    print(py_downstream_delta)

    assert rust_upstream == py_upstream
    assert rust_downstream == py_downstream

    assert rust_upstream_delta < 10e-3
    assert rust_downstream_delta < 10e-3
    assert py_upstream_delta < 10e-3
    assert py_downstream_delta < 10e-3
