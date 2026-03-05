require
require r12 r13d
require
stdout:
mov eax, r12
mov ebx, r13d
mov rax, 1
mov rdi, 1
mov rsi, eax
mov rdx, ebx
syscall
