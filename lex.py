import sys, os

vartype = {}
args = sys.argv[1:]
kernel = "win32"
argd = {"--kernel":kernel}
arg = "--file"
for i in args:
    if i.startswith("-"):
        if i.startswith("--"):
            arg = i
        else:
            match i:
                case "-I":
                    arg = "--file"
                case "-O":
                    arg = "--output"
                case _:
                    arg = i
    else:
        argd[arg] = i

kernel = argd["--kernel"]
scr = str(os.path.abspath(os.path.dirname(__file__))).replace("\\", "/")
ma = {}

with open(argd["--file"]) as f:
    tex = f.read()

imp = True

while imp:
    imp = False
    i = 0
    x = tex.replace("\t", "").split(";")
    tex = ""
    while i < len(x):
        y = [j.lstrip() for j in x[i].split(" ")]
        if not y:
            i += 1
            continue
        if y[0] == ".macro":
            ma[y[1]] = " ".join(y[2:])
        elif y[0] == ".import":
            with open(y[1]) as f:
                tex += f.read()
            imp = True
        else:
            tex += " ".join(y)
            tex += ";"
        i += 1
    
tx = tex


if True:
    f = tx
    data = [[""]]
    x = f.replace("\t", "")
    i = 0
    lisx = list(x)
    comment = False
    in_str = False
    j = 0
    k = 0
    while i < len(x):
        match lisx[i]:
            case "{":
                if in_str:
                    data[j][k] += "{"
                elif comment:
                    pass
                else:
                    data[j].append("{")
                    data.append([""])
                    j += 1
                    k = 0
            case "}":
                if in_str:
                    data[j][k] += "}"
                elif comment:
                    pass
                else:
                    data[j].append("}")
                    data.append([""])
                    k = 0
                    j += 1
            case " ":
                if in_str:
                    data[j][k] += " "
                elif comment:
                    pass
                else:
                    data[j].append("")
                    k += 1

            case "\"":
                if comment:
                    pass
                elif in_str:
                    in_str = False
                    data[j][k] += "\""
                    data[j].append("")
                    k += 1
                else:
                    data[j].append("\"")
                    k += 1
                    in_str = True

            case "/":
                if comment:
                    pass
                elif in_str:
                    data[j][k] += "/"
                else:
                    try:
                        if lisx[i+1] == "/":
                            comment = True
                        else:
                            data[j][k] += "/"
                    except:
                        data[j] += "/"

            case "\n":
                if comment:
                    comment = False

            case "<":
                if not comment and not in_str:
                    try:
                        if data[j][k][-1] in ["<", ">", "="]:
                            data[j][k] += lisx[i]
                        else:
                            data[j].append("<")
                            k += 1
                    except IndexError:
                        data[j][k] += lisx[i]
                elif in_str:
                    data[j][k] += lisx[i]
            
            case ">":
                if not comment and not in_str:
                    try:
                        if data[j][k][-1] in ["<", ">", "="]:
                            data[j][k] += lisx[i]
                        else:
                            data[j].append(">")
                            k += 1
                    except IndexError:
                        data[j][k] += lisx[i]
                elif in_str:
                    data[j][k] += lisx[i]

            case "=":
                if not comment and not in_str:
                    try:
                        if data[j][k][-1] in ["<", ">", "="]:
                            data[j][k] += lisx[i]
                        else:
                            data[j].append("=")
                            k += 1
                    except IndexError:
                        data[j][k] += lisx[i]
                elif in_str:
                    data[j][k] += lisx[i]

            case ";":
                if not comment and not in_str:
                    data.append([""])
                    j += 1
                    k = 0
                elif in_str:
                    data[j][k] += lisx[i]

            case _:
                if not comment:
                    try:
                        if in_str or (data[j][k][-1] not in ["<", ">", "="]):
                            data[j][k] += lisx[i]
                        else:
                            data[j].append(lisx[i])
                            k += 1
                    except IndexError:
                        data[j][k] += lisx[i]
        i += 1

i = 0
while i < len(data):
    while '' in data[i]:
        data[i].remove('')
    i += 1

while [] in data:
    data.remove([])

print(data, "\n")
d = []
for i in data:
    d += i
    if i[-1] != "{":
        d.append(";")

print(d)
