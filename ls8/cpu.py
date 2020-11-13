"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.SP = 7
        self.PC = 0 
        self.IR = 0
        self.MAR = 0
        self.MDR = 0
        self.FL = 0
        self.reg = [0]*7
        self.reg.append(0xF4)
        self.ram = [0]*255
        self.addresses= {
            0b01010100: self.JMP,
            0b01010101: self.JEQ,
            0b01010110: self.JNE,
            0b10100111: self.CMP,
            0b10000010: self.LDI, 
            0b01000111: self.PRN,
            0b10100010: self.MUL,
        }
        self.definitions = {
            'HLT': 0b00000001,
            'LDI': 0b10000010 ,  
            'PRN': 0b01000111,
            'ADD': 0b10100000,
            'MUL': 0b10100010,
            'CMP': 0b10100111,
            'PUSH': 0b01000101,
            'POP': 0b01000110,
            'CALL': 0b01010000,
            'RET': 0b00010001,
            'JMP': 0b01010100,
            'JNE': 0b01010110,
            'JEQ': 0b01010101,
            'ST': 0b10000100,
        }


    def ram_read(self, MAR):
        return self.ram[MAR]  
    
    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR  
        
    def load(self):
        """Load a program into memory."""
        address = 0
        program = []
        with open(sys.argv[1], 'r') as file:
            for line in file:
                get = line.find("#")
                if get >= 0:
                    line = line[:get]
                get = line.find('\n')
                if get >= 0:
                    line = line[:get]
                if len(line) > 1:
                    line = line.strip()
                    program.append(line)
        for instruction in program:
            self.ram[address] = int(instruction,2)
            address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.FL |= 1
            else:
                self.FL &= 0
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.PC,
            #self.fl,
            #self.ie,
            self.ram_read(self.PC),
            self.ram_read(self.PC + 1),
            self.ram_read(self.PC + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def LDI(self):
        self.PC += 1
        reg = self.ram_read(self.PC)
        self.PC += 1
        val = self.ram_read(self.PC)
        self.reg[reg] = val

    def PRN(self):
        self.PC += 1
        reg = self.ram[self.PC]
        print(self.reg[reg])

    def MUL(self):
        self.PC += 1
        reg1 = self.ram_read(self.PC)
        self.PC += 1
        reg2 = self.ram_read(self.PC)
        self.alu('MUL', reg1, reg2)
    
    def CMP(self):
        self.PC += 1
        reg1 = self.ram_read(self.PC)
        self.PC += 1
        reg2 = self.ram_read(self.PC)
        self.alu("CMP", reg1, reg2)

    def JMP(self):
        self.PC += 1
        reg_with_dest = self.ram_read(self.PC)
        self.PC = self.reg[reg_with_dest]
        self.PC -= 1

    def JEQ(self):
        test_against = self.FL & 0b00000001
        if test_against == 1:
            self.JMP()
        else:
            self.PC += 1

    def JNE(self):
        test_against = self.FL & 0b00000001
        if test_against == 0:
            self.JMP()
        else:
            self.PC += 1

    def run(self):
        """Run the CPU."""
        while True:
            self.IR = self.ram[self.PC]
            if self.IR == self.definitions['HLT']:
                break
            else:
                self.addresses[self.IR]()
                self.PC += 1