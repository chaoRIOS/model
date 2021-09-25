from collections import deque
import numpy as np

from config.data_types import *
from config.register_name import register_name
from module_base import Module, Port
from func.decode.decoder import decode_word


class IDU(Module):
    def __init__(self) -> None:
        super().__init__()
        self.ports = {
            "input": {"IF": Port("IF->[ID]")},
            "output": {
                "ROB": Port("[ID]->ROB"),
                "IF": Port("[ID]->IF"),
            },
        }

    def step(self):
        if self.ports["input"]["IF"].valid and self.ports["output"]["ROB"].ready:
            self.ports["output"]["ROB"].data = self.op(self.ports["input"]["IF"].data)
            self.ports["input"]["IF"].data = None
            self.ports["input"]["IF"].update_status()
            self.ports["output"]["ROB"].update_status()

        return

    def op(self, port_data):
        results = []
        for data in port_data:
            inst = decode_word(data["word"])
            # TODO: Handle decoding error
            if 'decode_error' in inst:
                break
            inst["pc"] = data["pc"]
            inst["insn_code"] = hex(data["word"])
            inst["insn_len"] = 2 if data['is_compressed'] else 4
            results.append(inst)
            if inst['name'] == ['JAL']:
                self.ports['output']['IF'].data = inst
                self.ports['output']['IF'].data['next_pc'] = inst['pc'] + inst['imm'][0]
                self.ports['output']['IF'].update_status()
                break

        if results == []:
            results = None
        return results
