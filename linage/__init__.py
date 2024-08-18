from abc import ABC

node_id = int
node_label = str

MAX_NODES = 10000


class Graph(ABC):

    def add(self, source: node_label, target: node_label) -> None:
        pass

    def upstream(self, paths: set[node_label]) -> set[str] | None:
        pass

    def downstream(self, paths: set[node_label]) -> set[str] | None:
        pass
