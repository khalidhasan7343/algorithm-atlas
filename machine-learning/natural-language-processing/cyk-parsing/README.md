# CYK Parsing

## 1. Algorithm Name

CYK Parsing. Cocke–Younger–Kasami (CYK) parsing recognizes a token string under an explicit Chomsky Normal Form grammar and reconstructs one deterministic parse witness.

## 2. Overview

CYK fills a bottom-up substring chart. Each cell records exactly the nonterminals deriving that substring. Recognition and parse reconstruction require no probabilistic scores or training data.

## 3. Problem Statement

CYKParser(start,productions) takes1..128 rules (lhs,tuple(rhs)),at most32 nonterminals. A one-symbol RHS is a literal terminal outside the nonterminal set;two-symbol RHS contains two defined nonterminals. Only the start may have an empty RHS,and then start must be absent from every RHS. Nonterminals are exactly the symbols appearing on a left-hand side; capitalization is not a classification rule. No unit,ternary,mixed binary or arbitrary CFG conversion. Inputs are list/tuple0..32 nonempty literal token strings,each<=128 code points. Start/lhs names<=32 code points.

recognize(tokens) returns bool;parse returns a frozen ParseTree or None. to_tuple gives a serializable nested tree;chart returns an owned mapping of half-open spans(i,j) to frozenset nonterminals. Empty input is recognized exactly when allowed start epsilon exists. Unknown terminals simply fail recognition. Ambiguity returns one deterministic tree,not all parses.

## 4. Why Do We Need This Algorithm?

A long CNF derivation consists of two shorter derivations. Saving which categories derive every substring prevents repeated exponential rediscovery. First valid backpointers preserve a complete witness without storing every ambiguous parse. Every recognized string has a reconstructible checked witness. Exact set membership and grammar rules are inspectable,and the independent leftmost-derivation oracle shares no chart/span recurrence.

## 5. Real-World Applications

Grammar membership checking, compiler/language teaching and reconstructing syntactic analyses under an explicit small CNF grammar.

## 6. Core Intuition

For token w_i,put A in C[i,i+1] iff A->w_i. For j-i>=2,put A in C[i,j] iff some split i<k<j and binary A->BC have B in C[i,k] and C in C[k,j]. Induct on span length:base terminal membership is exact;every binary witness concatenates two valid shorter derivations,and every CNF parse decomposes at such a split. Accept iff start belongs to C[0,n],with the separate empty-start rule.

A long CNF derivation consists of two shorter derivations. Saving which categories derive every substring prevents repeated exponential rediscovery. First valid backpointers preserve a complete witness without storing every ambiguous parse.

## 7. Prerequisites

Prerequisites: Python collections/NumPy arrays, counting, basic probability/logarithms where applicable, and training/query separation. Prerequisites are context-free productions,nonterminals versus literal terminals,half-open indices,dynamic programming and inductive correctness. This formal token parser compares literal Unicode strings exactly;it does not casefold or segment natural-language input silently.

## 8. Step-by-Step Working Process

Validate and canonicalize grammar rules. Build all nonempty chart cells. Fill terminal cells,then increase span length;for each cell inspect increasing split positions and sorted binary rules. Record the first witness for each nonterminal. Follow witnesses recursively only after start recognition. Tree depth is at most n under nonempty CNF;epsilon is handled separately.

## 9. Pseudocode

```text
for i,token in input:
    C[i,i+1] <- matching terminal nonterminals
for length from2 to n:
    for start i and end j=i+length:
        for split k in i+1..j-1:
            for A->B C:
                if B in chart[i,k] and C in chart[k,j]:
                    add A and first backpointer
return start in chart[0,n]
```

## 10. Dry Run

Grammar S->AC,C->AB,A->a,B->b parses a a b. Terminal cells are A,A,B. Cell[1,3] contains C because A derives the second a and B derives b. Cell[0,3] contains S through split1. Tree is(S,(A,a),(C,(A,a),(B,b))). The actual example prints every chart cell,including empty ones.

## 11. Time Complexity

Let n be token length,R_t terminal rules,R_b binary rules,K nonterminals. Initialization O(n²+nR_t);binary pass O(n³R_b) under average O(1) set lookup,with the same loop worst case for unproductive grammars. Set-hash pathological costs are implementation-dependent. Tree construction O(n);validation/sorting O(R log R). There is no training/optimizer factor.

## 12. Space Complexity

