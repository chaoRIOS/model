from collections import deque
import numpy as np

from config.data_types import *
from config.register_name import register_name
from module_base import Module


class LSU(Module):
    def __init__(self, memory) -> None:
        super().__init__()
        self.memory = memory

    def tick(self, data):
        self.input_port = data
        return self

    def step(self):
        if self.input_port is not None:
            self.output_port = self.op(self.input_port)
            self.input_port = None
        else:
            self.output_port = None

        return self.output_port

    # Handle results from EX stage
    def op(self, port_data):
        for issue_queue_data in port_data["results"]:
            for data in issue_queue_data:
                # load store
                if "load_mem" in data:
                    for load_request in data["load_mem"]:
                        data["write_regs"]["int"][0]["value"] = self.memory.read_bytes(
                            load_request["addr"],
                            load_request["len"],
                            sign_extend=data["name"] in ["LB", "LH", "LW"],
                        )

                if "store_mem" in data:
                    for store_request in data["store_mem"]:
                        self.memory.write_bytes(
                            store_request["addr"],
                            store_request["len"],
                            store_request["value"],
                        )

        return port_data
