#!/usr/bin/python3

import sys
import os
import numpy as np

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
        # self.tohost_addr = data.tohost_addr
        self.cycle = 0

        self.reg = REG.ArchitecturalRegisterFile()
        self.memory = MEM.Memory(data.memory.data)

        self.fetch_unit = IFU.IFU(self.memory, reg_type(data.entry_pc))
        self.decoder = IDU.IDU()
        self.function_units = EX.EX(self.reg)
        self.load_store_unit = LSU.LSU(self.memory)

        self.last_execute_result = None
        self.exit = False

    # Transport data
    def tick(self):
        # debug logging
        print("cycle =", self.cycle, "pc =", hex(self.fetch_unit.pc))

        print("self.last_execute_result", self.last_execute_result)

        if self.last_execute_result is not None:
            # Flush
            if "next_pc" in self.last_execute_result.keys():
                self.fetch_unit.flush()
                self.decoder.flush()
                self.function_units.flush()
                self.load_store_unit.flush()

        fetch_result = self.fetch_unit.tick(self.last_execute_result)
        print("fetch_result", fetch_result)

        decode_result = self.decoder.tick(fetch_result)
        print("decode_result", decode_result)

        execute_result = self.function_units.tick(decode_result)
        self.last_execute_result = execute_result
        print("execute_result", execute_result)

        # # 1) read register file
        # decode_result_with_register = self.reg.tick(decode_result).step()
        # self.function_units.tick_in(decode_result_with_register)
        # print("decode_result_with_register", decode_result_with_register)

        # Single issue 0-timing LSU
        load_store_result = self.load_store_unit.tick(execute_result).step()
        # print("load_store_result", load_store_result)

        # 2) write back to register file
        self.reg.tick(load_store_result).step()

        self.cycle += 1

        if self.cycle > 1000:
            self.exit = True

        # TODO: for riscv-test isa test only
        if decode_result is not None:
            if decode_result["name"] == "ECALL":
                if self.reg.read_register("int", 10) == 0:
                    print("Test Passed:{}".format(test))
                    self.exit = True
                else:
                    raise UserWarning(
                        "\nTest failed:{} at pc:{}".format(
                            test, hex(self.fetch_unit.pc)
                        )
                    )

        # debug logging
        self.reg.print_registers()

    # Updata internal status
    def step(self):

        # 1) Implictly access memory
        self.fetch_unit.step()

        self.decoder.step()

        self.function_units.step()

        # 2) Implictly access memory
        self.load_store_unit.step()


for test in rv64ui_p_tests:
    cpu = Simulator(load_elf(riscv_tests_path + test, 2049 * 1024 * 1024))

    while cpu.exit is not True:
        cpu.tick()
        cpu.step()
    break
