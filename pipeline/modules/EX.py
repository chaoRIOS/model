from collections import deque
import numpy as np

from config.data_types import *
from config.register_name import register_name
from module_base import Module, Port
import func.execution.rv64i as instructions
from . import FU


class EX(Module):
    def __init__(self) -> None:
        super().__init__()
        self.ports = {
            "input": {"ROB": Port("ROB->[EX]")},
            "output": {"ROB": Port("[EX]->ROB")},
        }
        self.function_unit_status = FU.new_function_units(with_data=True)

    # Execute internal logic
    def step(self):
        # Allocate function units
        if self.ports["input"]["ROB"].valid is True:
            self.handle_ROB_input(self.ports["input"]["ROB"].data)
            self.ports["input"]["ROB"].data = None
            self.ports["input"]["ROB"].update_status()

        # Step clock
        for issue_queue_index, issue_queue_function_unit_status in enumerate(self.function_unit_status):
            for function_unit_type in issue_queue_function_unit_status:
                for function_unit in issue_queue_function_unit_status[function_unit_type]:
                    if function_unit["data"] is not None:
                        function_unit["latency"] = max(function_unit["latency"] - 1, 0)

        # Operate if countdown ends
        if self.ports["output"]["ROB"].ready:
            results = [[],[],[],[]]

            for issue_queue_index, issue_queue_function_unit_status in enumerate(self.function_unit_status):
                for function_unit_type in issue_queue_function_unit_status:
                    for function_unit in issue_queue_function_unit_status[function_unit_type]:
                        if (function_unit["data"] is not None) and (
                            function_unit["latency"] == 0
                        ):
                            results[issue_queue_index].append(self.op(function_unit["data"]))
                            function_unit["data"] = None

            if results == [[],[],[],[]]:
                self.ports["output"]["ROB"].data = None
            else:
                self.ports["output"]["ROB"].data = {"results": results}
                self.ports["output"]["ROB"].update_status()

    def handle_ROB_input(self, port_data):
        for issue_queue_index, queue_data in enumerate(port_data):
            for data in queue_data:
                self.function_unit_status[issue_queue_index][data["function_unit_type"]][
                    data["function_unit_index"]
                ] = {"data": data, "latency": 1}

    def op(self, data):
        # data = self.reg.tick(data).step()
        return getattr(instructions, data["name"])(data)

    def flush(self):
        self.function_unit_status = FU.new_function_units(with_data=True)
        return super().flush()
