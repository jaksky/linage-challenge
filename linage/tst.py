class TSTNode:
    def __init__(self, fragment: str):
        self.fragment: str = fragment
        self.value: int | None = None
        self.left: TSTNode | None = None
        self.eq: TSTNode | None = None
        self.right: TSTNode | None = None


class SynqTST:
    """
    I would preffer to use some py lib, just couldn't find any. So this is quick naive implementation with the main purpose of:
    - save some memory space when using syng resource paths (induced based on few examples)
    - access is suboptimal, since there is no balancing

    This class could be more generic as TODO if ever needed
    """
    def __init__(self):
        self.root: TSTNode = TSTNode("")

    def insert(self, resource: str, value: int) -> None:
        def _insert(root: TSTNode, resource_fragments: list[str], value: int):
            if not root:
                root = TSTNode(resource_fragments[0])

            if resource_fragments[0] < root.fragment:
                root.left = _insert(root.left, resource_fragments, value)
            elif resource_fragments[0] > root.fragment:
                root.right = _insert(root.right, resource_fragments, value)
            else:
                if len(resource_fragments) > 1:
                    root.eq = _insert(root.eq, resource_fragments[1:], value)
                else:
                    root.value = value
            return root

        _insert(self.root, SynqTST._parse_syng_resource(resource), value)

    def get(self, resource: str) -> int | None:
        def _get(root: TSTNode, resource_fragments: list[str]) -> int | None:
            if not root:
                return None
            if resource_fragments[0] < root.fragment:
                return _get(root.left, resource_fragments)
            elif resource_fragments[0] > root.fragment:
                return _get(root.right, resource_fragments)
            else:
                if len(resource_fragments) > 1:
                    return _get(root.eq, resource_fragments[1:])
                else:
                    return root.value
        return _get(self.root, SynqTST._parse_syng_resource(resource))

    @staticmethod
    def _parse_syng_resource(string: str) -> list[str]:
        segments = []
        for part in string.split('::'):
            segments.extend(part.split('.'))
        return segments

