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
        for i in range(width):
            self.write_byte(address + i, (value >> (i * 8)) & 0xFF)

    def write_byte(self, address, value):
        index = address >> 3
        pos = (address % 8) * 8
        self.mem[index] = np.bitwise_or(
            np.bitwise_and(
                self.data[index], double_type(np.bitwise_not(0xFF << pos)), value << pos
            )
        )

    # Handle read requesets from IF stage
    def read_bytes(self, address, width):
        data = double_type(0)
        for i in range(width):
            data = np.bitwise_or(
                data, double_type(self.read_byte(address + i) << (i * 8))
            )
        return reg_type(data)

    def read_byte(self, address):
        index = int(address) >> 3
        pos = (int(address) % 8) * 8
        data = self.mem[index] >> pos
        return byte_type(data & 0xFF)
