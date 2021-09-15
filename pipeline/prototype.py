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
                data, double_type(self.read_byte(address + i) << (i * 8))
            )
        return reg_type(data)

    def read_byte(self, address):
        index = int(address) >> 3
        pos = (int(address) % 8) * 8
        data = self.mem[index] >> pos
        return byte_type(data & 0xFF)

    def write_bytes(self, address, width, value):
        for i in range(width):
            self.write_byte(address + i, (value >> (i * 8)) & 0xFF)

    def write_byte(self, address, value):
        index = address >> 3
        pos = (address % 8) * 8
        self.mem[index] = np.bitwise_or(
            np.bitwise_and(
                self.data[index], double_type(np.bitwise_not(0xFF << pos)), value << pos
            )
        )


for test in rv64ui_p_tests:
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

        # TODO: for riscv-test isa test only
        if decode_result["name"] == "ECALL":
            if cpu.read_register("int", 10) == 0:
                break
            else:
                raise UserWarning("\nTest failed:{} at pc:{}".format(test, hex(cpu.pc)))

        # decorate decoding result
        decode_result["pc"] = cpu.pc
        decode_result["insn_code"] = hex(fetch_result)
        decode_result["insn_len"] = 4

        # read register file
        if "read_regs" in decode_result:
            for register_type in decode_result["read_regs"].keys():
                for i in decode_result["read_regs"][register_type]:
                    i["value"] = cpu.read_register(register_type, i["index"])

        # execute
        execute_result = getattr(instructions, decode_result["name"])(decode_result)

        # load store
        # TODO: place this section in func/
        if "load_mem" in execute_result:
            for load_request in execute_result["load_mem"]:
                execute_result["write_regs"]["int"][0]["value"] = cpu.read_bytes(
                    load_request["addr"], load_request["len"]
                )

        if "write_mem" in execute_result:
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
        # cpu.print_registers()

        # branch
        if "next_pc" in execute_result:
            cpu.fetch_pc = reg_type(execute_result["next_pc"])

        cpu.tick()
