#!/usr/bin/python3

import sys

sys.path.append("..")

from config.data_types import *
from config.register_name import register_name


class ModuleBase:
    def __init__(self) -> None:
        self.input_port = None
        self.output_port = None


# StateMachine
class Module(ModuleBase):
    # Transporting data through ports and tick the clock
    def tick(self, data):
        self.input_port = data
        if self.output_port is not None:
            # TODO: re-impl as pop()
            tmp = self.output_port
            self.output_port = None
            return tmp
        else:
            return None

    # Execute internal logic
    def step(self):
        if self.input_port is not None:
            # TODO: re-impl as push()
            self.output_port = self.op(self.input_port)
            self.input_port = None
        else:
            pass

    def op(self, data):
        pass

    def flush(self):
        self.input_port = None
        self.output_port = None
