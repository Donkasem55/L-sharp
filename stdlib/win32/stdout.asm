require kernel32.dll
require r12 r13d
require GetStdHandle WriteConsoleA
stdout:
push rbp
mov rbp, rsp
sub rsp, 40
mov ecx, -11
call GetStdHandle
mov rbx, rax
mov rcx, rbx
mov rdx, r12
mov r8d, r13d
lea r9, [rbp-8]
mov qword [rsp+32], 0
call WriteConsoleA
