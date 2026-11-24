#!/usr/bin/env python3
"""
Κεντρικό πρόγραμμα εκτέλεσης — επιλογή μεθόδου αναζήτησης.

Παραδείγματα:
  python3 main.py --method dfs --scenario small
  python3 main.py --method bfs --scenario medium --monitor
  python3 main.py --method heuristic --scenario assignment
  python3 main.py --compare
  python3 main.py --tree --scenario small
"""

from __future__ import annotations

import argparse
import sys

from warehouse_robot.scenarios import SCENARIOS
from warehouse_robot.search import METHODS, SearchResult, bfs, dfs, best_first_search
from warehouse_robot.state import is_goal_state
from warehouse_robot.tree import print_search_tree


def run_one(method: str, scenario: str, monitor: bool, max_expanded: int) -> SearchResult:
    if scenario not in SCENARIOS:
        raise SystemExit(f"Άγνωστο scenario: {scenario}. Επιλογές: {list(SCENARIOS)}")
    if method not in METHODS:
        raise SystemExit(f"Άγνωστη μέθοδος: {method}. Επιλογές: {list(METHODS)}")

    start = SCENARIOS[scenario]()
    print("=" * 60)
    print(f"Σενάριο: {scenario}")
    print(start.pretty())
    print(f"is_goal_state(αρχική) = {is_goal_state(start)}")
    print("=" * 60)

    solver = METHODS[method]
    result = solver(start, monitor_frontier=monitor, max_expanded=max_expanded)
    print(result.summary())
    if result.success and result.goal_state is not None:
        print("-" * 60)
        print("Τελική κατάσταση:")
        print(result.goal_state.pretty())
        print(f"is_goal_state(τελική) = {is_goal_state(result.goal_state)}")
    return result


def run_compare(max_expanded: int) -> None:
    """Συγκριτική μελέτη όλων των μεθόδων σε όλα τα σενάρια."""
    methods = [("dfs", dfs), ("bfs", bfs), ("heuristic", best_first_search)]
    print("ΣΥΓΚΡΙΤΙΚΗ ΜΕΛΕΤΗ ΜΕΘΟΔΩΝ ΑΝΑΖΗΤΗΣΗΣ")
    print("=" * 72)
    header = f"{'Σενάριο':<12} {'Μέθοδος':<22} {'OK':<4} {'Βάθος':>6} {'Επεκτ.':>8} {'Μέτωπο':>8} {'sec':>8}"
    print(header)
    print("-" * 72)

    for scen_name, scen_fn in SCENARIOS.items():
        start = scen_fn()
        for method_name, solver in methods:
            result = solver(start, monitor_frontier=False, max_expanded=max_expanded)
            print(
                f"{scen_name:<12} {result.method:<22} "
                f"{'ΝΑΙ' if result.success else 'ΟΧΙ':<4} "
                f"{len(result.path):>6} {result.nodes_expanded:>8} "
                f"{result.max_frontier:>8} {result.elapsed_sec:>8.4f}"
            )
        print("-" * 72)

    print(
        "\nΣυμπεράσματα (σύνοψη):\n"
        "  • BFS βρίσκει λύση ελάχιστου μήκους (πλήθος ενεργειών) όταν ολοκληρώνει.\n"
        "  • DFS είναι οικονομική σε μνήμη μετώπου, αλλά το μονοπάτι είναι συχνά μακρύτερο.\n"
        "  • Η ευριστική Best-First επεκτείνει συνήθως τους λιγότερους κόμβους.\n"
        "  • Στο πλήρες πρόβλημα της εκφώνησης: BFS δίνει τη συντομότερη λύση, DFS τη μακρύτερη,\n"
        "    ενώ η Best-First ισορροπεί μήκος λύσης και αριθμό επεκτάσεων."
    )


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Ρομπότ αποθήκης — DFS / BFS / Ευριστική αναζήτηση"
    )
    p.add_argument(
        "--method",
        choices=sorted(METHODS.keys()),
        help="Μέθοδος αναζήτησης",
    )
    p.add_argument(
        "--scenario",
        choices=sorted(SCENARIOS.keys()),
        default="small",
        help="Αρχική κατάσταση (default: small)",
    )
    p.add_argument(
        "--monitor",
        action="store_true",
        help="Παράλληλη παρακολούθηση ουράς/στοίβας μονοπατιών",
    )
    p.add_argument(
        "--max-expanded",
        type=int,
        default=200_000,
        help="Όριο επεκτάσεων κόμβων (default: 200000)",
    )
    p.add_argument(
        "--compare",
        action="store_true",
        help="Συγκριτική εκτέλεση όλων των μεθόδων σε όλα τα σενάρια",
    )
    p.add_argument(
        "--tree",
        action="store_true",
        help="Εκτύπωση δένδρου αναζήτησης (πρώτα 4 επίπεδα)",
    )
    p.add_argument(
        "--tree-depth",
        type=int,
        default=4,
        help="Βάθος δένδρου (default: 4)",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.compare:
        run_compare(args.max_expanded)
        return 0

    if args.tree:
        start = SCENARIOS[args.scenario]()
        print_search_tree(
            start,
            max_depth=args.tree_depth,
            title=f"Δένδρο αναζήτησης — σενάριο '{args.scenario}'",
        )
        if not args.method:
            return 0

    if not args.method:
        build_parser().print_help()
        print(
            "\nΓρήγορη εκκίνηση:\n"
            "  python3 main.py --method heuristic --scenario small\n"
            "  python3 main.py --compare\n"
            "  python3 main.py --tree --scenario small\n"
        )
        return 1

    result = run_one(args.method, args.scenario, args.monitor, args.max_expanded)
    return 0 if result.success else 2


if __name__ == "__main__":
    sys.exit(main())
