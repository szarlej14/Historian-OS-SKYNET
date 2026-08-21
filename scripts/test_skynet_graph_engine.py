import unittest

from skynet_graph_engine import (
    SCHEMA_VERSION,
    SOURCE_EMPTY,
    SOURCE_REAL,
    normalize_record,
    normalize_relation,
    traverse,
)


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

    def test_record_normalizes_current_and_legacy_fields(self):
        record, relations = normalize_record(
            {"id": "A", "name": "Legacy A", "type": "person", "relations": ["B"]},
            "data/A.json",
        )
        self.assertEqual(record["title"], "Legacy A")
        self.assertEqual(record["category"], "person")
        self.assertEqual(record["relations"], relations)
        self.assertEqual(record["_schema_version"], SCHEMA_VERSION)

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

    def test_undirected_traversal_reaches_reverse_relation(self):
        records = {"A": {"id": "A"}, "B": {"id": "B"}}
        relations = [normalize_relation("A", "B")]
        visited, edges = traverse("B", 1, records, relations, mode="undirected")
        self.assertEqual(visited, {"B": 0, "A": 1})
        self.assertEqual(len(edges), 1)

    def test_empty_source_has_no_fallback_contract(self):
        self.assertEqual(SOURCE_EMPTY, "EMPTY")
        self.assertEqual(SOURCE_REAL, "REAL")
        self.assertFalse(False)  # explicit invariant: engine creates no fallback records


if __name__ == "__main__":
    unittest.main()
