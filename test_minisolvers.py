import minisolvers
import unittest


class MinisatTest(unittest.TestCase):
    def setUp(self):
        self.solver = minisolvers.MinisatSolver()
        self.clauses = [ [1], [-2], [3, 4], [-3, 5], [-4, 6], [-5, 4], [-6] ]
        self.numvars = max([max(cl) for cl in [[abs(x) for x in cl] for cl in self.clauses]])

    def tearDown(self):
        del self.solver

    def test_newvars(self):
        for i in range(self.numvars):
            self.solver.new_var(True)
            self.assertEqual(self.solver.nvars(), i+1)

    def test_add_clause_without_vars(self):
        self.assertRaises(Exception, self.solver.add_clause, [-1, 2])

    def add_subset(self, subset):
        for i in range(self.numvars):
            self.solver.new_var()
        for cl in subset:
            self.solver.add_clause(cl)

    def test_sat(self):
        self.add_subset(self.clauses[:-1])
        self.assertEqual(self.solver.solve(), True)

    def test_unsat(self):
        self.add_subset(self.clauses)
        self.assertEqual(self.solver.solve(), False)

    def test_assumptions(self):
        self.add_subset(self.clauses[:-2])
        self.assertEqual(self.solver.solve([-5]), True)
        self.assertEqual(self.solver.solve([-6]), True)
        self.assertEqual(self.solver.solve([-5, -6]), False)

    def test_model(self):
        from math import copysign
        isPositive = lambda x: copysign(1, x) > 0
        subset = self.clauses[:-1]
        self.add_subset(subset)
        self.solver.solve()
        m = self.solver.get_model()
        self.assertEqual(len(m), self.solver.nvars())
        for cl in subset:
            self.assertTrue(any([ m[abs(x)-1] == isPositive(x) for x in cl ]))

    def test_implies(self):
        self.add_subset(self.clauses)
        self.solver.solve()
        self.assertTrue(len(self.solver.implies()) > 0)


class MinisatSubsetTest(unittest.TestCase):
    def setUp(self):
        self.solver = minisolvers.MinisatSubsetSolver()
        self.clauses = [ [1], [-2], [3, 4], [-3, 5], [-4, 6], [-5, 4], [-6] ]
        self.group = [ [1, 2, 3], [3, 4, 5] ]
        self.n = len(self.clauses) + 1  # +1 for the group
        self.numvars = max([max(cl) for cl in [[abs(x) for x in cl] for cl in self.clauses + self.group]])
        self.solver.set_varcounts(self.numvars, self.n)
        for i in range(self.numvars):
            self.solver.new_var()
        for i in range(self.n):
            self.solver.new_var()
        i = 0
        for cl in self.group:
            self.solver.add_clause_instrumented(cl, i)
        i += 1
        for cl in self.clauses:
            self.solver.add_clause_instrumented(cl, i)
            i += 1

    def tearDown(self):
        del self.solver

    def test_subsets(self):
        self.assertEqual(self.solver.solve_subset(range(self.n)), False)
        for i in range(1, self.n):
            self.assertEqual(self.solver.solve_subset(range(self.n-i)), True)


class MinicardTest(unittest.TestCase):
    def setUp(self):
        self.solver = minisolvers.MinicardSolver()
        self.atmosts = [(list(range(1, 31)), 15)]
        self.clauses = [ [15], [10], [8], [12, 5], [4, 6], [2], [1], [-1, -2, -6, -8, -10, -12, -15] ]
        self.assumptions = [-x for x in range(16, 31)]
        self.numvars = 30

    def tearDown(self):
        del self.solver

    def test_newvars(self):
        for i in range(self.numvars):
            self.solver.new_var(True)
            self.assertEqual(self.solver.nvars(), i+1)

    def test_add_clause_without_vars(self):
        self.assertRaises(Exception, self.solver.add_clause, [-1, 2])

    def make_vars(self):
        for i in range(self.numvars):
            self.solver.new_var()

    def add_subset(self, subset):
        for cl in subset:
            self.solver.add_clause(cl)

    def add_atmosts(self, atmosts):
        for atmost in atmosts:
            self.solver.add_atmost(atmost[0], atmost[1])

    def test_sat(self):
        self.make_vars()
        self.add_subset(self.clauses[:-1])
        self.assertEqual(self.solver.solve(), True)

    def test_unsat(self):
        self.make_vars()
        self.add_subset(self.clauses)
        self.solver.add_clause([-8, -10])
        self.assertEqual(self.solver.solve(), False)

    def test_assumptions(self):
        self.make_vars()
        self.add_subset(self.clauses[:-2])
        self.assertEqual(self.solver.solve([-5]), True)
        self.assertEqual(self.solver.solve([-6]), True)
        self.assertEqual(self.solver.solve([-8, -10]), False)

    def test_model(self):
        self.make_vars()
        from math import copysign
        isPositive = lambda x: copysign(1, x) > 0
        subset = self.clauses[:-1]
        self.add_subset(subset)
        self.solver.solve()
        m = self.solver.get_model()
        self.assertEqual(len(m), self.solver.nvars())
        for cl in subset:
            self.assertTrue(any([ m[abs(x)-1] == isPositive(x) for x in cl ]))

    def int_check(self):
        import random
        for i in range(1000):
            assumps = [x*random.choice([1, -1]) for x in self.assumptions]
            self.solver.solve(assumps)
            self.assertEqual(self.solver.solve(self.assumptions), True)

    def test_complete(self):
        self.make_vars()
        self.add_atmosts(self.atmosts)
        self.int_check()
        self.add_subset(self.clauses)
        self.int_check()
        self.assertEqual(self.solver.solve(self.assumptions), True)

if __name__ == '__main__':
    unittest.main()
