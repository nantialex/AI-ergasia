"""
Αλγόριθμοι αναζήτησης με παρακολούθηση μετώπου (frontier / ανοιχτή λίστα):
  - DFS  (πρώτα σε βάθος) — στοίβα (LIFO)
  - BFS  (πρώτα σε πλάτος) — ουρά (FIFO)
  - Best-First (ευριστική) — ουρά προτεραιότητας με βάση h(n)

Κάθε κόμβος κρατά το μονοπάτι τελεστών από την αρχή, ώστε στο τέλος
να επιστρέφεται η λύση ως ακολουθία ενεργειών.

Η παράμετρος monitor_frontier επιτρέπει παράλληλη παρακολούθηση της
ουράς/στοίβας των μονοπατιών σε κάθε βήμα επέκτασης.
"""

from __future__ import annotations

import heapq
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Callable, Deque, List, Optional, Set, Tuple

from .heuristics import heuristic
from .operators import find_children
from .state import State, is_goal_state


@dataclass
class SearchNode:
    """Κόμβος αναζήτησης: κατάσταση + μονοπάτι τελεστών + βάθος."""

    state: State
    path: Tuple[str, ...] = ()
    depth: int = 0

    def path_label(self) -> str:
        if not self.path:
            return "(αρχή)"
        return " → ".join(self.path)


@dataclass
class SearchResult:
    """Αποτέλεσμα εκτέλεσης αλγορίθμου αναζήτησης."""

    method: str
    success: bool
    path: Tuple[str, ...] = ()
    goal_state: Optional[State] = None
    nodes_expanded: int = 0
    nodes_generated: int = 0
    max_frontier: int = 0
    elapsed_sec: float = 0.0
    message: str = ""

    def summary(self) -> str:
        lines = [
            f"Μέθοδος: {self.method}",
            f"Επιτυχία: {'ΝΑΙ' if self.success else 'ΟΧΙ'}",
            f"Κόμβοι που επεκτάθηκαν: {self.nodes_expanded}",
            f"Κόμβοι που παρήχθησαν: {self.nodes_generated}",
            f"Μέγιστο μέγεθος μετώπου: {self.max_frontier}",
            f"Χρόνος: {self.elapsed_sec:.4f} sec",
            f"Μήκος λύσης (ενέργειες): {len(self.path)}",
        ]
        if self.path:
            lines.append("Μονοπάτι λύσης:")
            lines.append("  " + " → ".join(self.path))
        if self.message:
            lines.append(f"Σημείωση: {self.message}")
        return "\n".join(lines)


def _print_frontier(label: str, items: List[str], step: int) -> None:
    """Εκτύπωση στιγμιότυπου της ουράς/στοίβας μονοπατιών (παρακολούθηση μετώπου)."""
    preview = items[:8]
    more = f" ... (+{len(items) - 8})" if len(items) > 8 else ""
    print(f"[βήμα {step}] {label} | μέγεθος={len(items)}")
    for i, item in enumerate(preview, start=1):
        print(f"    {i}. {item}")
    if more:
        print(f"    {more}")


def dfs(
    start: State,
    *,
    monitor_frontier: bool = False,
    max_expanded: int = 200_000,
) -> SearchResult:
    """
    Πρώτα σε βάθος αναζήτηση (DFS) με κλειστό σύνολο και στοίβα μετώπου.
    """
    t0 = time.perf_counter()
    frontier: List[SearchNode] = [SearchNode(start)]
    closed: Set[tuple] = set()
    expanded = 0
    generated = 0
    max_frontier = 1

    while frontier:
        max_frontier = max(max_frontier, len(frontier))
        if monitor_frontier:
            _print_frontier(
                "Μέτωπο DFS (στοίβα, πάνω=επόμενο)",
                [n.path_label() for n in reversed(frontier)],
                expanded,
            )

        node = frontier.pop()  # LIFO
        key = node.state.canonical_key()
        if key in closed:
            continue
        closed.add(key)
        expanded += 1

        if is_goal_state(node.state):
            return SearchResult(
                method="DFS",
                success=True,
                path=node.path,
                goal_state=node.state,
                nodes_expanded=expanded,
                nodes_generated=generated,
                max_frontier=max_frontier,
                elapsed_sec=time.perf_counter() - t0,
            )

        if expanded >= max_expanded:
            break

        # DFS: οι απόγονοι μπαίνουν στη στοίβα· αντιστρέφουμε ώστε
        # ο πρώτος τελεστής να εξεταστεί πρώτος (βάθος-πρώτα στα αριστερά).
        children = find_children(node.state)
        for name, child_state in reversed(children):
            child_key = child_state.canonical_key()
            if child_key in closed:
                continue
            generated += 1
            frontier.append(
                SearchNode(
                    state=child_state,
                    path=node.path + (name,),
                    depth=node.depth + 1,
                )
            )

    return SearchResult(
        method="DFS",
        success=False,
        nodes_expanded=expanded,
        nodes_generated=generated,
        max_frontier=max_frontier,
        elapsed_sec=time.perf_counter() - t0,
        message="Δεν βρέθηκε λύση εντός ορίου επέκτασης κόμβων"
        if expanded >= max_expanded
        else "Εξαντλήθηκε ο χώρος καταστάσεων χωρίς λύση",
    )


