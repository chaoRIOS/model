from collections import deque
import numpy as np

from config.data_types import *
from config.register_name import register_name
from module_base import Module


class Memory(Module):
    def __init__(self, mem) -> None:
        super().__init__()
        self.mem = mem

    def write_bytes(self, address, width, value):
        print(
            "[LSU] writing {} of {} byte(s) to {}".format(
                hex(value), width, hex(address)
            )
        )
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
    def read_bytes(self, address, width):
        data = double_type(0)
        for i in range(width):
            data = np.bitwise_or(
                data,
                double_type(self.read_byte(address + reg_type(i)) << reg_type(i * 8)),
            )
        return reg_type(data)

    def read_byte(self, address):
        index = reg_type(address) >> reg_type(3)
        pos = reg_type((address % 8) * 8)
        data = reg_type(self.mem[index]) >> reg_type(pos)
        return reg_type(data & reg_type(0xFF))
