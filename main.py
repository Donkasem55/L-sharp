import sys, os
from lex import lex
from tst import parse_tst

from pprint import PrettyPrinter

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
d, ma = lex(scr, argd)
print(d, "\n")
data = parse_tst(d)
# printer = PrettyPrinter(indent=4, width=40)
# printer.pprint(data)
# sys.exit(0)

pre = []
out = []
links = []
externs = []
mainfn = "_start"
libs = {}
bss = []
scope = ["global"]
fncs = []
currentline = 0
crsv = 0

def evalexpr(line, dest="rax"):
    global crsv
    if isinstance(line, str):
        return f"""
mov {dest}, {line}
"""

    left = line[0]
    right = line[2]
    code = ""

    if len(line) >= 2:
        end = ""
        if line[1] == "<!=>":
            code += evalexpr(left, dest)
            code += evalexpr(right, "rbx")
            code += f"""
cmp {dest}, rbx
setne {dest[1]}l
            """

        elif line[1] == "<==>":
            code += evalexpr(left, dest)
            code += evalexpr(right, "rbx")
            code += f"""
cmp {dest}, rbx
sete {dest[1]}l
            """

        elif line[1] == "<<":
            code += evalexpr(left, dest)
            code += evalexpr(right, "rbx")
            code += f"""
cmp {dest}, rbx
setlt {dest[1]}l
            """

        elif line[1] == ">>":
            code += evalexpr(left, dest)
            code += evalexpr(right, "rbx")
            code += f"""
cmp {dest}, rbx
setgt {dest[1]}l
            """

        elif line[1] == "<=":
            code += evalexpr(left, dest)
            code += evalexpr(right, "rbx")
            code += f"""
cmp {dest}, rbx
setle {dest[1]}l
            """

        elif line[1] == ">=":
            code += evalexpr(left, dest)
            code += evalexpr(right, "rbx")
            code += f"""
cmp {dest}, rbx
setge {dest[1]}l
            """

        elif line[1] == "+":
            code += f"add {dest}, rbx\n"

        elif line[1] == "-":
            code += f"sub {dest}, rbx\n"

        elif line[1] == "*":
            code += f"imul {dest}, rbx\n"

        elif line[1] == "/":
            code += f"idiv {dest}, rbx\n"
    
    return code

exprs = ["<!=>", "<==>", "<<", ">>", "<=", ">=", "+", "-", "*", "/"]
# print(evalexpr([["a", "+", "b"], "<!=>", ["c", "-", "d"]]))
# sys.exit(0)

