# General assumptions and simplified calculations:
# - node label - 1024 string length - in UTF8 (max 4B/char) = 4k/node
# - 10k nodes - 10k * 4k => 40MB
# - 10M edges - raw estimate node represented as ints (4Bytes) 20M*4 => 76MB though py doesn't have fixed size int types, would need to use NumPy if fixed size needed
# - python set has 64B overhead, list 56B on 64bit os -> 10k*64 = 625kB

from linage import MAX_NODES, node_label, node_id, Graph
from linage.tst import SynqTST


class PyGraph(Graph):
    # list access is  O(1) complexity
    def __init__(self, max_nodes: int = MAX_NODES):
        self._inverse_index: list[node_label | None] = [None] * max_nodes
        # self._index: dict[node_label, node_id] = {}  # might hold a lot of duplicate prefix strings - better would be TST but for generic labels ok
        self._index: SynqTST = SynqTST()
        self._upstream_nodes: list[set[node_id] | None] = [None] * max_nodes
        self._downstream_nodes: list[set[node_id] | None] = [None] * max_nodes
        self._node_count: int = 0
        self.max_nodes = max_nodes

    def add(self, source: node_label, target: node_label) -> None:
        source_id = self._maintain_indexes(source)
        target_id = self._maintain_indexes(target)

        if source_id != target_id:
            if downs := self._downstream_nodes[source_id]:
                downs.add(target_id)
            else:
                self._downstream_nodes[source_id] = {target_id}

            if ups := self._upstream_nodes[target_id]:
                ups.add(source_id)
            else:
                self._upstream_nodes[target_id] = {source_id}

        return None

    def _maintain_indexes(self, node: node_label) -> node_id:
        if self._index.get(node) is None:
            # self._index[node] = self._node_count
            self._index.insert(node, self._node_count)
            self._inverse_index[self._node_count] = node
            self._node_count += 1

        if self._index.get(node) is None:
            raise ValueError("Node should be indexed")

        return self._index.get(node)

    def upstream(self, paths: set[node_label]) -> set[str] | None:
        return self._reachable_nodes(paths, self._upstream_nodes)

    def _reachable_nodes(self, paths: set[node_label], adjustancy_list: list[set[node_id]]) -> set[node_label]:
        path_ids = [self._index.get(p) for p in paths if self._index.get(p) is not None]

        resulted_ids: set[node_id] = set()
        visited = [False] * self.max_nodes
        while True:
            iteration_result: set[node_id] = set()
            for id in path_ids:
                if not visited[id]:
                    if nodes := adjustancy_list[id]:
                        iteration_result |= nodes
                    visited[id] = True
            resulted_ids |= iteration_result
            if len(iteration_result) == 0:
                break
            path_ids = iteration_result

        return {self._inverse_index[id] for id in resulted_ids}

    def downstream(self, paths: set[node_label]) -> set[str] | None:
        return self._reachable_nodes(paths, self._downstream_nodes)