def bfs(
    start: State,
    *,
    monitor_frontier: bool = False,
    max_expanded: int = 200_000,
) -> SearchResult:
    """
    Πρώτα σε πλάτος αναζήτηση (BFS) με κλειστό σύνολο και ουρά μετώπου.
    """
    t0 = time.perf_counter()
    frontier: Deque[SearchNode] = deque([SearchNode(start)])
    closed: Set[tuple] = {start.canonical_key()}
    expanded = 0
    generated = 0
    max_frontier = 1

    while frontier:
        max_frontier = max(max_frontier, len(frontier))
        if monitor_frontier:
            _print_frontier(
                "Μέτωπο BFS (ουρά μονοπατιών)",
                [n.path_label() for n in frontier],
                expanded,
            )

        node = frontier.popleft()  # FIFO
        expanded += 1

        if is_goal_state(node.state):
            return SearchResult(
                method="BFS",
                success=True,
                path=node.path,
                goal_state=node.state,
                nodes_expanded=expanded,
                nodes_generated=generated,
                max_frontier=max_frontier,
                elapsed_sec=time.perf_counter() - t0,
            )

        if expanded >= max_expanded:
            break

        for name, child_state in find_children(node.state):
            child_key = child_state.canonical_key()
            if child_key in closed:
                continue
            closed.add(child_key)
            generated += 1
            frontier.append(
                SearchNode(
                    state=child_state,
                    path=node.path + (name,),
                    depth=node.depth + 1,
                )
            )

    return SearchResult(
        method="BFS",
        success=False,
        nodes_expanded=expanded,
        nodes_generated=generated,
        max_frontier=max_frontier,
        elapsed_sec=time.perf_counter() - t0,
        message="Δεν βρέθηκε λύση εντός ορίου επέκτασης κόμβων"
        if expanded >= max_expanded
        else "Εξαντλήθηκε ο χώρος καταστάσεων χωρίς λύση",
    )


@dataclass(order=True)
class _PQItem:
    priority: float
    seq: int
    node: SearchNode = field(compare=False)


def best_first_search(
    start: State,
    *,
    h: Callable[[State], float] = heuristic,
    monitor_frontier: bool = False,
    max_expanded: int = 200_000,
) -> SearchResult:
    """
    Ευριστική αναζήτηση Best-First: επεκτείνεται πρώτα ο κόμβος με
    μικρότερη τιμή h(n).
    """
    t0 = time.perf_counter()
    seq = 0
    start_node = SearchNode(start)
    frontier: List[_PQItem] = [_PQItem(h(start), seq, start_node)]
    closed: Set[tuple] = set()
    expanded = 0
    generated = 0
    max_frontier = 1

    while frontier:
        max_frontier = max(max_frontier, len(frontier))
        if monitor_frontier:
            ordered = sorted(frontier)
            _print_frontier(
                "Μέτωπο Best-First (κατά h)",
                [f"h={item.priority:.2f} | {item.node.path_label()}" for item in ordered],
                expanded,
            )

        item = heapq.heappop(frontier)
        node = item.node
        key = node.state.canonical_key()
        if key in closed:
            continue
        closed.add(key)
        expanded += 1

        if is_goal_state(node.state):
            return SearchResult(
                method="Best-First (ευριστική)",
                success=True,
                path=node.path,
                goal_state=node.state,
                nodes_expanded=expanded,
                nodes_generated=generated,
                max_frontier=max_frontier,
                elapsed_sec=time.perf_counter() - t0,
            )

        if expanded >= max_expanded:
            break

        for name, child_state in find_children(node.state):
            child_key = child_state.canonical_key()
            if child_key in closed:
                continue
            generated += 1
            seq += 1
            child_node = SearchNode(
                state=child_state,
                path=node.path + (name,),
                depth=node.depth + 1,
            )
            heapq.heappush(frontier, _PQItem(h(child_state), seq, child_node))

    return SearchResult(
        method="Best-First (ευριστική)",
        success=False,
        nodes_expanded=expanded,
        nodes_generated=generated,
        max_frontier=max_frontier,
        elapsed_sec=time.perf_counter() - t0,
        message="Δεν βρέθηκε λύση εντός ορίου επέκτασης κόμβων"
        if expanded >= max_expanded
        else "Εξαντλήθηκε ο χώρος καταστάσεων χωρίς λύση",
    )


METHODS = {
    "dfs": dfs,
    "bfs": bfs,
    "heuristic": best_first_search,
    "best_first": best_first_search,
}
