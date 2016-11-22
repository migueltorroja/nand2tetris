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

class HackLabelParser(HackInstruction):
    def __init__(self,line):
        super(HackLabelParser,self).__init__(line)
    def get_bin_code(self):
        m = re.match("\(([^)]+)\)",self.instruction_line)
        if m:
            return m.group(1)
        else:
            return None

class HackAInstruction(HackInstruction):
    A_INSTRUCTION_RE_STR = "@([0-9]+)"
    A_INSTRUCTION_SYMBOL_RE_STR = "@([^0-9].*)"
    def __init__(self,line):
        super(HackAInstruction,self).__init__(line)

    def get_bin_code(self,symbol_dict=None):
        if re.match(HackAInstruction.A_INSTRUCTION_RE_STR,self.instruction_line):
            inst_cmp=re.compile(HackAInstruction.A_INSTRUCTION_RE_STR)
            direct_number = int(inst_cmp.match(self.instruction_line).group(1)) 
            return direct_number & 0x7FFF
        elif re.match(HackAInstruction.A_INSTRUCTION_SYMBOL_RE_STR,self.instruction_line):
            inst_cmp=re.compile(HackAInstruction.A_INSTRUCTION_SYMBOL_RE_STR)
            label = inst_cmp.match(self.instruction_line).group(1)
            if symbol_dict and symbol_dict.has_key(label):
                return int(symbol_dict[label]) & 0x7FFF
            else:
                return inst_cmp.match(self.instruction_line).group(1)
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

   
class HackAssembler(object):
    def __init__(self,filename):
        self.filename=filename
        self.symbols=dict()
        self.symbols['R0']      =     0
        self.symbols['R1']      =     1
        self.symbols['R2']      =     2
        self.symbols['R3']      =     3
        self.symbols['R4']      =     4
        self.symbols['R5']      =     5
        self.symbols['R6']      =     6
        self.symbols['R7']      =     7
        self.symbols['R8']      =     8
        self.symbols['R9']      =     9
        self.symbols['R10']     =    10
        self.symbols['R11']     =    11
        self.symbols['R12']     =    12
        self.symbols['R13']     =    13
        self.symbols['R14']     =    14
        self.symbols['R15']     =    15
        self.symbols['SP']      =     0
        self.symbols['LCL']     =     1
        self.symbols['ARG']     =     2
        self.symbols['THIS']    =     3
        self.symbols['THAT']    =     4
        self.symbols['SCREEN']  =0x4000
        self.symbols['KBD']     =0x6000

    def __ResolveSymbols(self):
        fp=open(self.filename,"r")
        program_counter = 0
        for l in fp:
            symbol_name = None
            symbol_value = None
            A_binary = HackAInstruction(l).get_bin_code()
            C_binary = HackCInstruction(l).get_bin_code()
            Label = HackLabelParser(l).get_bin_code()
            if A_binary is not None:
                if type(A_binary) is str:
                    symbol_name = A_binary
                program_counter += 1
            elif C_binary is not None:
                program_counter += 1
            elif Label is not None:
                symbol_name = Label
                symbol_value = program_counter
            if symbol_value is not None:
                self.symbols[symbol_name] = symbol_value
            if not self.symbols.has_key(symbol_name):
                self.symbols[symbol_name] = None
        fp.close()
        last_mem_address = 0x10
        for k,v in self.symbols.iteritems():
            if v is None:
                self.symbols[k] = last_mem_address
                last_mem_address += 1


    def Output(self,outputfile=sys.stdout):
        self.__ResolveSymbols()
        fp=open(self.filename,"r")
        for l in fp:
            A_binary = HackAInstruction(l).get_bin_code(self.symbols)
            if A_binary is not None: 
                outputfile.write("{:016b}\n".format(A_binary))
                continue
            C_binary = HackCInstruction(l).get_bin_code()
            if C_binary is not None: 
                outputfile.write("{:016b}\n".format(C_binary))
                continue
        fp.close()

if __name__ == "__main__":
    hasm=HackAssembler(sys.argv[1])
    hasm.Output(sys.stdout)
