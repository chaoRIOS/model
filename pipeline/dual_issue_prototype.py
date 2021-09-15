#!/usr/bin/python3

import sys
import os
import numpy as np
from numpy.lib.arraysetops import isin

sys.path.append("..")

from config.data_types import *
from config.register_name import register_name
from utils.elf_parser import load_elf

from modules import *

np.set_printoptions(formatter={"int": hex})


riscv_tests_path = (
    os.path.expanduser("~") + "/work/riscv-tests/build/share/riscv-tests/isa/"
)
# Target Environment Name	Description
# p                         virtual memory is disabled, only core 0 boots up
# pm	                    virtual memory is disabled, all cores boot up
# pt	                    virtual memory is disabled, timer interrupt fires every 100 cycles
# v	                        virtual memory is enabled
rv64ui_p_tests = [
    i
    for i in os.listdir(riscv_tests_path)
    if "rv64ui" in i and "-p-" in i and "dump" not in i
]


class Simulator:
    def __init__(self, data):
        self.tohost_addr = data.tohost_addr
        self.cycle = 1

        self.reg = REG.PhysicalRegisterFile(100)
        self.memory = MEM.Memory(data.memory.data)

        self.IF = IFU.IFU(self.memory, reg_type(data.entry_pc))
        self.ID = IDU.IDU()
        self.ROB = ROB.reorder_buffer(32, self.reg, 2)
        self.EX = EX.EX()
        self.load_store_unit = LSU.LSU(self.memory)

        self.flush_signal = False

        self.exit = False

    # Transport data
    def tick(self):
        # debug logging
        print("-" * 10, "tick @ cycle:", self.cycle, "-" * 10)

        if self.IF.ports["output"]["ID"].valid and self.ID.ports["input"]["IF"].ready:
            self.ID.ports["input"]["IF"].data = self.IF.ports["output"]["ID"].data
            self.ID.ports["input"]["IF"].update_status()
            self.IF.ports["output"]["ID"].data = None
            self.IF.ports["output"]["ID"].update_status()

        if self.ID.ports["output"]["ROB"].valid and self.ROB.ports["input"]["ID"].ready:
            self.ROB.ports["input"]["ID"].data = self.ID.ports["output"]["ROB"].data
            self.ROB.ports["input"]["ID"].update_status()
            self.ID.ports["output"]["ROB"].data = None
            self.ID.ports["output"]["ROB"].update_status()

        if self.ROB.ports["output"]["EX"].valid and self.EX.ports["input"]["ROB"].ready:
            # input data from ROB: enters backend at T cycle
            # complete_result: enters before T-1 cycle
            self.EX.ports["input"]["ROB"].data = self.ROB.ports["output"]["EX"].data
            self.EX.ports["input"]["ROB"].update_status()
            self.ROB.ports["output"]["EX"].data = None
            self.ROB.ports["output"]["EX"].update_status()

        if self.EX.ports["output"]["ROB"].valid and self.ROB.ports["input"]["EX"].ready:
            # Single issue 0-timing LSU
            self.ROB.ports["input"]["EX"].data = self.load_store_unit.tick(
                self.EX.ports["output"]["ROB"].data
            ).step()
            self.ROB.ports["input"]["EX"].update_status()
            self.EX.ports["output"]["ROB"].data = None
            self.EX.ports["output"]["ROB"].update_status()

        if self.ROB.ports["output"]["IF"].valid and self.IF.ports["input"]["ROB"].ready:
            self.IF.ports["input"]["ROB"].data = self.ROB.ports["output"]["IF"].data
            self.IF.ports["input"]["ROB"].update_status()
            self.ROB.ports["output"]["IF"].data = None
            self.ROB.ports["output"]["IF"].update_status()

            self.flush_signal = True

    # Updata internal status
    def step(self):
        print("-" * 10, " step @ cycle:", self.cycle, "-" * 10)

        # 1) Implictly access memory
        self.IF.step()

        self.ID.step()

        if self.ROB.step() is True:
            # Flush
            return

        self.EX.step()

        # 2) Implictly access memory
        self.load_store_unit.step()

        # self.reg.print_registers()

    def flush(self):
        print("-" * 10, " flush @ cycle:", self.cycle, "-" * 10)

        self.flush_signal = False
        # Flush
        self.IF.flush()
        self.ID.flush()
        self.ROB.flush()
        self.EX.flush()
        self.load_store_unit.flush()


for test in rv64ui_p_tests:
    cpu = Simulator(load_elf(riscv_tests_path + test, 2049 * 1024 * 1024))

    while cpu.exit is not True:
        cpu.tick()
        if cpu.flush_signal is True:
            cpu.flush()
        cpu.step()
        cpu.cycle += 1

        if cpu.cycle > 1000:
            cpu.exit = True

        # TODO: for riscv-test isa test only
        endcode = cpu.memory.read_byte(cpu.tohost_addr)
        if endcode != 0:
            print("cycles = {}".format(cpu.cycle))
            if endcode == 1:
                print("Test {} Passed".format(test))
            else:
                print(
                    "Test {} Failed at test[{}]".format(test, endcode >> byte_type(1))
                )

            break
    break
