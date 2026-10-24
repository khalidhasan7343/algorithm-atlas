# Two Pointers and Sliding Window contracts — Phase 12

Arrays are Python list/tuple of native int (excluding bool), or C++ vector<int64_t>.
Length≤10000; values are -10^9..10^9. Inputs are never reordered or mutated.
Python ValueError and C++ std::invalid_argument signal invalid contracts.
Executable errors exit 2, print `error:` to stderr and no partial result.

**Two Sum:** solve(values,target), sorted nondecreasing values required and
validated in O(n). Target is -2*10^9..2*10^9. Return the lexicographically
smallest zero-based [i,j], i<j, or [] if impossible. Empty/single arrays have no
pair. On equality, move across equal right-hand values to their earliest valid
position. Numeric bounds make all C++ sums safe in int64_t. CLI starts with
target, followed by array values, without a length prefix.

**Sliding Maximum:** solve(values,k). Nonempty arrays require 1≤k≤n; empty
input requires k=0 and returns []. Return one maximum value per complete
fixed-size window. Negative values are fully supported. A deque stores increasing
indices and decreasing values; equal values retain the latest representative,
which does not change value output. CLI starts with k, followed by values.
Working space is O(k), output O(n-k+1); each index enters/leaves the deque once.

**Longest Distinct Substring:** solve(text) returns the earliest longest
half-open [start,end) interval, serialized as [start,end]; empty input [0,0]. Python accepts bytes, C++
std::string; all 256 symbols are supported up to 10000 bytes. Matching is case
sensitive. Unicode callers explicitly encode UTF-8; offsets count bytes and
the interval need not align to code points or graphemes. No normalization occurs.
This follows the approved [String byte contracts](string-conventions.md).
The executable takes one even-length hex token, or - for empty, reusing the
existing String transport support. A 256-entry last-position table moves the
left boundary only forward, using max(left,last[byte]+1); earliest ties remain.

Array CLI uses signed ASCII decimal tokens, optional +/-, at most 20 characters
per token. Exact scalar-prefix presence, size and value bounds are enforced.
No in-place partitioning, fast/slow linked-list algorithm, nonnegative-only
sum window or other uncataloged topic is added. All outputs are eager compact
JSON. Allocation failure and concurrent mutation are outside this bounded
educational API. See [scope](number-theory-window-scope.md) and
[checkpoints](two-pointers-sliding-window-checkpoints.md).
