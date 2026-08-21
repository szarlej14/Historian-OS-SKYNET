import unittest

from skynet_graph_engine import normalize_relation, traverse


class GraphEngineRealTests(unittest.TestCase):
    def test_string_relation_is_normalized(self):
        self.assertEqual(
            normalize_relation("A", "B"),
            {"source": "A", "target": "B", "relation": "related_to"},
        )

    def test_object_relation_supports_target(self):
        self.assertEqual(
            normalize_relation("A", {"type": "trained_at", "target": "B"}),
            {"source": "A", "target": "B", "relation": "trained_at"},
        )

    def test_object_relation_supports_legacy_to(self):
        self.assertEqual(
            normalize_relation("A", {"type": "related_to", "to": "B"}),
            {"source": "A", "target": "B", "relation": "related_to"},
        )

    def test_directed_depth_two(self):
        records = {
            "A": {"id": "A", "title": "A"},
            "B": {"id": "B", "title": "B"},
            "C": {"id": "C", "title": "C"},
        }
        relations = [
            normalize_relation("A", "B"),
            normalize_relation("B", {"type": "trained_at", "target": "C"}),
        ]
        visited, edges = traverse("A", 2, records, relations, mode="directed")
        self.assertEqual(visited, {"A": 0, "B": 1, "C": 2})
        self.assertEqual(len(edges), 2)
        self.assertEqual(edges[0]["target"], "B")
        self.assertEqual(edges[1]["target"], "C")


if __name__ == "__main__":
    unittest.main()
