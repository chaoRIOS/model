from collections import deque
import numpy as np

from config.data_types import *
from config.register_name import register_name
from module_base import Module, Port


class IFU(Module):
    def __init__(self, memory, pc, issue_number=2) -> None:
        super().__init__()
        self.pc = pc
        self.fetch_pc = pc
        self.memory = memory
        self.issue_number = issue_number

        self.ports = {
            "input": {"ROB": Port("ROB->[IF]")},
            "output": {"ID": Port("[IF]->ID")},
        }

    def step(self):
        if self.ports["input"]["ROB"].valid:
            self.fetch_pc = self.ports["input"]["ROB"].data["next_pc"]
            self.ports["input"]["ROB"].data = None
            self.ports["input"]["ROB"].update_status()

        if self.ports["output"]["ID"].ready:
            self.ports["output"]["ID"].data = []
            for i in range(self.issue_number):
                self.pc = self.fetch_pc
                data = self.op()
                self.fetch_pc += reg_type(4)
                self.ports["output"]["ID"].data.append(data)
            self.ports["output"]["ID"].update_status()

    def op(self):
        return {
            "pc": self.pc,
            "word": word_type(self.memory.read_bytes(self.fetch_pc, 4)),
        }

    def flush(self, data):
        self.ports["output"]["ID"].data = None
        self.ports["output"]["ID"].update_status()

        # Hold input port
        self.ports["input"]["ROB"].data = data
        self.ports["input"]["ROB"].update_status()
        self.step()
