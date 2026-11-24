"""
Τελεστές μετάβασης και συνάρτηση εύρεσης απογόνων (find_children / findchildren).

Τελεστές:
  1. move_left          — μετακίνηση κατά μία θέση προς την είσοδο
  2. move_right         — μετακίνηση κατά μία θέση βαθύτερα στην αποθήκη
  3. load               — φόρτωση του επόμενου δέματος της τρέχουσας θέσης
                          (αν δεν παραβιάζονται οι περιορισμοί)
  4. return_and_unload  — όταν δεν μπορεί να φορτωθεί το επόμενο δέμα λόγω
                          περιορισμών (ή το cargo είναι γεμάτο), επιστροφή
                          στην είσοδο και εκφόρτωση σε ΜΙΑ ενέργεια
  5. unload             — εκφόρτωση στην είσοδο (όταν το ρομπότ βρίσκεται εκεί)

Κάθε τελεστής επιστρέφει νέα State ή None αν δεν εφαρμόζεται.
"""

from __future__ import annotations

from typing import Callable, List, Optional, Tuple

from .state import ENTRANCE, NUM_SHELVES, State

# Τύπος τελεστή: State -> Optional[State]
Operator = Callable[[State], Optional[State]]


def move_left(state: State) -> Optional[State]:
    """Μετακίνηση κατά μία θέση προς τα αριστερά (προς την είσοδο), αν υπάρχει."""
    if state.robot_pos <= ENTRANCE:
        return None
    return State(
        robot_pos=state.robot_pos - 1,
        cargo=state.cargo,
        shelves=state.shelves,
        entrance=state.entrance,
    )


def move_right(state: State) -> Optional[State]:
    """Μετακίνηση κατά μία θέση προς τα δεξιά, αν υπάρχει η θέση."""
    if state.robot_pos >= NUM_SHELVES:
        return None
    return State(
        robot_pos=state.robot_pos + 1,
        cargo=state.cargo,
        shelves=state.shelves,
        entrance=state.entrance,
    )


def load(state: State) -> Optional[State]:
    """
    Φόρτωση του πρώτου δέματος της τρέχουσας θέσης, εφόσον:
      - το ρομπότ δεν είναι στην είσοδο
      - η θέση έχει δέματα
      - το δέμα δεν παραβιάζει τους περιορισμούς (≤3 δέματα, ≤20kg)
    """
    pos = state.robot_pos
    if pos == ENTRANCE:
        return None

    shelf_index = pos - 1
    shelf = state.shelves[shelf_index]
    if not shelf:
        return None

    weight = shelf[0]
    if not state.can_accept(weight):
        return None

    # Αφαίρεση από το ράφι, προσθήκη στο cargo
    new_shelf = shelf[1:]
    new_shelves = (
        state.shelves[:shelf_index] + (new_shelf,) + state.shelves[shelf_index + 1 :]
    )
    new_cargo = state.cargo + (weight,)

    return State(
        robot_pos=state.robot_pos,
        cargo=new_cargo,
        shelves=new_shelves,  # type: ignore[arg-type]
        entrance=state.entrance,
    )


def _cannot_load_next(state: State) -> bool:
    """
    True όταν στη θέση υπάρχει δέμα που ΔΕΝ χωράει στο cargo,
    ή όταν το cargo έχει ήδη 3 δέματα και παραμένουν δέματα στη θέση.
    (Συνθήκη για αυτόματη επιστροφή-εκφόρτωση σύμφωνα με την εκφώνηση.)
    """
    pos = state.robot_pos
    if pos == ENTRANCE:
        return False
    shelf = state.shelves[pos - 1]
    if not shelf:
        return False
    return not state.can_accept(shelf[0])


def return_and_unload(state: State) -> Optional[State]:
    """
    Επιστροφή στην είσοδο και εκφόρτωση σε μία ενέργεια.

    Εφαρμόζεται όταν το ρομπότ είναι σε θέση αποθήκευσης, έχει δέματα
    στο cargo και παραβιάζεται ο περιορισμός χωρητικότητας για το
    επόμενο δέμα της θέσης (όπως περιγράφει η εκφώνηση).
    """
    if state.robot_pos == ENTRANCE:
        return None
    if not state.cargo:
        return None
    if not _cannot_load_next(state):
        return None

    return State(
        robot_pos=ENTRANCE,
        cargo=(),
        shelves=state.shelves,
        entrance=state.entrance + state.cargo,
    )


def unload(state: State) -> Optional[State]:
    """
    Εκφόρτωση όλων των δεμάτων του cargo στην είσοδο.
    Εφαρμόζεται μόνο όταν το ρομπότ βρίσκεται στην είσοδο και έχει cargo.
    """
    if state.robot_pos != ENTRANCE:
        return None
    if not state.cargo:
        return None

    return State(
        robot_pos=ENTRANCE,
        cargo=(),
        shelves=state.shelves,
        entrance=state.entrance + state.cargo,
    )


# Λίστα τελεστών με ονόματα (για εκτύπωση μονοπατιού / δένδρου)
OPERATORS: List[Tuple[str, Operator]] = [
    ("move_left", move_left),
    ("move_right", move_right),
    ("load", load),
    ("return_and_unload", return_and_unload),
    ("unload", unload),
]


def find_children(state: State) -> List[Tuple[str, State]]:
    """
    Συνάρτηση εύρεσης απογόνων (findchildren).

    Εφαρμόζει όλους τους τελεστές μετάβασης στην τρέχουσα κατάσταση
    και επιστρέφει λίστα ζευγών (όνομα_τελεστή, νέα_κατάσταση) για
    όσους τελεστές είναι εφαρμόσιμοι.
    """
    children: List[Tuple[str, State]] = []
    for name, operator in OPERATORS:
        child = operator(state)
        if child is not None:
            children.append((name, child))
    return children


# Συνώνυμο όπως στην εκφώνηση
findchildren = find_children
