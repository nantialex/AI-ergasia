"""
Αναπαράσταση κόσμου, αρχικής/τελικής κατάστασης και βοηθητικές συναρτήσεις.

Ο κόσμος:
  - Είσοδος (θέση 0) και πέντε διαδοχικές θέσεις αποθήκευσης (1..5).
  - Σε κάθε θέση υπάρχει ουρά δεμάτων (βάρη σε kg). Το πρώτο στοιχείο
    της ουράς εξετάζεται πρώτο από το ρομπότ.
  - Το ρομπότ έχει θέση, χώρο μεταφοράς (cargo) και η είσοδος συγκεντρώνει
    τα παραδοθέντα δέματα.

Περιορισμοί χώρου μεταφοράς:
  - το πολύ 3 δέματα
  - συνολικό βάρος ≤ 20 kg
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

# Μέγιστος αριθμός δεμάτων και μέγιστο βάρος στο cargo του ρομπότ
MAX_PACKAGES = 3
MAX_WEIGHT = 20

# Θέσεις: 0 = είσοδος, 1..5 = θέσεις αποθήκευσης
ENTRANCE = 0
NUM_SHELVES = 5


Package = int
Shelf = Tuple[Package, ...]
Shelves = Tuple[Shelf, Shelf, Shelf, Shelf, Shelf]
Cargo = Tuple[Package, ...]


@dataclass(frozen=True)
class State:
    """
    Κατάσταση του προβλήματος (αμετάβλητη / hashable για κλειστό σύνολο).

    Attributes:
        robot_pos: θέση ρομπότ (0=είσοδος, 1..5=ράφια)
        cargo: δέματα που μεταφέρει αυτή τη στιγμή
        shelves: περιεχόμενα των 5 θέσεων (ουρές δεμάτων)
        entrance: δέματα που έχουν ήδη εκφορτωθεί στην είσοδο
    """

    robot_pos: int
    cargo: Cargo
    shelves: Shelves
    entrance: Cargo

    def cargo_weight(self) -> int:
        """Συνολικό βάρος των δεμάτων στο cargo."""
        return sum(self.cargo)

    def can_accept(self, weight: Package) -> bool:
        """Ελέγχει αν ένα δέμα μπορεί να φορτωθεί χωρίς παραβίαση περιορισμών."""
        return (
            len(self.cargo) < MAX_PACKAGES
            and self.cargo_weight() + weight <= MAX_WEIGHT
        )

    def packages_on_shelves(self) -> int:
        """Πλήθος δεμάτων που απομένουν στις θέσεις αποθήκευσης."""
        return sum(len(shelf) for shelf in self.shelves)

    def total_packages(self) -> int:
        """Συνολικό πλήθος δεμάτων στον κόσμο (ράφια + cargo + είσοδος)."""
        return self.packages_on_shelves() + len(self.cargo) + len(self.entrance)

    def canonical_key(self) -> tuple:
        """
        Κανονική μορφή για το κλειστό σύνολο.
        Η σειρά στην είσοδο δεν επηρεάζει τη συνέχεια της αναζήτησης,
        ούτε η εσωτερική σειρά του cargo (μετράνε πλήθος και βάρη).
        """
        return (
            self.robot_pos,
            tuple(sorted(self.cargo)),
            self.shelves,
            tuple(sorted(self.entrance)),
        )

    def pretty(self) -> str:
        """Αναγνώσιμη περιγραφή κατάστασης για εκτύπωση / screenshots."""
        cargo_s = list(self.cargo) if self.cargo else "—"
        ent_s = list(self.entrance) if self.entrance else "—"
        lines = [
            f"Ρομπότ@{'Είσοδος' if self.robot_pos == 0 else f'Θέση {self.robot_pos}'} "
            f"| cargo={cargo_s} ({self.cargo_weight()}kg)",
            f"Είσοδος: {ent_s}",
        ]
        for i, shelf in enumerate(self.shelves, start=1):
            lines.append(f"Θέση {i}: {list(shelf) if shelf else '—'}")
        return "\n".join(lines)


def make_state(
    shelves: Shelves,
    robot_pos: int = ENTRANCE,
    cargo: Cargo = (),
    entrance: Cargo = (),
) -> State:
    """Δημιουργία κατάστασης με έλεγχο βασικής εγκυρότητας."""
    if not (ENTRANCE <= robot_pos <= NUM_SHELVES):
        raise ValueError(f"Μη έγκυρη θέση ρομπότ: {robot_pos}")
    if len(shelves) != NUM_SHELVES:
        raise ValueError("Απαιτούνται ακριβώς 5 θέσεις αποθήκευσης")
    if len(cargo) > MAX_PACKAGES or sum(cargo) > MAX_WEIGHT:
        raise ValueError("Μη έγκυρο αρχικό cargo")
    return State(
        robot_pos=robot_pos,
        cargo=tuple(cargo),
        shelves=tuple(tuple(s) for s in shelves),  # type: ignore[arg-type]
        entrance=tuple(entrance),
    )


# Αρχική κατάσταση όπως στην εκφώνηση (σχήμα σελίδας 1)
INITIAL_STATE: State = make_state(
    shelves=(
        (12, 15),  # Θέση 1
        (8, 11),  # Θέση 2
        (3, 9, 7),  # Θέση 3
        (6, 2, 13),  # Θέση 4
        (10, 4),  # Θέση 5
    )
)


def is_goal_state(state: State) -> bool:
    """
    Τελική κατάσταση: όλα τα δέματα βρίσκονται στην είσοδο.
    Δηλαδή τα ράφια είναι άδεια και το cargo του ρομπότ είναι άδειο.
    """
    return state.packages_on_shelves() == 0 and len(state.cargo) == 0
