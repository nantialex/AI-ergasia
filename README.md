# Ρομπότ μεταφοράς δεμάτων σε αποθήκη

Απαλλακτική εργασία μαθήματος **Τεχνητή Νοημοσύνη** (UNIWA, 2026-27) — Μέρος Ι.

Αυτόνομο ρομπότ μεταφέρει δέματα από 5 θέσεις αποθήκευσης στην είσοδο, με περιορισμούς χωρητικότητας (≤3 δέματα, ≤20 kg). Η επίλυση γίνεται με **DFS**, **BFS** και **ευριστική Best-First** αναζήτηση, με τελεστές μετάβασης και συνάρτηση `find_children`.

## Απαιτήσεις

- Python 3.10+ (μόνο τυπική βιβλιοθήκη — δεν χρειάζονται επιπλέον πακέτα)

## Γρήγορη εκκίνηση

```bash
# Μικρό σενάριο με ευριστική αναζήτηση
python3 main.py --method heuristic --scenario small

# DFS / BFS με παρακολούθηση μετώπου
python3 main.py --method dfs --scenario small --monitor
python3 main.py --method bfs --scenario medium --monitor

# Πλήρες πρόβλημα εκφώνησης
python3 main.py --method heuristic --scenario assignment
python3 main.py --method bfs --scenario assignment

# Δένδρο αναζήτησης (πρώτα 4 επίπεδα)
python3 main.py --tree --scenario small

# Συγκριτική μελέτη όλων των μεθόδων / σεναρίων
python3 main.py --compare

# Unit tests
python3 -m unittest discover -s tests -v
```

## Επιλογή μεθόδου

| `--method`   | Περιγραφή                                      |
|--------------|-------------------------------------------------|
| `dfs`        | Πρώτα σε βάθος (στοίβα)                         |
| `bfs`        | Πρώτα σε πλάτος (ουρά)                          |
| `heuristic`  | Best-First με ευριστική `h(n)`                  |

| `--scenario` | Περιγραφή                                      |
|--------------|-------------------------------------------------|
| `small`      | Μικρό στιγμιότυπο (γρήγοροι έλεγχοι)            |
| `medium`     | Μεσαίο στιγμιότυπο                              |
| `tight`      | Βαριά δέματα / συχνές επιστροφές              |
| `assignment` | Αρχική κατάσταση εκφώνησης (12 δέματα)          |

## Δομή κώδικα

```
warehouse_robot/
  state.py         # κόσμος, κατάσταση, is_goal_state
  operators.py     # τελεστές + find_children
  search.py        # DFS, BFS, Best-First + παρακολούθηση μετώπου
  heuristics.py    # ευριστική h(n)
  scenarios.py     # εναλλακτικές αρχικές καταστάσεις
  tree.py          # δένδρο αναζήτησης (≤4 επίπεδα)
main.py            # CLI επιλογής μεθόδου
docs/TEKMIRIOSI.md # τεκμηρίωση ζητουμένων 1–7
NOTES.md           # παρατηρήσεις για τον αξιολογητή
tests/             # περιπτώσεις ελέγχου
```

## Τεκμηρίωση

Η αναλυτική περιγραφή κόσμου, χώρου καταστάσεων, τελεστών, δένδρων και συγκριτικής μελέτης βρίσκεται στο [`docs/TEKMIRIOSI.md`](docs/TEKMIRIOSI.md).
