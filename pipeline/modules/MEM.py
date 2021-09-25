from collections import deque
import os
import numpy as np

from config.data_types import *
from config.register_name import register_name
from module_base import Module

from numba import types, typed
from numba.experimental import jitclass

DRAM_BASE = reg_type(0x80000000)

@jitclass([
    ('mem', types.ListType(types.uint64))
])
class Memory:
    def __init__(self, mem) -> None:
        # self.mem = mem
        self.mem = typed.List.empty_list(types.uint64)
        [self.mem.append(x) for x in mem]

    def write_bytes(self, address, width, value):
        address -= DRAM_BASE
        for i in range(width):
            self.write_byte(
                address + reg_type(i), (value >> reg_type(i * 8)) & reg_type(0xFF)
            )

    def write_byte(self, address, value):
        index = address >> reg_type(3)
        pos = reg_type((address % 8) * 8)
        self.mem[index] = (
            reg_type(self.mem[index]) & double_type(np.invert(reg_type(0xFF) << pos))
        ) | (value << pos)

    # Handle read requesets from IF stage
    def read_bytes(self, address, width, sign_extend):
        address -= DRAM_BASE
        data = double_type(0)
        for i in range(width):
            # TODO: replace with `|` operator?
            data = np.bitwise_or(
                data,
                double_type(self.read_byte(address + reg_type(i)) << reg_type(i * 8)),
            )
        if sign_extend is True:
            sign = reg_type(data >> reg_type(width * 8 - 1)) & reg_type(0x1)
            if sign != 0:     
                data = reg_type(data) | reg_type( 
                    reg_type(np.invert(reg_type(0))) << reg_type(width * 8)
                )
        return reg_type(data)

    def read_byte(self, address):
        index = reg_type(address) >> reg_type(3)
        pos = reg_type((address % 8) * 8)
        data = reg_type(self.mem[index]) >> reg_type(pos)
        return reg_type(data & reg_type(0xFF))
