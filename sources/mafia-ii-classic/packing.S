.intel_syntax noprefix
.code32

/* Preserve binary32 rounding before truncation. Use disjoint integer spills
   so the three x87 stores and subsequent integer loads can proceed independently. */
.section .position,"ax"
    sub esp, 48
    mov eax, [esp + 56]
    fld DWORD PTR [ecx + 0x10]
    fld QWORD PTR [0x18f1430]

    fld DWORD PTR [eax + 4]
    fsub DWORD PTR [ecx + 4]
    fmul st, st(2)
    fadd st, st(1)
    fstp DWORD PTR [esp + 28]

    fld DWORD PTR [eax + 8]
    fsub DWORD PTR [ecx + 8]
    fmul st, st(2)
    fadd st, st(1)
    fstp DWORD PTR [esp + 32]

    fld DWORD PTR [eax]
    fsub DWORD PTR [ecx]
    fmul st, st(2)
    faddp st(1), st
    fstp DWORD PTR [esp + 24]
    fstp st(0)

    fld DWORD PTR [esp + 24]
    fisttp QWORD PTR [esp]
    fld DWORD PTR [esp + 28]
    fisttp QWORD PTR [esp + 8]
    fld DWORD PTR [esp + 32]
    fisttp QWORD PTR [esp + 16]

    mov eax, [esp + 52]
    mov ecx, [esp]
    mov edx, [esp + 8]
    mov WORD PTR [eax], cx
    mov WORD PTR [eax + 2], dx
    movzx ecx, WORD PTR [eax + 4]
    and ecx, 0x8000
    or ecx, [esp + 16]
    mov WORD PTR [eax + 4], cx
    mov al, 1
    add esp, 48
    ret 8

/* The original prefix computes the basis handedness. Preserve it and every
   binary32 intermediate. Three tangent bytes and one normal byte occupy the
   same byte lanes as the original destination. */
.section .basis,"ax"
.macro scaled src, offset, spill
    fld DWORD PTR [\src + \offset]
    fmul st, st(1)
    fadd st, st(1)
    fstp DWORD PTR [esp + \spill]
.endm
.macro truncated rounded, result
    fld DWORD PTR [esp + 48 + \rounded]
    fisttp QWORD PTR [esp + \result]
.endm
    fld QWORD PTR [0x1903a78]
    scaled edi, 4, 0x44
    scaled edi, 8, 0x08
    scaled esi, 8, 0x0c
    scaled esi, 0, 0x10
    scaled esi, 4, 0x14
    fld DWORD PTR [edi]
    fmul st, st(1)
    faddp st(1), st
    fstp DWORD PTR [esp + 0x40]

    sub esp, 48
    truncated 0x40, 0
    truncated 0x44, 8
    truncated 0x08, 16
    truncated 0x0c, 24
    truncated 0x10, 32
    truncated 0x14, 40

    movzx ecx, BYTE PTR [esp + 16]
    mov edx, [esp + 24]
    shl ecx, 16
    shl edx, 24
    or edx, ecx
    mov dl, BYTE PTR [esp]
    mov dh, BYTE PTR [esp + 8]
    mov eax, [esp + 0x78]
    mov [eax], edx

    mov eax, [esp + 0x7c]
    mov edx, [esp + 32]
    mov [eax + 2], dl
    mov edx, [esp + 40]
    mov [eax + 3], dl
    mov ecx, [esp + 0x48]
    shr ecx, 16
    and ecx, 0x8000
    movzx edx, WORD PTR [eax]
    and edx, 0x7fff
    or edx, ecx
    mov WORD PTR [eax], dx
    mov al, 1
    add esp, 48
    pop edi
    pop esi
    add esp, 0x30
    ret
