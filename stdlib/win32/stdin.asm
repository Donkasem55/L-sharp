require kernel32.dll
require r12 r13d r14
require GetStdHandle ReadConsoleA
stdin:
sub rsp, 40
mov ecx, -10
call GetStdHandle
mov rcx, rax
mov rdx, r12
mov r8d, r13d
mov r9, r14
mov qword [rsp+32], 0
call ReadConsoleA
add rsp, 40
