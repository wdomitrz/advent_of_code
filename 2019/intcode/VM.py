import sys
import copy
import itertools
import collections
from enum import IntEnum
from ..utils import dprint

class OP(IntEnum):
    ADD = 1
    MULT = 2
    INPUT = 3
    OUTPUT = 4
    JUMP_IF_TRUE = 5
    JUMP_IF_FALSE = 6
    LESS_THAN = 7
    EQUAL = 8
    INCREMENT_RB = 9
    HALT = 99

class NeedInputException(Exception):
    pass

class VM:
    def __init__(self, program, input = None, phase = None):
        self.mem = collections.defaultdict(int)
        for i,d in enumerate(program):
            self.mem[i] = d
        self.RB = 0
        self.IP = 0
        self.input = input if input else []
        if phase:
            self.set_param(1, phase)
            self.IP += 2

    def run(self, input = None):
        if input is not None:
            self.input += input

        while self.mem[self.IP] != OP.HALT:
            # dprint(f"[{self.IP}] {self.mem[self.IP]}: {self.mem[self.IP+1]} {self.mem[self.IP+2]} {self.mem[self.IP+3]}")

            cmd = self.mem[self.IP] % 100

            if cmd == OP.ADD:
                self.set_param(3, self.param(1) + self.param(2))
                self.IP += 4
            elif cmd == OP.MULT:
                self.set_param(3, self.param(1) * self.param(2))
                self.IP += 4
            elif cmd == OP.INPUT:
                if len(self.input) == 0:
                    raise(NeedInputException("Missing input!"))
                i = self.input.pop(0)
                dprint(f"using input: {i}")
                self.set_param(1, int(i))
                self.IP += 2
            elif cmd == OP.OUTPUT:
                output = int(self.param(1))
                dprint(f"output: {output}\n")
                self.IP += 2
                yield output
            elif cmd == OP.JUMP_IF_TRUE:
                self.IP = self.param(2) if self.param(1) else self.IP+3
            elif cmd == OP.JUMP_IF_FALSE:
                self.IP = self.param(2) if not self.param(1) else self.IP+3
            elif cmd == OP.LESS_THAN:
                self.set_param(3, self.param(1) < self.param(2))
                self.IP += 4
            elif cmd == OP.EQUAL:
                self.set_param(3, self.param(1) == self.param(2))
                self.IP += 4
            elif cmd == OP.INCREMENT_RB:
                self.RB += self.param(1)
                # dprint(f"RB: {self.RB}")
                self.IP += 2
            else: # op_err
                dprint(f"Unknown opcode: {self.mem[self.IP]} ")
                raise(Exception("Unknown opcode"))

        dprint("[HALT]\n")
        # return None

    @property
    def is_running(self):
        return self.mem[self.IP] != 99

    def mode(self, n):
        return (self.mem[self.IP] // (10**(n+1))) %10

    def param(self, n):
        mode = self.mode(n)
        if mode == 2:
            return self.mem[self.RB+self.mem[self.IP+n]]
        elif mode == 1:
            return self.mem[self.IP+n]
        else:
            return self.mem[self.mem[self.IP+n]]

    def set_param(self, n, val):
        mode = self.mode(n)
        if mode == 2:
            self.mem[self.RB+self.mem[self.IP+n]] = val
        elif mode == 1:
            self.mem[self.IP+n] = val
        else:
            self.mem[self.mem[self.IP+n]] = val
