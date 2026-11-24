"""
Ευριστική συνάρτηση για Best-First Search.

h(n) εκτιμά το «κόστος» που απομένει μέχρι τον στόχο:
  - Κάθε δέμα που παραμένει στα ράφια χρειάζεται τουλάχιστον μία μελλοντική
    ενέργεια φόρτωσης.
  - Αν υπάρχει cargo, χρειάζεται τουλάχιστον μία εκφόρτωση.
  - Προστίθεται μικρό κόστος απόστασης από την είσοδο όταν υπάρχει cargo
    (ώστε να προτιμάται η επιστροφή για παράδοση).

Η συνάρτηση είναι αποδεκτή ως αδρή εκτίμηση (δεν υπερεκτιμά δραματικά)
και καθοδηγεί την ευριστική αναζήτηση προς καταστάσεις με λιγότερα
εκκρεμή δέματα.
"""

from __future__ import annotations

from .state import State


def heuristic(state: State) -> float:
    """
    Ευριστική τιμή h(n) για την κατάσταση.

    Μικρότερη τιμή = πιο υποσχόμενη κατάσταση για επέκταση.
    """
    remaining = state.packages_on_shelves()
    cargo_penalty = 1.0 if state.cargo else 0.0
    # Αν έχει cargo, ενθάρρυνση επιστροφής προς την είσοδο
    distance_penalty = float(state.robot_pos) if state.cargo else 0.0
    # Εκτίμηση ελάχιστων διαδρομών: κάθε «φορτίο» ≤3 δέματα
    min_trips = (remaining + 2) // 3  # ceil(remaining/3) όταν remaining>0
    if remaining == 0:
        min_trips = 0

    return float(remaining) + cargo_penalty + 0.1 * distance_penalty + float(min_trips)
