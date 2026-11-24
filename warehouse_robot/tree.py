"""
Σχεδίαση δένδρου αναζήτησης (μη εξαντλητικό) — πρώτα max_depth επίπεδα.
Χρησιμοποιείται για DFS/BFS όπως ζητά η εκφώνηση (έως 4 επίπεδα).
"""

from __future__ import annotations

from typing import List, Set

from .operators import find_children
from .state import State


def build_search_tree(start: State, max_depth: int = 4) -> List[str]:
    """
    Επιστρέφει γραμμές ASCII που αναπαριστούν το δένδρο αναζήτησης
    μέχρι βάθος max_depth (ρίζα = επίπεδο 0).
    """
    lines: List[str] = []
    closed: Set[tuple] = set()

    def walk(state: State, depth: int, prefix: str, is_last: bool, op_name: str) -> None:
        connector = "" if depth == 0 else ("└── " if is_last else "├── ")
        cargo = list(state.cargo) if state.cargo else "[]"
        pos = "Είσοδος" if state.robot_pos == 0 else f"Θέση {state.robot_pos}"
        rem = state.packages_on_shelves()
        ent = len(state.entrance)
        tag = op_name if op_name else "ΑΡΧΗ"
        lines.append(
            f"{prefix}{connector}{tag} · {pos} · cargo={cargo} · "
            f"ράφια={rem} · είσοδος={ent}"
        )

        key = state.canonical_key()
        if depth >= max_depth:
            return
        if key in closed:
            pad = prefix + ("    " if is_last else "│   ")
            lines.append(f"{pad}└── (κύκλος/επισκεφθείσα)")
            return
        closed.add(key)

        children = find_children(state)
        child_prefix = "" if depth == 0 else prefix + ("    " if is_last else "│   ")
        for i, (name, child) in enumerate(children):
            walk(child, depth + 1, child_prefix, i == len(children) - 1, name)

    walk(start, 0, "", True, "")
    return lines


def print_search_tree(start: State, max_depth: int = 4, title: str = "") -> str:
    """Εκτυπώνει και επιστρέφει το δένδρο ως κείμενο."""
    header = title or f"Δένδρο αναζήτησης (πρώτα {max_depth} επίπεδα)"
    body = "\n".join(build_search_tree(start, max_depth=max_depth))
    text = f"{header}\n{'=' * len(header)}\n{body}"
    print(text)
    return text
