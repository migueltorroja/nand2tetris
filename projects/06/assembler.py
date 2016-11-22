#! /usr/bin/python

import re
import sys


class HackInstruction(object):
    def __init__(self,line):
        self.instruction_line = self.strip_space_comments(line)

    def get_bin_code(self):
        return None

    def strip_space_comments(self,line):
        line_nocomment=line[:]
        index = line_nocomment.find("//")
        if index >= 0:
            line_nocomment = line_nocomment[:index]
        line_out=""
        for c in line_nocomment:
            if re.match("\S",c):
                line_out +=c
        return line_out

class HackAInstruction(HackInstruction):
    A_INSTRUCTION_RE_STR = "@([0-9]+)"
    def __init__(self,line):
        super(HackAInstruction,self).__init__(line)

    def get_bin_code(self):
        if re.match(HackAInstruction.A_INSTRUCTION_RE_STR,self.instruction_line):
            inst_cmp=re.compile(HackAInstruction.A_INSTRUCTION_RE_STR)
            direct_number = int(inst_cmp.match(self.instruction_line).group(1)) 
            return direct_number & 0x7FFF
        else:
            return None 


class HackCInstruction(HackInstruction):
    def __init__(self,line):
        super(HackCInstruction,self).__init__(line)

    def __get_dest_str(self):
        index_eq = self.instruction_line.find("=")
        if index_eq >= 0:
            return self.instruction_line[0:index_eq]
        else:
            return "" 

    def __get_dest_bin(self):
        dest_bin = 0
        dest_str = self.__get_dest_str()
        if dest_str.find("A") >= 0:
            dest_bin |= 0b100000 
        if dest_str.find("D") >= 0:
            dest_bin |= 0b010000 
        if dest_str.find("M") >= 0:
            dest_bin |= 0b001000 

        return dest_bin

    def __get_op_str(self):
        eq_split = self.instruction_line.split('=')
        return eq_split[-1].split(';')[0]

    def __get_op_bin(self):
        op_str = self.__get_op_str()
        if "0" == op_str:
            op_bin = 0b0101010000000
        elif "1" == op_str:
            op_bin = 0b0111111000000
        elif "-1" == op_str:
            op_bin = 0b0111010000000
        elif "D" == op_str:
            op_bin = 0b0001100000000
        elif "A" == op_str:
            op_bin = 0b0110000000000
        elif "M" == op_str:
            op_bin = 0b1110000000000
        elif "!D" == op_str:
            op_bin = 0b0001101000000
        elif "!A" == op_str:
            op_bin = 0b0110001000000
        elif "!M" == op_str:
            op_bin = 0b1110001000000
        elif "-D" == op_str:
            op_bin = 0b0001111000000
        elif "-A" == op_str:
            op_bin = 0b0110011000000
        elif "-M" == op_str:
            op_bin = 0b1110011000000
        elif "D+1" == op_str:
            op_bin = 0b0011111000000
        elif "A+1" == op_str:
            op_bin = 0b0110111000000
        elif "M+1" == op_str:
            op_bin = 0b1110111000000
        elif "D-1" == op_str:
            op_bin = 0b0001110000000
        elif "A-1" == op_str:
            op_bin = 0b0110010000000
        elif "M-1" == op_str:
            op_bin = 0b1110010000000
        elif "D+A" == op_str:
            op_bin = 0b0000010000000
        elif "D+M" == op_str:
            op_bin = 0b1000010000000
        elif "D-A" == op_str:
            op_bin = 0b0010011000000
        elif "D-M" == op_str:
            op_bin = 0b1010011000000
        elif "A-D" == op_str:
            op_bin = 0b0000111000000
        elif "M-D" == op_str:
            op_bin = 0b1000111000000
        elif "D&A" == op_str:
            op_bin = 0b0000000000000
        elif "D&M" == op_str:
            op_bin = 0b1000000000000
        elif "D|A" == op_str:
            op_bin = 0b0010101000000
        elif "D|M" == op_str:
            op_bin = 0b1010101000000
        else:
            return None
        return op_bin

    def __get_jmp_str(self):
        jmp_cmp = re.compile(".*;(.*)$") 
        mtch = jmp_cmp.match(self.instruction_line)
        if mtch: 
            return mtch.group(1)
        else:
            return ""

    def __get_jmp_code(self):
        jmp_str = self.__get_jmp_str()
        jmp_bin = 0
        if jmp_str == "":
            jmp_bin = 0b000
        elif jmp_str == "JGT":
            jmp_bin = 0b001
        elif jmp_str == "JEQ":
            jmp_bin = 0b010
        elif jmp_str == "JGE":
            jmp_bin = 0b011
        elif jmp_str == "JLT":
            jmp_bin = 0b100
        elif jmp_str == "JNE":
            jmp_bin = 0b101
        elif jmp_str == "JLE":
            jmp_bin = 0b110
        elif jmp_str == "JMP":
            jmp_bin = 0b111
        return jmp_bin

    def get_bin_code(self):
        op_bin = self.__get_op_bin()
        if op_bin is None:
            return None
        return 0b1110000000000000 | op_bin | self.__get_dest_bin() | self.__get_jmp_code()

    
if __name__ == "__main__":
    fp = open(sys.argv[1],"r")
    for l in fp:
        A_binary = HackAInstruction(l).get_bin_code()
        if A_binary is not None: 
            print "{:016b}".format(A_binary)
            continue
        C_binary = HackCInstruction(l).get_bin_code()
        if C_binary is not None: 
            print "{:016b}".format(C_binary)
            continue
        
