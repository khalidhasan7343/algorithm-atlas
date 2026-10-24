# Number Theory contracts — Phase 11

Python uses native int only (bool is invalid). C++ uses int64_t; no nonstandard
128-bit extension is required. Both languages enforce the same finite domains.
Public operations do not mutate arguments. Contract/overflow failures raise
ValueError in Python or std::invalid_argument in C++; CLI errors exit 2 with
`error:` on stderr and no partial result. Inputs are decimal tokens, optional
+/-, ASCII digits, at most 20 characters per token; exact arity is enforced.

| Operation | Supported inputs | Result |
| --- | --- | --- |
| Sieve | integer limit 0..1000000, inclusive | ascending primes ≤limit; [] below 2 |
| Euclidean GCD | a,b each -10^9..10^9 | nonnegative gcd; gcd(0,0)=0 |
| LCM | same a,b | nonnegative; zero if either input is zero |
| Extended Euclid | same a,b | [g,x,y], a*x+b*y=g≥0; (0,0) gives [0,0,0] |
| Modular power | base -10^9..10^9, exponent 0..10^9, modulus 1..1000000007 | least nonnegative residue |
| Fast power | base -10^9..10^9, exponent 0..10^9 | exact signed-64 result; reject overflow |
| Factorization | n in 1..10^12 | ascending [prime,exponent] rows; 1 gives [] |

GCD reduces nonnegative magnitudes. LCM reuses the canonical Euclidean routine,
divides before multiplication and is at most 10^18. Extended Euclid runs on
magnitudes, then adjusts coefficients to original signs; coefficients are
deterministic for this recurrence, with no minimal-coefficient promise. Tests
check Bézout semantically rather than requiring one arbitrary valid pair.
With input magnitudes ≤10^9, conservative intermediate coefficient products and
the final identity verification fit signed 64-bit arithmetic.

Powers use repeated squaring, with 0^0=1 for exact power and 1 modulo m for
modular power. Modulus 1 always gives zero. Negative exponents are rejected;
no modular inverse or coprimality requirement is implied. Negative bases are
normalized before modular multiplication. Each reduced product is at most
(1000000006)^2, below INT64_MAX. Fast power detects overflow before C++ signed
multiplication using unsigned magnitudes and sign-specific limits; INT64_MIN
is a valid result. It avoids an unnecessary final square that could overflow
even when the requested result fits. Python explicitly enforces the same range.

Factorization is deterministic trial division, not a probabilistic primality
test. Zero and negative n are rejected. Edges test d≤remaining/d instead of an
overflow-prone square. The 10^12 bound keeps worst-case trial work finite; this
is not a large cryptographic-integer factorization API. Sieve uses O(limit)
marking bytes plus returned primes; factorization returns prime powers only.

CLI arity: sieve/factorization one token; gcd/lcm/extended/power two tokens;
modular power three tokens. All outputs are compact JSON, including scalar
integers. See [scope](number-theory-window-scope.md) for exact IDs and ownership.
