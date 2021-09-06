from collections import deque
import numpy as np

from config.data_types import *
from config.register_name import register_name
from module_base import Module
class IFU(Module):
    def __init__(self, memory, pc) -> None:
        super().__init__()
        self.pc = pc
        self.fetch_pc = pc
        self.memory = memory

    def step(self):
        if self.input_port is not None:
            # Handle 2 cases:
            # 1) ordinary fetch
            # 2) update pc after branch/jump instructions

            if "next_pc" in self.input_port:
                self.fetch_pc = reg_type(self.input_port["next_pc"])

        self.pc = self.fetch_pc
        self.output_port = self.op(self.input_port)
        self.fetch_pc += reg_type(4)
        self.input_port = None

    def op(self, data):
        return {
            "pc": self.pc,
            "word": word_type(self.memory.read_bytes(self.fetch_pc, 4)),
        }
