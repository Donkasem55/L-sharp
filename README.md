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
**--file (-I):** input file (relative/absolute path, first positional argument by default, errors if not provided)

**--output (-O):** output file (relative/absolute path, prints output to the console if not provided)

**--kernel**: the kernel the code is compiled for (win32/linux, default win32)


Note: L# has not been tested on Linux yet.

THIS DOCUMENTATION IS INCOMPLETE.

# Features
## Keywords
### include
Includes an assembly standard library. Syntax:
```
include <file name>;
```
### .macro
Defines a macro. Syntax:
```
.macro <macro name> <macro value>;
```
### .import
Imports another L# file, similar to #include in C. Syntax:
```
.import <file name>;
```
### entry
Defines a specific entry point function instead of the default \_start. Syntax:
```
entry <function name>;
```
### varinit
Initialises data sections. Syntax:
```
varinit;
```
### Variable definitions
#### byte
Defines character variables (or array). Syntax:
```
byte <variable name> => <variable value>;
```
For uninitialised variables:
```
byte <variable name> <= <allocated memory in bytes>;
```
#### pipe
Defines an assembly pipeline. Syntax:
```
pipe <variable name> => <assembly definition>;
```
Example:
```
pipe text_length => $-text;
```
#### short
Defines a 16-bit integer. Syntax:
```
short <variable name> => <initial value>;
```
For uninitialised integers:
```
short <variable name>;
```
#### int
Defines a 32-bit integer. Syntax:
```
int <variable name> => <initial value>;
```
For uninitialised integers:
```
int <variable name>;
```
#### long
Defines a 64-bit integer. Syntax:
```
long <variable name> => <initial value>;
```
For uninitialised integers:
```
long <variable name>;
```
#### dword
Defines a DWORD. Syntax:
```
dword <variable name> => <allocated memory>;
```
#### asmdef
Defines a variable using inline assembly. Syntax:
```
asmdef <assembly definition>;
```
### asm
Inline Assembly. Syntax:
```
asm <assembly code>;
```
### label
Creates a new label, local or global. Syntax:
```
label <label name>;
```
### func
Defines a function. Syntax:
```
func <function name> => {
    <function codeblock>
}
```
### while
Declares a while loop. Syntax:
```
while (<condition>) => {
    <while loop codeblock>
}
```
### struct 
Declares a struct. Syntax:
```
struct <name> => {
    <struct codeblock>
}
```
Example:
```
struct wc => {
    long 0;
    long 5;
    long 4;
}
```
###  return
Ends a function. Syntax:
```
return;
```
### =>
Jumps to a location in memory. Syntax:
```
=> <address>;
```
## Features (built-in)
### <+, <-, <\*, \</
Arithmetic operations. Syntax:
```
<variable/register> <+ <source/integer literal>;
<variable/register> <- <source/integer literal>;
<variable/register> <* <source/integer literal>;
<variable/register> </ <source/integer literal>;
```
### Function/stdlib execution
Execute functions and standard libraries with:
```
<function/stdlib name>;
```
With arguments:
```
<function/stdlib name> <= arg1;
<function/stdlib name> <= arg1 <= arg2;
...
```
L# currently only supports up to 3 arguments, stored in r12, r13d, and r14 respectively. Apologies for the inconvenience.

