# The L# Programming Language

L# is a compiled programming language designed for low level controls yet easy usage. It comes with the standard library for Windows and Linux, however it is extremely simple to add libraries for other kernels, add to existing kernels, or even add libraries for bare-metal programming. L# compiles to x86 Assembly (formatted for NASM). The standard library of L# is written directly in Assembly, as such they do not need compilation.

The way to print text to the console in L# is:

```
include stdout.asm;
include exit.asm;

entry \\\_start;

varinit;

byte hello => "Hello, world!", 0;
pipe hellolen => $-hello;

func \\\_start => {
	stdout <= hello <= hellolen; // Write hello to console
	exit <= 0;
}
```

Usage:
```
lshrp.exe main.lshrp -O main.asm
```
```
./lshrp main.lshrp -O main.asm
```
```
python main.py main.lshrp -O main.asm
```

Note: L# has never been tested on Linux.
