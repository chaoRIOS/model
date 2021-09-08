from collections import deque
import numpy as np

from config.data_types import *
from config.register_name import register_name
from module_base import Module, Port
import func.execution.rv64i as instructions


class EX(Module):
    def __init__(self) -> None:
        super().__init__()
        self.function_unit_status = {
            "ALU": [0, 0],
            # TODO
        }
        # self.reg = reg
        self.ports = {
            "input": {"ROB": Port("ROB->[EX]")},
            "output": {"ROB": Port("[EX]->ROB")},
        }

    # Execute internal logic
    def step(self):
        if self.ports["input"]["ROB"].valid is True:

            self.ports["output"]["ROB"].data = self.op(self.ports["input"]["ROB"].data)
            self.ports["input"]["ROB"].data = None

            self.ports["input"]["ROB"].update_status()
            self.ports["output"]["ROB"].update_status()
        else:
            pass

    def op(self, port_data):
        # data = self.reg.tick(data).step()
        results = []
        for data in port_data:
            results.append(getattr(instructions, data["name"])(data))

        return {"results": results, "status": self.function_unit_status}
