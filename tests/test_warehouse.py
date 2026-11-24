"""Βασικοί έλεγχοι λειτουργίας για τελεστές και αλγορίθμους αναζήτησης."""

from __future__ import annotations

import unittest

from warehouse_robot.operators import find_children, load, move_right, unload
from warehouse_robot.scenarios import scenario_medium, scenario_small
from warehouse_robot.search import best_first_search, bfs, dfs
from warehouse_robot.state import INITIAL_STATE, is_goal_state, make_state


class TestStateAndGoal(unittest.TestCase):
    def test_initial_not_goal(self):
        self.assertFalse(is_goal_state(INITIAL_STATE))
        self.assertEqual(INITIAL_STATE.packages_on_shelves(), 12)

    def test_goal_detection(self):
        goal = make_state(
            shelves=((), (), (), (), ()),
            entrance=(5, 4, 8),
        )
        self.assertTrue(is_goal_state(goal))


class TestOperators(unittest.TestCase):
    def test_move_and_load(self):
        s0 = scenario_small()
        s1 = move_right(s0)
        self.assertIsNotNone(s1)
        assert s1 is not None
        self.assertEqual(s1.robot_pos, 1)
        s2 = load(s1)
        self.assertIsNotNone(s2)
        assert s2 is not None
        self.assertEqual(s2.cargo, (5,))
        self.assertEqual(s2.shelves[0], (4,))

    def test_find_children_from_start(self):
        children = find_children(scenario_small())
        names = [n for n, _ in children]
        self.assertIn("move_right", names)
        self.assertNotIn("move_left", names)
        self.assertNotIn("load", names)

    def test_unload_at_entrance(self):
        s = make_state(
            shelves=((), (), (), (), ()),
            robot_pos=0,
            cargo=(5, 4),
            entrance=(),
        )
        u = unload(s)
        self.assertIsNotNone(u)
        assert u is not None
        self.assertEqual(u.cargo, ())
        self.assertEqual(u.entrance, (5, 4))
        self.assertTrue(is_goal_state(u))


class TestSearch(unittest.TestCase):
    def test_all_methods_solve_small(self):
        start = scenario_small()
        for solver in (dfs, bfs, best_first_search):
            result = solver(start, max_expanded=50_000)
            self.assertTrue(result.success, solver.__name__)
            self.assertTrue(is_goal_state(result.goal_state))
            self.assertGreater(len(result.path), 0)

    def test_bfs_path_not_longer_than_dfs_on_small(self):
        start = scenario_small()
        r_bfs = bfs(start, max_expanded=50_000)
        r_dfs = dfs(start, max_expanded=50_000)
        self.assertTrue(r_bfs.success and r_dfs.success)
        self.assertLessEqual(len(r_bfs.path), len(r_dfs.path))

    def test_medium_heuristic(self):
        result = best_first_search(scenario_medium(), max_expanded=100_000)
        self.assertTrue(result.success)
        self.assertTrue(is_goal_state(result.goal_state))


if __name__ == "__main__":
    unittest.main()
