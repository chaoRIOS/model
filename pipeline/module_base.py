#!/usr/bin/python3

import sys
import os

from numpy.lib.arraysetops import isin

sys.path.append("..")

from config.data_types import *
from config.register_name import register_name


class ModuleBase:
    def __init__(self) -> None:
        self.input_port = None
        self.output_port = None
        self.ports = {
            "input": {},
            "output": {},
        }


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
        for port_type in self.ports:
            for port in self.ports[port_type]:
                self.ports[port_type][port].data = None
                self.ports[port_type][port].update_status()


class Port:
    def __init__(self, name) -> None:
        self.name = name
        self.data = None
        self.valid = self.data is not None
        self.ready = self.data is None

    def update_status(self):
        self.valid = self.data is not None
        self.ready = self.data is None

        if os.environ.get('DEBUG_PRINT') is not None:
            self.print()

    def print(self):
        print("{}: [valid:{} ready:{}]".format(self.name, self.valid, self.ready))
        self.print_data(self.data)

    def print_data(self, data):
        if data is None:
            return

        # EX output data, multi-field
        # TODO: Trap info
        if isinstance(data, dict):
            if "results" in data:
                for issue_queue_data in data["results"]:
                    for item in issue_queue_data:
                        print("  [")
                        for k, v in item.items():
                            if isinstance(v, word_type) or isinstance(v, double_type):
                                print("    {}: {:08x}".format(k, v))
                            else:
                                print("    {}: {}".format(k, str(v)))
                        print("  ]")
            else:
                print("  [")
                for k, v in data.items():
                    if isinstance(v, word_type) or isinstance(v, double_type):
                        print("    {}: {:08x}".format(k, v))
                    else:
                        print("    {}: {}".format(k, str(v)))
                print("  ]")

        elif isinstance(data, list):
            if isinstance(data[0], dict):
                for item in data:
                    print("  [")
                    for k, v in item.items():
                        if isinstance(v, word_type) or isinstance(v, double_type):
                            print("    {}: {:08x}".format(k, v))
                        else:
                            print("    {}: {}".format(k, str(v)))
                    print("  ]")
            elif isinstance(data[0], list):
                for issue_queue_index, issue_queue_data in enumerate(data):
                    print("Issue queue[{}]".format(issue_queue_index))
                    for item in issue_queue_data:
                        print("  [")
                        for k, v in item.items():
                            if isinstance(v, word_type) or isinstance(v, double_type):
                                print("    {}: {:08x}".format(k, v))
                            else:
                                print("    {}: {}".format(k, str(v)))
                        print("  ]")
