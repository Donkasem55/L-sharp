
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
            added.append(group(i))
        elif i == ";":
            added.append([])
        else:
            added[-1].append(i)
    out += added
    return out

def parse_tst(d):
    tst = []
    tst, _ = ptst(d)
    return group(tst)
