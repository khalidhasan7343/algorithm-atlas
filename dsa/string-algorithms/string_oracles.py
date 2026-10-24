"""Independent bounded references and reproducible vectors, never used by solutions."""
import itertools
import random

SEED = 90901


def occurrences(text, pattern):
    # Deliberately use slicing, independently of alignment/failure/hash logic.
    return [i for i in range(len(text)+1) if text[i:i+len(pattern)] == pattern]


def lps(pattern):
    return [max([0]+[k for k in range(1,i+1)
                     if pattern[:k] == pattern[i-k+1:i+1]])
            for i in range(len(pattern))]


def z_values(text):
    result = [0] * len(text)
    for i in range(1,len(text)):
        while i+result[i] < len(text) and text[result[i]] == text[i+result[i]]:
            result[i] += 1
    return result


def good_shifts(pattern):
    """Enumerate safe shifts from matched-suffix constraints, without border links."""
    m = len(pattern)
    if not m:
        return [1]
    shifts = []
    for index in range(m+1):
        for delta in range(1,m+1):
            consistent = all(t-delta < 0 or pattern[t] == pattern[t-delta]
                             for t in range(index,m))
            # The mismatching preceding byte must not be the same again.
            if index > 0 and index-1-delta >= 0:
                consistent &= pattern[index-1-delta] != pattern[index-1]
            if consistent:
                shifts.append(delta)
                break
    return shifts


def palindromes(text):
    odd, even = [], []
    for i in range(len(text)):
        a = 1
        while i-a >= 0 and i+a < len(text) and text[i-a] == text[i+a]:
            a += 1
        odd.append(a)
        b = 0
        while i-b-1 >= 0 and i+b < len(text) and text[i-b-1] == text[i+b]:
            b += 1
        even.append(b)
    best = [0,0]
    for start in range(len(text)):
        for end in range(start+1,len(text)+1):
            piece = text[start:end]
            if piece == piece[::-1] and end-start > best[1]-best[0]:
                best = [start,end]
    return [odd,even,best]


def suffixes(text):
    order = sorted(range(len(text)),key=lambda i:text[i:])
    lcp = [0] * len(order)
    for i in range(1,len(order)):
        a,b = order[i-1:i+1]
        k = 0
        while a+k<len(text) and b+k<len(text) and text[a+k]==text[b+k]:
            k += 1
        lcp[i] = k
    return order,lcp


def multi(text, patterns):
    matches = [[i+len(p),j,i] for j,p in enumerate(patterns)
               for i in occurrences(text,p)]
    return sorted(matches,key=lambda hit:(hit[0],-len(patterns[hit[1]]),hit[1]))


def matching_vectors():
    cases = [(b"",b""),(b"",b"a"),(b"a",b""),(b"a",b"a"),
             (b"a",b"aa"),(b"aaaaa",b"aaa"),(b"banana",b"ana"),
             (b"ababababac",b"ababac"),(b"mississippi",b"issi"),
             (bytes(range(256))*2,bytes([255,0])),
             (b"\x00#$\xff\x00#$\xff",b"\x00#$"),
             ("ééবাংলা🙂é".encode(),"é".encode()),
             (b"AbA aBA",b"a"),(b"a\n\tb",b"\n\t")]
    words = [bytes(w) for n in range(5) for w in itertools.product(b"ab",repeat=n)]
    patterns = [bytes(w) for n in range(4) for w in itertools.product(b"ab",repeat=n)]
    cases.extend(itertools.product(words,patterns))
    rng = random.Random(SEED)
    for _ in range(160):
        alphabet = rng.choice([b"ab",b"abc#$\x00\xff",bytes(range(256))])
        text = bytes(rng.choice(alphabet) for _ in range(rng.randrange(61)))
        if rng.randrange(2) and text:
            a = rng.randrange(len(text)+1)
            pattern = text[a:a+rng.randrange(17)]
        else:
            pattern = bytes(rng.choice(alphabet) for _ in range(rng.randrange(17)))
        cases.append((text,pattern))
    for n in range(1,41):
        cases.append((b"a"*n+b"b",b"a"*(n//2)+b"b"))
    return cases


def palindrome_vectors():
    return list(dict.fromkeys(t for t,_ in matching_vectors()))


def multi_vectors():
    cases = [(b"",[]),(b"",[b"",b""]),(b"ushers",[b"he",b"she",b"his",b"hers"]),
             (b"aaaa",[b"a",b"aa",b"aaa",b"",b"aa",b""]),
             (b"ababa",[b"a",b"ba",b"aba",b"baba"]),
             ("éé🙂".encode(),["é".encode(),"🙂".encode(),b""]),
             (bytes(range(256))*2,[bytes([255,0]),b"\x00",b"\xff",b"#$"])]
    rng = random.Random(SEED+3)
    for _ in range(160):
        text = bytes(rng.choice(b"abc\x00\xff") for _ in range(rng.randrange(50)))
        patterns = [bytes(rng.choice(b"abc\x00\xff") for _ in range(rng.randrange(9)))
                    for _ in range(rng.randrange(10))]
        if patterns and rng.randrange(2): patterns.append(patterns[0])
        cases.append((text,patterns))
    return cases


def hex_token(value):
    return value.hex() or "-"


def encode(case,kind):
    if kind == "palindrome": return hex_token(case)+"\n"
    text,pattern = case
    if kind == "multi":
        return " ".join([hex_token(text),str(len(pattern)),*(hex_token(p) for p in pattern)])+"\n"
    return hex_token(text)+" "+hex_token(pattern)+"\n"


def vectors(kind):
    return palindrome_vectors() if kind == "palindrome" else multi_vectors() if kind == "multi" else matching_vectors()


def expected(case,name):
    if name == "manacher": return palindromes(case)
    text,pattern = case
    if name == "aho-corasick": return multi(text,pattern)
    if name == "suffix-array":
        order,lcp = suffixes(text)
        return [order,lcp,occurrences(text,pattern)]
    return occurrences(text,pattern)
