#include "minisat/core/Solver.h"

using namespace Minisat;

inline Lit itoLit(int i) {
    bool sign = i < 0;
    int var = (sign) ? -i-1 : i-1; // 0-based variable numbering
    return (sign) ? ~mkLit(var) : mkLit(var);
}

inline int Littoi(Lit l) {
    return (var(l)+1) * (sign(l) ? -1 : 1);
}

extern "C" {
    Solver* Solver_new() { return new Solver(); }
    void Solver_delete(Solver* s) { delete s; }

    int nVars(Solver* s) { return s->nVars(); }
    int nClauses(Solver* s) { return s->nClauses(); }

    // Controls the level of phase saving (0=none, 1=limited, 2=full).
    void setPhaseSaving(Solver* s, int ps) { s->phase_saving = ps; }

    // Control whether random polarities are used (overridden if vars are created with a user polarity other than Undef)
    void setRndPol(Solver* s, bool val) { s->rnd_pol = val; }

    // polarity: 0=False, 1=True, 2=Undef
    int newVar(Solver* s, uint8_t polarity, bool dvar=true) { return s->newVar(lbool(polarity), dvar); }

    bool addClause(Solver* s, int len, int* lits) {
        vec<Lit> clause;
        for (int i = 0 ; i < len ; i++) {
            clause.push( itoLit(lits[i]) );
        }
        return s->addClause(clause);
    }
    bool addUnit(Solver* s, int lit) {
        return s->addClause(itoLit(lit));
    }

    bool solve(Solver* s) { return s->solve(); }
    bool solve_assumptions(Solver* s, int len, int* lits) {
        vec<Lit> assumptions;
        for (int i = 0 ; i < len ; i++) {
            assumptions.push( itoLit(lits[i]) );
        }
        return s->solve(assumptions);
    }

    bool simplify(Solver* s) { return s->simplify(); }

    // This is fairly slow to call from Python.
    // It is better to copy the whole model over with fillModel()
    // if you will be looking at most or all values, anyway.
    int modelValue(Solver* s, int i) { return s->modelValue(i-1) != l_False; }

    void fillModel(Solver* s, int* model, int from, int to) {
        for (int i = from ; i < to ; i++) {
            model[i-from] = s->modelValue(i) != l_False;
        }
    }

    int getModelTrues(Solver* s, int* trues, int from, int to) {
        int count = 0;
        for (int i = from ; i < to ; i++) {
            if (s->modelValue(i) == l_True) trues[count++] = i-from;
        }
        return count;
    }

    // returns a core with 0-based counting
    // (i.e., first clause is 0, etc.)
    // (subtracts given number of original variables from conflict variables)
    int unsatCore(Solver* s, int nv, int* core) {
        for (int i = 0 ; i < s->conflict.size() ; i++) {
            core[i] = var(s->conflict[i]) - nv;
        }
        return s->conflict.size();
    }

    // fills an array w/ any literals known to be implied by the current formula
    // (i.e., all 0-level assignments)
    // returns number of elements in the filled array
    int getImplies(Solver* s, int* assigns) {
        vec<Lit> empty;
        vec<Lit> outvec;
        s->implies(empty, outvec, true);
        int len = outvec.size();
        for (int i = 0 ; i < len ; i++) {
            assigns[i] = Littoi(outvec[i]);
        }
        return len;
    }
}
