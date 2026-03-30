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

with open(argd["--file"]) as f:
    data = [[""]]
    x = f.read().replace("\t", "")
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

print(data)
i = 0
while i < len(data):
    while '' in data[i]:
        data[i].remove('')
    i += 1

pre = []
out = []
links = []
externs = []
mainfn = "_start"
libs = {}
bss = []
scope = ["global"]
fncs = []

linecount = len(data)
i = 0
while i < linecount:
    line = data[i]

    if line == [] or line[0].startswith("//"):
        i += 1
        continue

    if line[0] == "include":
        with open(f"{scr}/stdlib/{kernel}/{line[1]}") as f:
            asm = f.read().splitlines()
            include = asm[4:]
            lnk = asm[0].split(" ")
            lnk.pop(0)

            extern = asm[2].split(" ")
            extern.pop(0)

            newlib = []
            for j in include:
                newlib.append(j)

            libname = line[1].split(".")[0]
            libs[libname] = newlib

            for j in lnk:
                links.append(j)
            for j in extern:
                externs.append(j)

    elif line[0] == "entry":
        mainfn = line[1]

    elif line[0] == "varinit":
        try:
            if pre[0] != "default rel\nsection .data":
                pre = ["default rel\nsection .data"] + pre
        except IndexError:
            pre = ["default rel\nsection .data"]

        try:
            if bss[0] != "section .bss":
                bss = ["section .bss"] + bss
        except IndexError:
            bss = ["section .bss"]
    elif line[0] == "byte":
        try:
            if line[2] == "=>":
                pre.append(f"{line[1]} db {" ".join(line[3:])}")
                vartype[line[1]] = "byte"
            elif line[2] == "<=":
                bss.append(f"{line[1]}: resb {line[3]}")
                vartype[line[1]] = "byteptr"

        except IndexError:
            bss.append(f"{line[1]}: resb 1")
            vartype[line[1]] = "byteptr"

    elif line[0] == "pipe":
        try:
            if line[2] == "=>":
                pre.append(f"{line[1]} EQU {' '.join(line[3:])}")
            elif line[2] == "<=":
                pre.append(f"{line[3]} EQU {line[1]}")
        except IndexError:
            print(f"Error: At line {i}")

    elif line[0] == "short":
        try:
            if line[2] == "=>":
                pre.append(f"{line[1]} dw {line[3]}")
                vartype[line[1]] = "short"

        except IndexError:
            pre.append(f"{line[1]}: resb 2")
            vartype[line[1]] = "shortptr"

    elif line[0] == "dword":
        if line[2] == "<=":
            bss.append(f"{line[1]}: resd {line[3]}")


    elif line[0] == "asmdef":
        pre.append(" ".join(line[1:]))

    elif line[0] == "asm":
        out.append(" ".join(line[1:]))

    elif line[0] == "label":
        pre.append(f"{line[1]}:")

    elif line[0] == "return":
        try:
            out.append(f"mov rax, {line[1]}")
        except IndexError:
            pass
        out.append("ret")

    elif line[0] == "=>":
        out.append(f"jmp {line[1]}")

    else:
        try:
            if line[1] == "<=" and line[0] not in libs and line[0] not in fncs:
                out.append(f"mov {line[0]}, {line[2]}")
                i += 1
                continue

            elif line[1] == "<":
                match line[2]:
                    case "+":
                        out.append(f"add {line[0]}, {line[3]}")

                    case "-":
                        out.append(f"sub {line[0]}, {line[3]}")

                    case "*":
                        out.append(f"imul {line[0]}, {line[3]}")

                    case "/":
                        out.append(f"idiv {line[0]}, {line[3]}")

        except IndexError:
            pass

        if line[0] == "func":
            try:
                if line[2] == "=>":
                    if scope == ["global"]:
                        out.append(f"{line[1]}:")
                        scope.append(f"{line[1]}")
                        fncs.append(line[1])
                    else:
                        print(f"ScopeError: func {' '.join(line[1:])}, at line {i}: function definition outside 'global'")
                        sys.exit(1)
            except IndexError:
                print(f"SyntaxError: func {line[1]}, at line {i}: incomplete function definition")
                sys.exit(1)
        elif line[0] == "}":
            scope.pop()
            if out[-1] != "ret":
                out.append("ret")

        try:
            if line[1] == "<=":
                if line[2].startswith("(ptr)"):
                    out.append(f"lea r12, [{''.join(line[2][5:])}]")
                else:
                    out.append(f"mov r12, {line[2]}")

                try:
                    if line[3] == "<=":
                        if line[4].startswith("(ptr)"):
                            out.append(f"lea r13d, [{''.join(line[4][5:])}]")
                        else:
                            out.append(f"mov r13d, {line[4]}")

                        try:
                            if line[5] == "<=":
                                if line[6].startswith("(ptr)"):
                                    out.append(f"lea r14, [{''.join(line[6][5:])}]")
                                else:
                                    out.append(f"mov r14, {line[6]}")
                        except IndexError:
                            pass

                except IndexError:
                    pass
                
                if line[0] in fncs:
                    out.append(f"call {line[0]}")
                elif line[0] in libs:
                    out = out + libs[line[0]]
                else:
                    print(f"NameError, {line[0]}, at line {i}: Undefined Function or Unimported Module")
                    sys.exit(1)

        except IndexError:
            if line[0] in libs:
                out = out + libs[line[0]]

    i += 1

out = ["section .text", f"global {mainfn}"] + out
       
links = list(set(links))
externs = list(set(externs))

if "--output" not in argd:
    print(links)
    print(libs)
    print(externs, "\n")
    print(pre)
    print(bss)
    print(out)
else:
    presys = ""
    for i in externs:
        presys += f"extern {i}\n"

    with open(argd["--output"], "w") as f:
        f.write(presys)

    with open(argd["--output"], "a") as f:
        f.write("\n".join(pre) + "\n")
        f.write("\n".join(bss) + "\n")
        f.write("\n".join(out) + "\n")

    if "--linkfile" in argd:
        with open(argd["--linkfile"], "w") as f:
            f.write("\n".join(links))
    else:
        print(f"Application extensions required to link with: {" ".join(links)}")
