# The L# Programming Language

L# is a compiled programming language designed for low level controls yet easy usage. It comes with the standard library for Windows and Linux, however it is extremely simple to add libraries for other kernels, add to existing kernels, or even add libraries for bare-metal programming. L# compiles to x86 Assembly (formatted for NASM). The standard library of L# is written directly in Assembly, as such they do not need compilation.

L# has direct CPU manipulation, meaning you can move data to any specific registers like rax. It also supports inline Assembly with the asm keyword. For example:
```
rax <= 5;
```
moves 5 into RAX, same with
```
asm mov rax, 5
```

The following code prints "Hello, world!" to the console and exits with exit code 0.

```
include stdout.asm;
include exit.asm;

varinit;

byte hello => "Hello, world!", 0;
pipe hellolen => $-hello;

func _start => {
	stdout <= hello <= hellolen; // Write hello to console
	exit <= 0;
}
```

## CLI Arguments:
### Examples:
Compile main.lshrp for windows and output it to main.asm:
```
lshrp.exe main.lshrp --output main.asm
```
Compile main.lshrp for windows and print the result (as a python list) to the console:
```
lshrp.exe main.lshrp
```
Compile main.lshrp for Linux and output the result to main.asm:
```
lshrp.exe main.lshrp --kernel linux --output main.asm
```

### All options:
--file (-I): input file (relative/absolute path, first positional argument by default, errors if not provided)
--output (-O): output file (relative/absolute path, prints output to the console if not provided)
--kernel: the kernel the code is compiled for (win32/linux, default win32)

Note: L# has not been tested on Linux yet.
