require kernel32.dll user32.dll
require r12 r13d
require GetModuleHandleA RegisterClassExA CreateWindowExA ShowWindow UpdateWindow GetMessageA TranslateMessage DispatchMessageA
createwindow:

sub rsp, 40
xor rcx, rcx
call GetModuleHandleA
mov [r12+40], rax

mov rcx, r12
call RegisterClassExA

mov rcx, 0
movzx rax, r13d
lea rdx, [rax]
lea r8, [r14]
mov r9d, 0xCF0000
sub rsp, 32
mov qword [rsp+0], 100
mov qword [rsp+8], 100
mov qword [rsp+16], 500
mov qword [rsp+24], 400
mov qword [rsp+32], 0
mov qword [rsp+40], 0
mov qword [rsp+48], [wc+40]
mov qword [rsp+56], 0
call CreateWindowExA
mov rbx, rax

mov rcx, rbx
mov edx, 1
call ShowWindow

mov rcx, rbx
call UpdateWindow