def codegen(line):
    global vartype, links, mainfn, libs, scope, fncs, externs, currentline
    pre, bss, out, = [], [], []
    end = ""
    if isinstance(line[0], list):
        for i in line:
            a, b, c = codegen(i)
            pre += a
            bss += b
            out += c

    if line == [] or line[0].startswith("//"):
        return [], [], []

    for j in range(len(line)):
        if line[j] in ma:
            line[j] = ma[line[j]]

    

    if line[0] == "while":
        tlcrsv = crsv
        out += f".LSCOMPRSVLAB{tlcrsv}:\n"
        crsv += 1
        tscrsv = crsv
        crsv += 1
        scope.append("while")

        end = evalexpr(line[1])
        out += end
        out += "cmp rax, 0\n"
        out += f"je .LSCOMPRSVLAB{tscrsv}\n"
        if line[2] != "=>":
            print(f"SyntaxError: Incomplete while loop, at line {currentline}.")

        a, b, c = codegen(line[3])
        pre += a
        bss += b
        out += c
        out += f"jmp .LSCOMPRSVLAB{tlcrsv}\n"
        out += f".LSCOMPRSVLAB{tscrsv}:\n"

        scope.pop()

    if line[0] == "include":
        if line[1].startswith("\""):
            with open(f"{line[1:-1]}") as f:
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

        else:
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
                pre.append(f"{line[1]} db {" ".join(line[2+1:])}")
                vartype[line[1]] = "byte"
            elif line[2] == "<=":
                bss.append(f"{line[1]}: resb {line[3]}")
                vartype[line[1]] = "byte"

        except IndexError:
            bss.append(f"{line[1]}: resb 1")
            vartype[line[1]] = "byte"

    elif line[0] == "pipe":
        try:
            if line[2] == "=>":
                pre.append(f"{line[1]} EQU {' '.join(line[2+1:])}")
            elif line[2] == "<=":
                pre.append(f"{line[3]} EQU {line[1]}")
            vartype[line[1]] = "pipe"
        except IndexError:
            print(f"SyntaxError: At line {currentline}, expected '=>' or '<=' as definition, however nothing is found.")

    elif line[0] == "short":
        try:
            if line[2] == "=>":
                pre.append(f"{line[1]} dw {line[3]}")
                vartype[line[1]] = "short"

            else:
                print(f"SyntaxError: At line {currentline}: unexpected character at the end of variable definition.")

        except IndexError:
            pre.append(f"{line[1]}: resb 2")
            vartype[line[1]] = "short"

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
            if isinstance(line[1], str):
                out.append(f"mov rdx, {line[1]}")
            else:
                a = evalexpr(line[1])
                out.append(a)
                out.append(f"mov rdx, rax")
        except IndexError:
            pass
        out.append("ret")

    elif line[0] == "=>":
        if isinstance(line[1], str):
            out.append(f"jmp {line[1]}")
        else:
            a = evalexpr(line[1])
            out.append(a)
            out.append(f"jmp [rax]")

    else:
        try:
            if line[1] == "<=" and line[0] not in libs and line[0] not in fncs:
                if isinstance(line[2], str):
                    out.append(f"mov {line[0]}, {line[2]}")
                else:
                    a = evalexpr(line[2])
                    out += a
                    out.append(f"mov {line[0]}, rax")

            elif line[1] == "<":
                match line[2]:
                    case "+":
                        if isinstance(line[3], str):
                            out.append(f"add {line[0]}, {line[3]}")
                        else:
                            a = evalexpr(line[3])
                            out.append(a)
                            out.append(f"add {line[0]}, rax")

                    case "-":
                        if isinstance(line[3], str):
                            out.append(f"sub {line[0]}, {line[3]}")
                        else:
                            a = evalexpr(line[3])
                            out.append(a)
                            out.append(f"sub {line[0]}, rax")

                    case "*":
                        if isinstance(line[3], str):
                            out.append(f"imul {line[0]}, {line[3]}")
                        else:
                            a = evalexpr(line[3])
                            out.append(a)
                            out.append(f"imul {line[0]}, rax")

                    case "/":
                        if isinstance(line[3], str):
                            out.append(f"idiv {line[0]}, {line[3]}")
                        else:
                            a = evalexpr(line[3])
                            out.append(a)
                            out.append(f"idiv {line[0]}, rax")

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
            if out[-1] != "ret" and (scope[-1] not in ["while", "for", "if", "else"]):
                out.append("ret")

        try:
            if line[1] == "<=":
                if isinstance(line[2], str):
                    if line[2].startswith("[ptr]"):
                        out.append(f"lea r12, [{''.join(line[2][5:])}]")
                    else:
                        out.append(f"mov r12, {line[2]}")

                else:
                    a = evalexpr(line[2])
                    out.append(a)
                    out.append(f"mov r12, rax")

                try:
                    if line[3] == "<=":
                        if isinstance(line[4], str):
                            if line[4].startswith("[ptr]"):
                                out.append(f"lea r13d, [{''.join(line[4][5:])}]")
                            else:
                                out.append(f"mov r13d, {line[4]}")

                        else:
                            a = evalexpr(line[4])
                            out.append(a)
                            out.append(f"mov r12, rax")

                        try:
                            if line[5] == "<=":
                                if line[6].startswith("[ptr]"):
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
    currentline += 1
    return pre, bss, out

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
