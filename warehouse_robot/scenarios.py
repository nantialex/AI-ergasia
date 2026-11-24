"""
Διαφορετικές έγκυρες αρχικές καταστάσεις για συγκριτικούς ελέγχους.
"""

from __future__ import annotations

from .state import State, make_state, INITIAL_STATE


def scenario_assignment() -> State:
    """Αρχική κατάσταση της εκφώνησης (12 δέματα)."""
    return INITIAL_STATE


def scenario_small() -> State:
    """Μικρό στιγμιότυπο — γρήγορος έλεγχος και των τριών μεθόδων."""
    return make_state(
        shelves=(
            (5, 4),
            (8,),
            (),
            (),
            (),
        )
    )


def scenario_medium() -> State:
    """Μεσαίο στιγμιότυπο με περισσότερες θέσεις."""
    return make_state(
        shelves=(
            (10, 6),
            (7, 5),
            (9, 3),
            (4,),
            (),
        )
    )


def scenario_tight_weight() -> State:
    """
    Περιοριστικό βάρος: βαριά δέματα που αναγκάζουν συχνές επιστροφές.
    """
    return make_state(
        shelves=(
            (12, 12),
            (15, 5),
            (10, 10),
            (),
            (),
        )
    )


SCENARIOS = {
    "assignment": scenario_assignment,
    "small": scenario_small,
    "medium": scenario_medium,
    "tight": scenario_tight_weight,
}
