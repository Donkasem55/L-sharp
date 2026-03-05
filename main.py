import sys

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
                    daata[j][k] += "}"
                elif comment:
                    pass
                else:
                    data[j].append("}")
                    data[j].append("")
                    k += 2
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
         
            case ";":
                if not comment and not in_str:
                    data.append([""])
                    j += 1
                    k = 0

            case _:
                if not comment:
                    data[j][k] += lisx[i]
        i += 1

i = 0
while i < len(data):
    while '' in data[i]:
        data[i].remove('')
    i += 1

pre = []
out = []
links = []
externs = []
mainfn = ""
libs = {}
bss = []
scope = ["global"]

linecount = len(data)
i = 0
while i < linecount:
    line = data[i]
    if line == [] or line[0].startswith("//"):
        i += 1
        continue
    if line[0] == "include":
        with open(f"stdlib/{kernel}/{line[1]}") as f:
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
        out = ["section .txt:", f"global {mainfn}"] + out
    elif line[0] == "varinit":
        try:
            if pre[0] != "section .data:":
                pre = ["section .data:"] + pre
        except IndexError:
            pre = ["section .data:"]
        try:
            if bss[0] != "section .bss:":
                bss = ["section .bss:"] + bss
        except IndexError:
            bss = ["section .bss:"]
    elif line[0] == "byte":
        if line[2] == "=>":
            pre.append(f"{line[1]} db {" ".join(line[3:])}")
        elif line[2] == "<=":
            bss.append(f"{line[1]}: resb {line[3]}")
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
        except IndexError:
            pre.append(f"{line[1]}: resb 2")


    elif line[0] == "asmdef":
        pre.append(" ".join(line[1:]))

    elif line[0] == "asm":
        out.append(" ".join(line[1:]))

    elif line[0] == "label":
        pre.append(f"{line[1]}:")

    else:
        try:
            if line[1] == "<=" and line[0] not in libs:
                out.append(f"mov {line[0]}, {line[2]}")
                i += 1
                continue
        except IndexError:
            pass
        if line[0] == "func":
            try:
                if line[2] == "=>":
                    out.append(f"{line[1]}:")
                    scope.append(f"{line[1]}")
            except IndexError:
                out.append(f"{line[1]}:")
        elif line[0] == "}":
            scope.pop()
        try:
            if line[1] == "<=":
                out.append(f"mov r12, {line[2]}")
                try:
                    if line[3] == "<=":
                        out.append(f"mov r13d, {line[4]}")
                except IndexError:
                    pass
                out = out + libs[line[0]]
        except IndexError:
            if line[0] in libs:
                out = out + libs[line[0]]
    i += 1
       
links = list(set(links))

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
