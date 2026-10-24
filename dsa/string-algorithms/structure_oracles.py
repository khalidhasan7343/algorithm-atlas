"""External structure checks consume snapshots, not construction helpers."""


def suffix_tree(text, rows):
    symbols = list(text)+[256]
    assert rows and rows[0][:3] == [0,0,-1]
    assert len(rows) <= 2*len(symbols)
    seen,leaves = set(),{}
    stack = [(0,[])]
    while stack:
        identity,spelling = stack.pop()
        assert identity not in seen and 0 <= identity < len(rows)
        seen.add(identity)
        start,end,suffix,*edges = rows[identity]
        assert len(edges)%2 == 0
        if identity:
            assert 0 <= start < end <= len(symbols)
            spelling = spelling+symbols[start:end]
        children = list(zip(edges[::2],edges[1::2]))
        assert len({key for key,_ in children}) == len(children)
        if children:
            assert suffix == -1
            if identity: assert len(children) >= 2  # fully compressed
            for key,child in children:
                assert 0 < child < len(rows)
                assert key == symbols[rows[child][0]]
                stack.append((child,spelling))
        else:
            assert 0 <= suffix < len(symbols) and suffix not in leaves
            assert spelling == symbols[suffix:]
            assert spelling[-1] == 256 and spelling.count(256) == 1
            leaves[suffix] = identity
    assert seen == set(range(len(rows)))
    assert set(leaves) == set(range(len(symbols)))


def automaton(patterns, rows):
    # Reconstruct every trie spelling from the original pattern prefixes.
    prefixes = {b""}
    for pattern in patterns:
        prefixes.update(pattern[:i] for i in range(1,len(pattern)+1))
    assert len(rows) == len(prefixes)
    mapping = {b"":0}
    for prefix in sorted(prefixes,key=lambda p:(len(p),p)):
        if prefix:
            mapping[prefix] = rows[mapping[prefix[:-1]]][3+prefix[-1]]
    assert set(mapping.values()) == set(range(len(rows)))
    for prefix,identity in mapping.items():
        row = rows[identity]
        depth,failure,output,*rest = row
        transitions,terminal = rest[:256],rest[256:]
        assert depth == len(prefix)
        proper = [p for p in prefixes if len(p)<len(prefix) and prefix.endswith(p)]
        expected_failure = max(proper,key=len) if proper else b""
        assert failure == mapping[expected_failure]
        if prefix: assert rows[failure][0] < depth
        expected_terminal = [i for i,p in enumerate(patterns) if p == prefix]
        assert terminal == expected_terminal
        terminal_suffixes = [p for p in proper if p and p in patterns]
        expected_output = mapping[max(terminal_suffixes,key=len)] if terminal_suffixes else -1
        assert output == expected_output
        for ch,target in enumerate(transitions):
            extended = prefix+bytes([ch])
            suffix = next(extended[i:] for i in range(len(extended)+1)
                          if extended[i:] in prefixes)
            assert target == mapping[suffix]
