#!/usr/bin/python3

import sys
import os
import numpy as np
import getopt
import time
import warnings

sys.path.append("..")

from config.data_types import *
from config.register_name import register_name
from utils.elf_parser import load_elf

from modules import *

class Simulator:
    def __init__(self, data):
        self.tohost_addr = data.tohost_addr
        self.cycle = 1

        self.reg = REG.PhysicalRegisterFile(100)
        self.memory = MEM.Memory(np.array(data.memory.data, dtype=np.uint64))

        self.IF = IFU.IFU(self.memory, reg_type(data.entry_pc), 4)
        self.ID = IDU.IDU()
        self.lsu = LSU.LSU(self.memory)
        self.ROB = ROB.reorder_buffer(80, self.reg, self.lsu, 8)
        self.EX = EX.EX()

        self.linkages = [
            "IF->ID",
            "ID->IF",
            "ID->ROB",
            "ROB->EX",
            "EX->ROB",
            "ROB->IF",
        ]

        self.exit = False

    # Transport data
    def tick(self):
        # debug logging
        if DEBUG_PRINT:
            print("-" * 10, "tick @ cycle:", self.cycle, "-" * 10)
        
        # update MCYCLE
        self.reg.write_csr(0xb00, reg_type(self.cycle))

        # Propagation
        for linkage in self.linkages:
            src, dst = linkage.split("->")
            src, dst = (
                getattr(self, src).ports["output"][dst],
                getattr(self, dst).ports["input"][src],
            )
            if src.valid and dst.ready:
                src.data, dst.data = None, src.data
                src.update_status()
                dst.update_status()

    # Updata internal status
    def step(self):
        if DEBUG_PRINT:
            print("-" * 10, " step @ cycle:", self.cycle, "-" * 10)

        # 1) Implictly access memory
        self.IF.step()

        self.ID.step()

        if self.ROB.step() is True:
            # Flush
            return True

        self.EX.step()

        # self.reg.print_registers()

    def flush(self):
        if DEBUG_PRINT:
            print("-" * 10, " flush @ cycle:", self.cycle, "-" * 10)

        # Flush
        self.IF.flush(self.ROB.ports["output"]["IF"].data)
        self.ID.flush()
        self.ROB.flush()
        self.EX.flush()


DEBUG_PRINT = os.environ.get('DEBUG_PRINT') is not None
IS_RISCV_TEST = False
def main(argv):
    global DEBUG_PRINT
    riscv_tests_index = 0
    warnings.filterwarnings('ignore')

    try:
        opts, args = getopt.getopt(argv, "hdi:", ["index="])
    except getopt.GetoptError:
        print("prototype.py [-i <riscv_tests_index=0>] [-d]")
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print("prototype.py [-i <riscv_tests_index=0>] [-d]")
            sys.exit()
        elif opt in ("-d", "--debug"):
            os.environ['DEBUG_PRINT'] = "True"
            DEBUG_PRINT = (os.environ.get('DEBUG_PRINT') is not None)

        elif opt in ("-i", "--index"):
            riscv_tests_index = int(arg)

    np.set_printoptions(formatter={"int": hex})

    riscv_tests_path = (
        os.path.expanduser("~") + "/work/riscv-tests/build-rv64i/share/riscv-tests/isa/"
    )
    # Target Environment Name	Description
    # p                         virtual memory is disabled, only core 0 boots up
    # pm	                    virtual memory is disabled, all cores boot up
    # pt	                    virtual memory is disabled, timer interrupt fires every 100 cycles
    # v	                        virtual memory is enabled
    rv64ui_p_tests = [
        riscv_tests_path + i
        for i in os.listdir(riscv_tests_path)
        if "rv64ui" in i and "-p-" in i and "dump" not in i
    ]

    benchmarks_path = (
        os.path.expanduser("~") + "/work/riscv-tests/build-rv64i/share/riscv-tests/benchmarks/"
    )

    benchmarks = [
        i
        for i in os.listdir(riscv_tests_path)
        if "rv64ui" in i and "-p-" in i and "dump" not in i
    ]


    for test in [benchmarks_path + "dhrystone.riscv"]:
    # for test in ["/opt/riscv-tests/coremark/coremark.riscv"]:
    # for test in rv64ui_p_tests[riscv_tests_index:]:
        cpu = Simulator(load_elf(test, 2049 * 1024 * 1024))

        st = time.time()
        while cpu.exit is not True:
            cpu.tick()
            if cpu.step() is True:
                cpu.flush()

            cpu.cycle += 1

            # TODO: for riscv-test isa test only
            if IS_RISCV_TEST:
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
            else:
                tohost_data = cpu.memory.read_bytes(cpu.tohost_addr,4,False)
                if tohost_data != 0:
                    if reg_type(tohost_data) & reg_type(0x1) == reg_type(0x1):
                        print("{}".format(hex(tohost_data)))
                        print("cycles = {}".format(cpu.cycle))
                        break
                    if tohost_data >= 0x80000000: 
                        # Address of tohost data
                        flag1 = cpu.memory.read_bytes(24 + tohost_data, 4,False)
                        flag2 = cpu.memory.read_bytes(28 + tohost_data, 4,False)

                        if (flag1 != 0) or (flag2 != 0):
                            base = cpu.memory.read_bytes(4 * 4 + tohost_data, 4,False)
                            length = cpu.memory.read_bytes(6 * 4 + tohost_data, 4,False)
                            for i in range(length):
                                # TODO: decode
                                char = cpu.memory.read_bytes(i + base, 1,False)
                                print(chr(char), end='')
                            cpu.memory.write_bytes(reg_type(cpu.tohost_addr + 0x40), 4, reg_type(1))
                            cpu.memory.write_bytes(reg_type(cpu.tohost_addr), 4, reg_type(0))

        et = time.time()

        print("Model run time: {} seconds".format(et - st))
        break

if __name__ == "__main__":
    main(sys.argv[1:])
