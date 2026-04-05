PRECEDENCE = [
    ["*", "/", "%"],
    ["+", "-"],
    ["<<", ">>", "<=", ">=", "<==>", "<!=>"]
]

def fold_expr(tokens):
    if not isinstance(tokens, list):
        return tokens

    tokens = [fold_expr(t) if isinstance(t, list) else t for t in tokens]

    for ops in PRECEDENCE:
        i = 0
        while i < len(tokens):
            if tokens[i] in ops:
                left = tokens[i-1]
                op = tokens[i]
                right = tokens[i+1]

                node = [left, op, right]

                tokens[i-1:i+2] = [node]
                i -= 1
            else:
                i += 1

    return tokens[0] if len(tokens) == 1 else tokens

def ptst(datin, start=0):
    tst = []
    i = start
    while i < len(datin):
        if datin[i] in ["{", "("]:
            yourmom, nomnomnom = ptst(datin, i+1)
            tst.append(yourmom)
            i += nomnomnom + 2
            continue
        elif datin[i] in ["}", ")"]:
            return tst, i - start
        else:
            tst.append(datin[i])
            i += 1
    return tst, i - start

def group(tst):
    out = []
    added = [[]]
    for i in tst:
        if isinstance(i, list):
            added[-1].append(group(i))
        elif i == ";":
            added.append([])
        else:
            added[-1].append(i)
    out += added
    return out

def parse_tst(d):
    tst, _ = ptst(d)
    print("\n", tst)
    grouped = group(tst)
    print("\n", grouped)

    out = []
    for stmt in grouped:
        if stmt:
            out.append(fold_expr(stmt))

    return out
