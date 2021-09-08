#!/usr/bin/python3

from collections import deque
import numpy as np
import sys

sys.path.append("..")
sys.path.append("../..")

from config.data_types import *
from config.register_name import register_name
from module_base import Module, Port


class reorder_buffer(Module):

    # Subclass ROBEntry
    class ROBEntry:
        def __init__(self) -> None:
            self.use = False
            self.ex = False

            self.opcode = None
            self.PRS1 = None
            self.PRS2 = None
            self.p1 = False
            self.p2 = False

            self.Rd = None
            self.PRd = None
            self.LPRd = None

            self.data = None

        def __str__(self) -> str:
            return str(self.__dict__)

        def is_ready(self):
            return (
                ((self.PRS1 is not None) and (self.p1 is True)) or (self.PRS1 is None)
            ) and (
                ((self.PRS2 is not None) and (self.p2 is True)) or (self.PRS2 is None)
            )

        def is_complete(self):
            return (self.use is True) and (self.ex is True)

        def fill_with(self, data):
            self.use = True
            self.ex = False
            self.opcode = data["name"]

            self.PRS1 = None
            self.p1 = None
            self.PRS2 = None
            self.p2 = None

            if "read_regs" in data:
                if "int" in data["read_regs"]:
                    if len(data["read_regs"]["int"]) >= 1:
                        # x0
                        if data["read_regs"]["int"][0]["index"] == None:
                            self.PRS1 = None
                            self.p1 = None
                        else:
                            self.PRS1 = data["read_regs"]["int"][0]["index"]
                            self.p1 = data["read_regs"]["int"][0]["p"]

                        self.PRS2 = None
                        self.p2 = None

                    if len(data["read_regs"]["int"]) > 1:
                        # x0
                        if data["read_regs"]["int"][1]["index"] == None:
                            self.PRS2 = None
                            self.p2 = None
                        else:
                            self.PRS2 = data["read_regs"]["int"][1]["index"]
                            self.p2 = data["read_regs"]["int"][1]["p"]

            if "write_regs" in data:
                if "int" in data["write_regs"]:
                    for reg_data in data["write_regs"]["int"]:
                        # x0
                        if reg_data["arch_index"] == 0:
                            self.Rd = None
                            self.PRd = None
                            self.LPRd = None
                        else:
                            self.Rd = reg_data["arch_index"]
                            self.PRd = reg_data["index"]
                            self.LPRd = reg_data["LPRd"]
            else:
                self.Rd = None
                self.PRd = None
                self.LPRd = None

            self.data = data

        def invalid(self):
            self.use = False
            self.ex = False

    # Member methods of class ROB
    def __init__(self, size, physical_register_file, issue_number) -> None:
        super().__init__()
        self.size = size
        self.entries = [self.ROBEntry() for i in range(self.size)]
        self.free_entry_index = deque(range(size), size)
        self.busy_entry_index = deque([], size)

        self.ports = {
            "input": {"ID": Port("ID->[ROB]"), "EX": Port("EX->[ROB]")},
            "output": {"EX": Port("[ROB]->EX"), "IF": Port("[ROB]->IF")},
        }

        self.function_unit_status = {
            "ALU": [0, 0],
            # TODO
        }

        # Unified physical register file
        self.physical_register_file = physical_register_file

        # Configurable issue number
        self.issue_number = issue_number

    # Entry updating methods
    def has_free_entry(self):
        assert len(self.free_entry_index) + len(self.busy_entry_index) == self.size
        return len(self.free_entry_index) > 0

    def allocate_entry(self):
        index = self.free_entry_index.popleft()
        self.busy_entry_index.append(index)
        self.entries[index].use = True
        return index

    def deallocate_entry(self, index):
        self.busy_entry_index.remove(index)
        self.entries[index].use = False
        self.free_entry_index.append(index)

    def fill_entry(self, data, index):
        self.entries[index].fill_with(data)

    # TODO: move to module_base
    # I/O methods
    def check_port_ready(self, port_type, index):
        return self.ports[port_type][index].ready

    def check_port_valid(self, port_type, index):
        return self.ports[port_type][index].valid

    def set_port_data(self, port_type, index, data):
        self.ports[port_type][index].data = data

    # Function unit status methods
    def function_unit_ready(self, opcode):
        # TODO: add opcode >> FU_type mapping
        if opcode is not None:
            function_unit_type = "ALU"
            if 0 in self.function_unit_status[function_unit_type]:
                # Set a meaningless placeholder
                self.function_unit_status[function_unit_type][
                    self.function_unit_status[function_unit_type].index(0)
                ] = -1
                return True
        return False

    # Processing internal ROB status
    def step(self):

        # 1. Handle input data

        # Check port ID->ROB
        # self.ports["input"]["ID"].update_status()
        if self.ports["input"]["ID"].valid is True:
            processed_item = self.handle_ID_input(self.ports["input"]["ID"].data)

            # After handling ID data, there may be data left
            self.ports["input"]["ID"].data = (
                [
                    self.ports["input"]["ID"].data[i]
                    for i in range(len(self.ports["input"]["ID"].data))
                    if i not in processed_item
                ]
                if len(processed_item) < len(self.ports["input"]["ID"].data)
                else None
            )

            self.ports["input"]["ID"].update_status()

        # Check port EX->ROB
        # self.ports["input"]["EX"].update_status()
        if self.ports["input"]["EX"].valid is True:
            # TODO: extend this interface for Trap handling
            data, is_branch, break_entry_index = self.handle_EX_input(
                self.ports["input"]["EX"].data
            )

            if is_branch:
                # TODO: Branch / Trap
                pass
            else:
                pass

            self.ports["input"]["EX"].data = None
            self.ports["input"]["EX"].update_status()

        # 2. Process internal data, aka. dispatching

        # Update mapping in entries
        for entry_index in self.busy_entry_index:
            if (self.entries[entry_index].use is True) and (
                self.entries[entry_index].ex is False
            ):
                # If PRSx is None, then px is None instead of False
                # So only existing PRSx enters either of following 2 branches
                if (self.entries[entry_index].PRS1 is not None) and (
                    self.entries[entry_index].p1 is False
                ):
                    self.entries[entry_index].p1 = self.physical_register_file.p[
                        self.entries[entry_index].PRS1
                    ]
                if (self.entries[entry_index].PRS2 is not None) and (
                    self.entries[entry_index].p2 is False
                ):
                    self.entries[entry_index].p2 = self.physical_register_file.p[
                        self.entries[entry_index].PRS2
                    ]

        # Check port ROB->EX
        # self.ports["output"]["EX"].update_status()
        if self.ports["output"]["EX"].ready is True:
            issue_number = 0
            for entry_index in self.busy_entry_index:
                # maximum issue number
                if issue_number >= self.issue_number:
                    break

                # Check entries ready for issue
                if (
                    (self.entries[entry_index].ex is False)
                    and (self.entries[entry_index].is_ready())
                    and (self.function_unit_ready(self.entries[entry_index].opcode))
                ):
                    if self.ports["output"]["EX"].data is None:
                        self.ports["output"]["EX"].data = []

                    # issue the entry
                    self.ports["output"]["EX"].data.append(
                        self.entries[entry_index].data
                    )
                    issue_number += 1

            if issue_number > 0:
                self.ports["output"]["EX"].update_status()

        # 3. Commit
        # Check port ROB->IF
        # self.ports["output"]["IF"].update_status()
        if (self.ports["output"]["IF"].ready is True) and (
            len(self.busy_entry_index) > 0
        ):
            for i in range(self.issue_number):
                entry = self.entries[self.busy_entry_index[0]]
                if entry.is_complete():

                    data = entry.data

                    # Update CSR
                    if "write_regs" in data:
                        if "csr" in data["write_regs"]:
                            for write_reg in data["write_regs"]["csr"]:
                                if "value" in write_reg:
                                    self.physical_register_file.write_csr(
                                        write_reg["index"],
                                        reg_type(write_reg["value"]),
                                    )

                    # deallocate LPRD
                    self.physical_register_file.deallocate_register(entry.LPRd)

                    entry.invalid()
                    self.free_entry_index.append(self.busy_entry_index.popleft())

                    # Branch controlling logic
                    # TODO: Exception handling
                    if entry.opcode in [
                        "BNE",
                        "BNE",
                        "BLT",
                        "BGE",
                        "BLTU",
                        "BGEU",
                        "JAL",
                        "JALR",
                    ]:
                        if data["next_pc"] == reg_type(data["pc"] + data["insn_len"]):
                            # Not taken
                            pass
                        else:
                            # Taken
                            # return to 'is_branch'
                            self.ports["output"]["IF"].data = data
                            self.ports["output"]["IF"].update_status()

                            # Flush ROB & reg_file
                            # TODO: revert / snapshot
                            # TODO: Add branch prediction

                            # Roll_back
                            for i in range(len(self.busy_entry_index)):
                                entry_index = self.busy_entry_index.pop()
                                self.entries[entry_index].invalid()
                                self.free_entry_index.insert(0, entry_index)
                                if self.entries[entry_index].Rd is not None:
                                    self.physical_register_file.set_physical_index(
                                        self.entries[entry_index].Rd,
                                        self.entries[entry_index].LPRd,
                                    )
                                    self.physical_register_file.rollback_register(
                                        self.entries[entry_index].PRd
                                    )

                            break
                else:
                    break
        return

    def handle_ID_input(self, port_data):
        # instructions from ID stage
        processed_item = []
        for i, data in enumerate(port_data):
            # check ROB and register file,
            # break if either was full
            if self.has_free_entry() and self.physical_register_file.has_free_register(
                len(data["write_regs"]["int"])
                if (("write_regs" in data) and ("int" in data["write_regs"]))
                else 0
            ):
                # rename
                if "write_regs" in data:
                    # CSR no renaming

                    # GPR
                    if "int" in data["write_regs"]:
                        for reg_data in data["write_regs"]["int"]:
                            # x0
                            if reg_data["index"] == 0:
                                reg_data["arch_index"] = 0
                                reg_data["index"] = None
                                reg_data["LPRd"] = None
                            # Other architectural registers
                            elif self.physical_register_file.has_free_register():
                                # Get newly-renamed physical register
                                # with renaming table not changed yet
                                phy_index = self.physical_register_file.rename()

                                # Update data fields
                                reg_data["arch_index"] = reg_data["index"]
                                reg_data["index"] = phy_index
                                # Get old physical register index
                                reg_data[
                                    "LPRd"
                                ] = self.physical_register_file.get_physical_index(
                                    reg_data["arch_index"]
                                )

                                # Update renaming table with new physical index
                                self.physical_register_file.set_physical_index(
                                    reg_data["arch_index"], phy_index
                                )

                # get register mapping
                if "read_regs" in data:
                    # CSR no renaming
                    if "csr" in data["read_regs"]:
                        for reg_data in data["read_regs"]["csr"]:
                            reg_data["value"] = self.physical_register_file.read_csr(
                                reg_data["index"]
                            )

                    # GPR
                    if "int" in data["read_regs"]:
                        for reg_data in data["read_regs"]["int"]:
                            # x0
                            if reg_data["index"] == 0:
                                reg_data["index"] = None
                                reg_data["p"] = True
                                reg_data["value"] = reg_type(0)
                            # Other architectural registers
                            else:
                                phy_index = (
                                    self.physical_register_file.get_physical_index(
                                        reg_data["index"]
                                    )
                                )

                                # Panic if non-mapped register is to be read
                                if phy_index is None:
                                    raise UserWarning(
                                        "Invalid mapping of RS reg[{}]".format(
                                            reg_data["index"]
                                        )
                                    )

                                # In-order entering ROB guarantees consistency
                                reg_data["index"] = phy_index
                                reg_data["p"] = self.physical_register_file.p[phy_index]

                # allocate ROB entry
                entry_index = self.allocate_entry()

                # taint
                data["ROB_entry"] = entry_index

                # fill ROB entry
                self.fill_entry(data, entry_index)

                processed_item.append(i)
            else:
                # ROB/regfile is full
                break
        return processed_item

    def handle_EX_input(self, port_data):
        # FU_status
        self.function_unit_status = port_data["status"]

        # Trap info
        # TODO

        # instruction results
        for i, data in enumerate(port_data["results"]):
            entry_index = data["ROB_entry"]

            # update physical register
            # Note: freelist are not updated yet (on committing)
            if "write_regs" in data:
                # 1) write PRD register
                # CSR

                # Note: CSR should be written on commiting

                # if "csr" in data["write_regs"]:
                #     for write_reg in data["write_regs"]["csr"]:
                #         if "value" in write_reg:
                #             self.physical_register_file.write_csr(
                #                 write_reg["index"],
                #                 reg_type(write_reg["value"]),
                #             )

                # GPR
                if "int" in data["write_regs"]:
                    for write_reg in data["write_regs"]["int"]:
                        if ("value" in write_reg) and (write_reg["index"] is not None):
                            self.physical_register_file.write_physical_register(
                                self.entries[entry_index].PRd,
                                reg_type(write_reg["value"]),
                            )

                # Note: This step should be taken on committing
                # # 2) deallocate LPRD
                # self.physical_register_file.freelist.append(self.entries[index].LPRd)

                # 3) update entries with dependent PRSx
                if self.entries[entry_index].PRd is not None:
                    for i in self.busy_entry_index:
                        if i == entry_index:
                            continue

                        if (self.entries[i].PRS1 == self.entries[entry_index].PRd) and (
                            self.entries[i].p1 is False
                        ):
                            self.entries[i].p1 = True

                        if (self.entries[i].PRS2 == self.entries[entry_index].PRd) and (
                            self.entries[i].p2 is False
                        ):
                            self.entries[i].p2 = True

            # Mark entry as post-EX
            self.entries[entry_index].ex = True
            self.entries[entry_index].data = data

            # TODO: branch and trap control
            if data["name"] in [
                "BNE",
                "BNE",
                "BLT",
                "BGE",
                "BLTU",
                "BGEU",
                "JAL",
                "JALR",
            ]:
                # TODO: Branch to 'next_pc'
                if data["next_pc"] == reg_type(data["pc"] + data["insn_len"]):
                    # Not taken
                    pass
                else:
                    # return to 'is_branch'
                    return port_data, True, i
        return port_data, False, 0

    def print_ports(self):
        for _, cluster in self.ports.items():
            for _, port in cluster.items():
                port.print()


# Test
if __name__ == "__main__":
    import REG

    decode_result = [
        {
            "name": "JAL",
            "imm": [72],
            "write_regs": {"int": [{"index": 0}]},
            "pc": 2147483648,
            "insn_code": "0x480006f",
            "insn_len": 4,
        },
        {
            "name": "CSRRS",
            "read_regs": {"int": [{"index": 0}], "csr": [{"index": 834}]},
            "write_regs": {"int": [{"index": 30}], "csr": [{"index": 834}]},
            "pc": 2147483652,
            "insn_code": "0x34202f73",
            "insn_len": 4,
        },
    ]
    ROB = reorder_buffer(32, REG.PhysicalRegisterFile(100), 2)
    ROB.ports["input"]["ID"].data = decode_result
    ROB.ports["input"]["ID"].update_status()

    ROB.step()
