#!/usr/bin/python3

import sys

sys.path.append("..")

from func.decode.decoder import decode_word
import func.execution.rv64i as instructions
from config.data_types import *
from config.register_name import register_name
from utils.elf_parser import load_elf

import os
import numpy as np
import getopt

class Simulator:
    def __init__(self, data):
        self.mem = data.memory.data
        self.fetch_pc = data.entry_pc
        self.pc = data.entry_pc
        self.tohost_addr = data.tohost_addr
        self.cycle = 0
        self.gpr = np.zeros(32, dtype=reg_type)
        self.csr = np.zeros(4096, dtype=reg_type)

        # Seems like Linux requirement
        self.gpr[0xB] = 0x1020
        self.csr[0x301] = 0x800000008014312F

        # mhartid
        self.csr[0xF14] = 0x0

    def tick(self):
        self.cycle += 1
        pass

    def read_register(self, register_type, index):
        if register_type == "int":
            return reg_type(self.gpr[index])
        elif register_type == "csr":
            return reg_type(self.csr[index])

    def write_register(self, register_type, index, value):
        if register_type == "int":
            self.gpr[index] = reg_type(value)
        elif register_type == "csr":
            self.csr[index] = reg_type(value)

    def print_registers(self):
        for i in range(32):
            print(
                register_name[i], ":\t", "{0:#0{1}x}".format(self.gpr[i], 18), end="\t"
            )
            if i % 4 == 3:
                print("", end="\n")

    # Rust read_bytes() costs 1.09s
    # Python read_bytes() costs 0.0003s
    def read_bytes(self, address, width):
        data = double_type(0)
        for i in range(width):
            data = np.bitwise_or(
                data,
                double_type(self.read_byte(address + reg_type(i)) << reg_type(i * 8)),
            )
        return reg_type(data)

    def read_byte(self, address):
        index = reg_type(address) >> reg_type(3)
        pos = reg_type((address % 8) * 8)
        data = reg_type(self.mem[index]) >> reg_type(pos)
        return reg_type(data & reg_type(0xFF))

    def write_bytes(self, address, width, value):
        for i in range(width):
            self.write_byte(
                address + reg_type(i), (value >> reg_type(i * 8)) & reg_type(0xFF)
            )

    def write_byte(self, address, value):
        index = address >> reg_type(3)
        pos = reg_type((address % 8) * 8)
        self.mem[index] = (
            reg_type(self.mem[index]) & double_type(np.invert(reg_type(0xFF) << pos))
        ) | (value << pos)

def main(argv):

    riscv_tests_index = 0
    DEBUG_PRINT = False

    try:
        opts, args = getopt.getopt(argv,"hdi:",["index="])
    except getopt.GetoptError:
        print ('prototype.py [-i <riscv_tests_index=0>] [-d]')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('prototype.py [-i <riscv_tests_index=0>] [-d]')
            sys.exit()
        elif opt in ("-d", "--debug"):
            DEBUG_PRINT = True
        elif opt in ("-i", "--index"):
            riscv_tests_index = int(arg)

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


    for test in rv64ui_p_tests[riscv_tests_index:]:
        cpu = Simulator(load_elf(riscv_tests_path + test, 2049 * 1024 * 1024))

        while cpu.read_byte(cpu.tohost_addr) == 0:
            cpu.write_register("int", 0, 0)
            cpu.pc = reg_type(cpu.fetch_pc)

            # fetch
            fetch_result = word_type(cpu.read_bytes(cpu.fetch_pc, 4))
            # TODO: C-ext
            cpu.fetch_pc += reg_type(4)

            # decode
            decode_result = decode_word(fetch_result)

            # decorate decoding result
            decode_result["pc"] = cpu.pc
            decode_result["insn_code"] = hex(fetch_result)
            decode_result["insn_len"] = 4

            # read register file
            if "read_regs" in decode_result:
                for register_type in decode_result["read_regs"].keys():
                    for i in decode_result["read_regs"][register_type]:
                        i["value"] = cpu.read_register(register_type, i["index"])

            if DEBUG_PRINT:
                print(
                "{} {}".format(hex(decode_result["pc"]), decode_result["name"]),
                decode_result,
            )

            # execute
            execute_result = getattr(instructions, decode_result["name"])(decode_result)

            # load store
            # TODO: place this section in func/
            if "load_mem" in execute_result:
                for load_request in execute_result["load_mem"]:
                    execute_result["write_regs"]["int"][0]["value"] = cpu.read_bytes(
                        load_request["addr"], load_request["len"]
                    )

            if "store_mem" in execute_result:
                for store_request in execute_result["store_mem"]:
                    cpu.write_bytes(
                        store_request["addr"], store_request["len"], store_request["value"]
                    )

            # write back
            if "write_regs" in execute_result:
                for register_type in execute_result["write_regs"].keys():
                    for write_reg in execute_result["write_regs"][register_type]:
                        cpu.write_register(
                            register_type, write_reg["index"], write_reg["value"]
                        )
            if DEBUG_PRINT:
                cpu.print_registers() 

            # branch
            if "next_pc" in execute_result:
                cpu.fetch_pc = reg_type(execute_result["next_pc"])

            cpu.tick()

        # TODO: for riscv-test isa test only
        endcode = cpu.read_byte(cpu.tohost_addr)
        if endcode != 0:
            print("cycles = {}".format(cpu.cycle))
            if endcode == 1:
                print("Test {} Passed".format(test))
            else:
                print("Test {} Failed at test[{}]".format(test, endcode >> byte_type(1)))

            break

if __name__ == "__main__":
   main(sys.argv[1:])