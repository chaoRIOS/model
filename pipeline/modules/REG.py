from collections import deque
import numpy as np

from config.data_types import *
from config.register_name import register_name
from module_base import Module


# Unified phisical register file
# Components:
# 1) renaming table
# 2) free list
# 3) valid table, aka. 'p' bit
# 4) register file
# 5) non-renaming CSR file
class PhysicalRegisterFile(Module):
    def __init__(self, size) -> None:
        self.rename_table = {reg: None for reg in register_name}
        # registers holding data
        self.physical_register = np.zeros(size, dtype=reg_type)
        # valid tag of registers
        self.p = [False] * size
        # freelist
        self.freelist = deque(range(size), size)
    
        # CSR
        self.csr = np.zeros(4096, dtype=reg_type)


        # TODO Seems like Linux requirement
        # self.gpr[0xB] = 0x1020
        index = self.rename()
        self.write_physical_register(index, 0x1020)
        self.rename_table[register_name[0xB]] = index
        self.p[index] = True

        self.csr[0x301] = 0x800000008014312F

        # mhartid
        self.csr[0xF14] = 0x0

    def has_free_register(self):
        return len(self.freelist) < self.freelist.maxlen

    def rename(self):
        index = self.freelist.popleft()
        self.p[index] = False
        # Note: Need to update rename table outside
        return index
    
    def get_physical_index(self, index):
        return self.rename_table[register_name[index]]
    
    def set_physical_index(self, arch_index, phy_index):
        self.rename_table[register_name[arch_index]] = phy_index

    def read_physical_register(self, index):
        return self.physical_register[index] if (self.p[index] is True) else None
    
    def write_physical_register(self, index, value):
        if self.p[index] is False:
            self.physical_register[index] = reg_type(value)
            self.p[index] = True
        else:
            raise UserWarning("Try to overwrite valid register[{}] with value {}".format(index, hex(value)))

class ArchitecturalRegisterFile:
    def __init__(self) -> None:
        super().__init__()
        self.gpr = np.zeros(32, dtype=reg_type)
        self.csr = np.zeros(4096, dtype=reg_type)

        # Seems like Linux requirement
        self.gpr[0xB] = 0x1020
        self.csr[0x301] = 0x800000008014312F

        # mhartid
        self.csr[0xF14] = 0x0

    def tick(self, data):
        self.input_port = data
        return self

    def step(self):
        # Hard-wire x0 as 0
        self.write_register("int", 0, 0)

        if self.input_port is not None:
            self.output_port = self.op(self.input_port)
            self.input_port = None
        else:
            self.output_port = None

        return self.output_port

    def op(self, data):
        # read register file
        if "read_regs" in data:
            for register_type in data["read_regs"].keys():
                for i in data["read_regs"][register_type]:
                    i["value"] = self.read_register(register_type, i["index"])

        # write back
        if "write_regs" in data:
            for register_type in data["write_regs"].keys():
                for write_reg in data["write_regs"][register_type]:
                    if "value" in write_reg.keys():
                        self.write_register(
                            register_type, write_reg["index"], write_reg["value"]
                        )

        return data

    def read_register(self, register_type, index):
        if register_type == "int":
            return reg_type(self.gpr[index])
        elif register_type == "csr":
            return reg_type(self.csr[index])

    def write_register(self, register_type, index, value):
        if register_type == "int":
            self.gpr[index] = reg_type(value)
        elif register_type == "csr":
            self.csr[index] = reg_type(value)

    def print_registers(self):
        for i in range(32):
            print(
                register_name[i], ":\t", "{0:#0{1}x}".format(self.gpr[i], 18), end="\t"
            )
            if i % 4 == 3:
                print("", end="\n")
