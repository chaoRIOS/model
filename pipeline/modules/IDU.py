from collections import deque
import numpy as np

from config.data_types import *
from config.register_name import register_name
from module_base import Module
from func.decode.decoder import decode_word

class IDU(Module):
    def step(self):

        return super().step()

    def op(self, data):
        inst = decode_word(data["word"])
        inst["pc"] = data["pc"]
        inst["insn_code"] = hex(data["word"])
        inst["insn_len"] = 4
        return inst