Chart sets/backpointers cost O(n²K),including at most one witness per cell/nonterminal. Rules use O(R),output tree O(n),recursion stack O(n<=32). Unknown tokens allocate bounded empty cells;no unbounded grammar expansion occurs in production.

## 13. Python Implementation

The [Python/NumPy implementation](python/solution.py) uses the stated mechanism directly. Read the [independent tests](tests/test_python.py) and [executed example](python/example.py). Text validation and fitted vocabulary conventions are in [B13 contracts](../../../docs/natural-language-processing-conventions.md). No complete NLP estimator is called.

## 14. C++ Implementation

C++ is optional for ML and is not implemented here. No placeholder source or test pass is claimed. Existing DSA C++17/C++20 requirements remain mandatory.

## 15. Input and Output Examples

From repository root:

```sh
.venv/bin/python machine-learning/natural-language-processing/cyk-parsing/python/example.py
.venv/bin/python -m pytest machine-learning/natural-language-processing/cyk-parsing -q
```

Actual output:

```json
{"start": "S", "rules": [["S", ["A", "C"]], ["C", ["A", "B"]], ["A", ["a"]], ["B", ["b"]]], "tokens": ["a", "a", "b"], "recognized": true, "tree": ["S", ["A", "a"], ["C", ["A", "a"], ["B", "b"]]], "chart": {"(0, 1)": ["A"], "(0, 2)": [], "(0, 3)": ["S"], "(1, 2)": ["A"], "(1, 3)": ["C"], "(2, 3)": ["B"]}, "unknown": false}
```

## 16. Edge Cases

Single/two/three-token,ambiguous,unparseable,unknown-terminal,Unicode literal,empty-start and unproductive recursive grammars are covered. Invalid CNF,undefined binary symbols,epsilon on non-start,start-epsilon RHS recursion,oversized grammars/tokens and malformed inputs fail explicitly. Grammar ordering/duplicates cannot change the selected witness.

## 17. Advantages

Every recognized string has a reconstructible checked witness. Exact set membership and grammar rules are inspectable,and the independent leftmost-derivation oracle shares no chart/span recurrence.

## 18. Disadvantages and Limitations

Requires the declared CNF representation;no grammar conversion,probabilities,semantic actions or all-parse forest. Cubic n and grammar factors limit large sentences. Literal tokens are case-sensitive and explicit;epsilon is restricted. Dense cells and first-witness backpointers trade completeness of ambiguity output for bounded storage.

## 19. When to Use It

Use for teaching exact CFG membership,dynamic-programming span invariants and one transparent parse of small explicitly CNF grammars.

## 20. When Not to Use It

Avoid arbitrary CFG input,large ambiguous parse forests,semantic parsing or probability-ranked parsing without an explicitly extended algorithm. A statistical sequence tagger solves a different problem.

## 21. Comparison With Related Algorithms

CYK derives hierarchical grammar spans;HMM/CRF decode linear token labels. Top-down derivation enumeration is exponential but serves as an independent tiny-case oracle. Earley parsing accepts broader CFG forms but is outside this implemented scope.

## 22. Interview Questions

Why increasing span length? Every binary child is shorter. Why forbid unit rules? They break the stated strictly shorter-child recurrence without closure. Why forbid start on RHS when epsilon is present? Nonempty chart children assume positive lengths. Does ambiguity mean nondeterminism? Rules/splits are ordered and return one fixed witness.

## 23. Practice Problems

Hand-fill a four-token chart;construct two distinct parses of a a a under S->SS|a;validate tree yields independently;add a terminal not in the grammar;prove a CNF n-terminal tree uses2n-1 production expansions. Extend the independent leftmost BFS to enumerate all a/b strings up to length4 without calling the production chart.

## 24. References

[University of Nevada Las Vegas, The CYK Algorithm](https://web.cs.unlv.edu/larmore/Courses/CSC456/cyk.html). The local exact grammar schema,start-only epsilon policy,resource bounds and deterministic tree convention are declared educational choices. Independent tests use BFS leftmost derivations bounded by2n-1 rewrites,not the CYK recurrence.

## 25. Author Attribution

Owner and maintainer: **[MD.Khalid Hasan](https://github.com/khalidhasan7343)**. [Algorithm Atlas](https://github.com/khalidhasan7343/algorithm-atlas); [MIT license](../../../LICENSE); [contributing](../../../CONTRIBUTING.md).

