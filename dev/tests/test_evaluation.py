"""R07: evaluation results do not depend on the order in which variants run, and totals cover the same cases."""
import sys
import unittest
from pathlib import Path

from cerbero_lab.fixtures import load
from cerbero_lab.variants import run_variant

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import run_evaluation  # noqa: E402

VOLATILE = {"runtime_ms"}


def stable(rows):
    return {(r["scenario"], r["variant_key"]): {k: v for k, v in r.items() if k not in VOLATILE} for r in rows}


class OrderInvariance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.forward = run_evaluation.evaluate(order=["A", "B", "C", "C-no-selector"])
        cls.backward = run_evaluation.evaluate(order=["C-no-selector", "C", "B", "A"])

    def test_same_functional_results_and_counters_in_both_orders(self):
        self.assertEqual(stable(self.forward["rows"]), stable(self.backward["rows"]))
        for variant, totals in self.forward["totals"].items():
            self.assertEqual({k: v for k, v in totals.items() if k not in VOLATILE},
                             {k: v for k, v in self.backward["totals"][variant].items() if k not in VOLATILE}, variant)

    def test_every_variant_runs_every_scenario(self):
        ids = [s["id"] for s in self.forward["scenarios"]]
        for variant, included in self.forward["included"].items():
            self.assertEqual(included["scenarios"], ids, variant)

    def test_a_variant_run_twice_on_one_scenario_object_matches_a_fresh_load(self):
        sc = load("fixtures/scenarios/S14-stale-memory-provenance.json")
        run_variant("C", sc)
        shared, shared_nas = run_variant("C-no-selector", sc)
        fresh, fresh_nas = run_variant("C-no-selector", load("fixtures/scenarios/S14-stale-memory-provenance.json"))
        self.assertEqual(shared_nas.stats(), fresh_nas.stats())
        self.assertEqual(shared.revalidated, fresh.revalidated)
        self.assertEqual(shared.states, fresh.states)


if __name__ == "__main__":
    unittest.main()
