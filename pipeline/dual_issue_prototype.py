#!/usr/bin/python3

import sys

sys.path.append("..")

from func.decode.decoder import decode_word
import func.execution.rv64i as instructions
from config.data_types import *
from config.register_name import register_name
from utils.elf_parser import load_elf

from modules import *

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
        # self.tohost_addr = data.tohost_addr
        self.cycle = 0

        self.reg = RegisterFile()
        self.memory = Memory(data.memory.data)

        self.fetch_unit = IFU(self.memory, reg_type(data.entry_pc))
        self.decoder = IDU()
        self.function_units = EX(self.reg)
        self.load_store_unit = LSU(self.memory)

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


class Memory(Module):
    def __init__(self, mem) -> None:
        super().__init__()
        self.mem = mem

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

    # Handle read requesets from IF stage
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


class IFU(Module):
    def __init__(self, memory, pc) -> None:
        super().__init__()
        self.pc = pc
        self.fetch_pc = pc
        self.memory = memory

    def step(self):
        if self.input_port is not None:
            # Handle 2 cases:
            # 1) ordinary fetch
            # 2) update pc after branch/jump instructions

            if "next_pc" in self.input_port:
                self.fetch_pc = reg_type(self.input_port["next_pc"])

        self.pc = self.fetch_pc
        self.output_port = self.op(self.input_port)
        self.fetch_pc += reg_type(4)
        self.input_port = None

    def op(self, data):
        return {
            "pc": self.pc,
            "word": word_type(self.memory.read_bytes(self.fetch_pc, 4)),
        }


class IDU(Module):
    def step(self):

        return super().step()

    def op(self, data):
        inst = decode_word(data["word"])
        inst["pc"] = data["pc"]
        inst["insn_code"] = hex(data["word"])
        inst["insn_len"] = 4
        return inst


class EX(Module):
    def __init__(self, reg) -> None:
        super().__init__()
        self.reg = reg


    def op(self, data):
        data = self.reg.tick(data).step()

        return getattr(instructions, data["name"])(data)


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
    def op(self, data):
        # load store
        if "load_mem" in data:
            for load_request in data["load_mem"]:
                data["write_regs"]["int"][0]["value"] = self.memory.read_bytes(
                    load_request["addr"], load_request["len"]
                )

        if "write_mem" in data:
            for store_request in data["store_mem"]:
                self.memory.write_bytes(
                    store_request["addr"], store_request["len"], store_request["value"]
                )

        return data


class RegisterFile(Module):
    def __init__(self) -> None:
        super().__init__()
        self.gpr = np.zeros(32, dtype=reg_type)
        self.csr = np.zeros(4096, dtype=reg_type)

        # Seems like Linux requirement
        self.gpr[0xB] = 0x1020
        self.csr[0x301] = 0x800000008014312F

        # mhartid
        self.csr[0xF14] = 0x0

    def tick(self, data):
        self.input_port = data
        return self

    def step(self):
        # Hard-wire x0 as 0
        self.write_register("int", 0, 0)

        if self.input_port is not None:
            self.output_port = self.op(self.input_port)
            self.input_port = None
        else:
            self.output_port = None

        return self.output_port

    def op(self, data):
        # read register file
        if "read_regs" in data:
            for register_type in data["read_regs"].keys():
                for i in data["read_regs"][register_type]:
                    i["value"] = self.read_register(register_type, i["index"])

        # write back
        if "write_regs" in data:
            for register_type in data["write_regs"].keys():
                for write_reg in data["write_regs"][register_type]:
                    if "value" in write_reg.keys():
                        self.write_register(
                            register_type, write_reg["index"], write_reg["value"]
                        )

        return data

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


for test in rv64ui_p_tests:
    cpu = Simulator(load_elf(riscv_tests_path + test, 2049 * 1024 * 1024))

    while cpu.exit is not True:
        cpu.tick()
        cpu.step()
    break
