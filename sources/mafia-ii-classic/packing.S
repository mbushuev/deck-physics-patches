.intel_syntax noprefix
.code32

/* The exponent range and intermediate binary32 rounding match the game path. */
.section .position,"ax"
    sub esp, 24
    mov eax, [esp + 32]
    fld DWORD PTR [ecx + 0x10]
    fld QWORD PTR [0x18f1430]

    fld DWORD PTR [eax + 4]
    fsub DWORD PTR [ecx + 4]
    fmul st, st(2)
    fadd st, st(1)
    fstp DWORD PTR [esp + 8]

    fld DWORD PTR [eax + 8]
    fsub DWORD PTR [ecx + 8]
    fmul st, st(2)
    fadd st, st(1)
    fstp DWORD PTR [esp + 12]

    fld DWORD PTR [eax]
    fsub DWORD PTR [ecx]
    fmul st, st(2)
    faddp st(1), st
    fstp DWORD PTR [esp + 16]
    fstp st(0)

    fld DWORD PTR [esp + 16]
    fisttp QWORD PTR [esp]
    mov ecx, [esp]
    fld DWORD PTR [esp + 8]
    fisttp QWORD PTR [esp]
    mov edx, [esp]
    fld DWORD PTR [esp + 12]
    fisttp QWORD PTR [esp]
    mov eax, [esp + 28]
    mov WORD PTR [eax], cx
    mov WORD PTR [eax + 2], dx
    movzx ecx, WORD PTR [eax + 4]
    and ecx, 0x8000
    or ecx, [esp]
    mov WORD PTR [eax + 4], cx

    mov al, 1
    add esp, 24
    ret 8

/* Preserve the cross product, dot product and binary32 rounding before each
   truncation. The caller-visible stores retain their original order. */
.section .basis,"ax"
.macro scale_component src, delta, spill
    fld DWORD PTR [\src + \delta]
    fmul st, st(1)
    fadd st, st(1)
    fstp DWORD PTR [esp + \spill]
.endm
    fld QWORD PTR [0x1903a78]
    scale_component edi, 4, 0x44
    scale_component edi, 8, 0x08
    scale_component esi, 8, 0x0c
    scale_component esi, 0, 0x10
    scale_component esi, 4, 0x14
    fld DWORD PTR [edi]
    fmul st, st(1)
    faddp st(1), st
    fstp DWORD PTR [esp + 0x40]

    fld DWORD PTR [esp + 0x40]
    fisttp QWORD PTR [esp + 0x20]
    movzx edx, BYTE PTR [esp + 0x20]
    fld DWORD PTR [esp + 0x44]
    fisttp QWORD PTR [esp + 0x20]
    mov dh, BYTE PTR [esp + 0x20]
    fld DWORD PTR [esp + 0x08]
    fisttp QWORD PTR [esp + 0x20]
    movzx ecx, BYTE PTR [esp + 0x20]
    shl ecx, 16
    or edx, ecx
    fld DWORD PTR [esp + 0x0c]
    fisttp QWORD PTR [esp + 0x20]
    mov ecx, [esp + 0x20]
    shl ecx, 24
    or edx, ecx
    mov [esp + 0x0c], edx

    fld DWORD PTR [esp + 0x10]
    fisttp QWORD PTR [esp + 0x20]
    mov edx, [esp + 0x20]
    mov [esp + 0x10], edx
    fld DWORD PTR [esp + 0x14]
    fisttp QWORD PTR [esp + 0x20]
    mov ecx, [esp + 0x18]
    and ecx, 0x80000000
    shr ecx, 16

    pop edi
    mov eax, [esp + 0x44]
    mov edx, [esp + 0x08]
    mov [eax], edx
    mov eax, [esp + 0x48]
    mov edx, [esp + 0x0c]
    mov [eax + 2], dl
    mov edx, [esp + 0x1c]
    mov [eax + 3], dl
    movzx edx, WORD PTR [eax]
    and edx, 0x7fff
    or edx, ecx
    mov WORD PTR [eax], dx
    mov al, 1
    pop esi
    add esp, 0x30
    ret
