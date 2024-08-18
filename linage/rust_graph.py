from rustworkx import rustworkx as rx

from linage import MAX_NODES, node_label, node_id
from linage.tst import SynqTST


class RustGraph:
    """
    Implementation of Graph using external Rust library
    """
    def __init__(self, max_nodes: int = MAX_NODES):
        self._inverse_index: list[node_label | None] = [None] * max_nodes
        # self._index: dict[node_label, node_id] = {}  # might hold a lot of duplicate prefix strings - better would be TST but for generic labels ok
        self._index: SynqTST = SynqTST()
        self._graph = rx.PyDiGraph(check_cycle=True, multigraph=False, node_count_hint=max_nodes)
        self.node_count: int = 0
        self.max_nodes = max_nodes

    def add(self, source: node_label, target: node_label) -> None:
        source_id = self._maintain_indexes(source)
        target_id = self._maintain_indexes(target)

        if source_id != target_id:
            self._graph.add_edge(source_id, target_id, None)

        return None

    def _maintain_indexes(self, node: node_label) -> node_id:
        if self._index.get(node) is None:
            node_index = self._graph.add_node(None)
            # self._index[node] = node_index
            self._index.insert(node, node_index)
            self._inverse_index[node_index] = node
            self.node_count += 1

        if self._index.get(node) is None:
            raise ValueError("Returning None shouldn't happen here")

        return self._index.get(node)

    def upstream(self, paths: set[node_label]) -> set[str] | None:
        path_ids = [self._index.get(p) for p in paths if self._index.get(p) is not None]
        resulted_ids = set()
        for p_id in path_ids:
            resulted_ids |= rx.ancestors(self._graph, p_id)

        return {self._inverse_index[id] for id in resulted_ids}

    def downstream(self, paths: set[node_label]) -> set[str] | None:
        path_ids = [self._index.get(p) for p in paths if self._index.get(p) is not None]
        resulted_ids = set()
        for p_id in path_ids:
            resulted_ids |= rx.descendants(self._graph, p_id)

        return {self._inverse_index[id] for id in resulted_ids}