// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

// Put your code here.
@R0
D=M
@RETURN0
D;JLT
@R1
D=M
@RETURN0
D;JLT

@R2
M=0
@i
M=0
(LOOP)
@R0
D=M
@i
D=D-M
@END
D;JEQ
@R1
D=M
@R2
M=M+D
@RETURNMAX
M;JLT
@i
M=M+1
@LOOP
0;JMP

(RETURNMAX)
@32767
D=A
@R2
M=D
@END
0;JMP
(RETURN0)
@R2
M=0
@END
0;JMP

(END)
@END
0;JMP
