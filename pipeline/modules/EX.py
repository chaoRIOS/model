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
            "ALU": [{"data": None, "latency": 0} for i in range(2)],
            # TODO
        }
        # self.reg = reg
        self.ports = {
            "input": {"ROB": Port("ROB->[EX]")},
            "output": {"ROB": Port("[EX]->ROB")},
        }

    # Execute internal logic
    def step(self):
        # Allocate function units
        if self.ports["input"]["ROB"].valid is True:
            self.handle_ROB_input(self.ports["input"]["ROB"].data)
            self.ports["input"]["ROB"].data = None
            self.ports["input"]["ROB"].update_status()

        # Step clock
        for function_unit_type in self.function_unit_status:
            for function_unit in self.function_unit_status[function_unit_type]:
                if function_unit["data"] is not None:
                    function_unit["latency"] = max(function_unit["latency"] - 1, 0)

        # Operate if countdown ends
        if self.ports["output"]["ROB"].ready:
            results = []

            for function_unit_type in self.function_unit_status:
                for function_unit in self.function_unit_status[function_unit_type]:
                    if (function_unit["data"] is not None) and (
                        function_unit["latency"] == 0
                    ):
                        results.append(self.op(function_unit["data"]))
                        function_unit["data"] = None

            if results == []:
                self.ports["output"]["ROB"].data = None
            else:
                self.ports["output"]["ROB"].data = {"results": results}
                self.ports["output"]["ROB"].update_status()

    def handle_ROB_input(self, port_data):
        for data in port_data:
            self.function_unit_status[data["function_unit_type"]][
                data["function_unit_index"]
            ] = {"data": data, "latency": 1}

    def op(self, data):
        # data = self.reg.tick(data).step()
        return getattr(instructions, data["name"])(data)

    def flush(self):
        self.function_unit_status = {
            "ALU": [{"data": None, "latency": 0} for i in range(2)],
            # TODO
        }
        return super().flush()
