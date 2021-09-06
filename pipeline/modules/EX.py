from collections import deque
import numpy as np

from config.data_types import *
from config.register_name import register_name
from module_base import Module
import func.execution.rv64i as instructions

class EX(Module):
    def __init__(self, reg) -> None:
        super().__init__()
        self.reg = reg

    def op(self, data):
        data = self.reg.tick(data).step()

        return getattr(instructions, data["name"])(data)
