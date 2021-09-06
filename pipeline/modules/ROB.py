from collections import deque
import numpy as np

from config.data_types import *
from config.register_name import register_name
from module_base import Module



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
        
        def is_ready(self):
            return (
                ((self.PRS1 is not None) and (self.p1 is True)) or (self.PRS1 is None)
            ) and (
                ((self.PRS2 is not None) and (self.p2 is True)) or (self.PRS2 is None)
            )

    # Member methods of class ROB
    def __init__(self, size, physical_register_file, issue_number) -> None:
        super().__init__()
        self.size = size
        self.entries = [self.ROBEntry()] * self.size
        self.free_entry_index = deque(range(size), size)
        self.busy_entry_index = deque([], size)

        # Unified physical register file
        self.physical_register_file = physical_register_file

        # Configurable issue number
        self.issue_number = issue_number

    def get_new_entry(self):
        index = self.free_entry_index.popleft()
        self.busy_entry_index.append(index)
        self.entries[index].use = True

        return index
    
    def deallocate_entry(self, index):
        self.busy_entry_index.remove(index)
        self.entries[index].use = False
        self.free_entry_index.append(index)

    def fill_entry(self, data, index):
        self.entries[index].use = True
        self.entries[index].ex = False
        self.entries[index].opcode = data["name"]

        if "read_regs" in data:
            if 'int' in data['read_regs']:
                if len(data['read_regs']['int']) == 1:
                    self.entries[index].PRS1 = data["read_regs"]['int'][0]["index"]
                    self.entries[index].p1 = data["read_regs"]['int'][0]["p"]
                    self.entries[index].PRS2 = None
                    self.entries[index].p2 = None
                elif len(data['read_regs']['int']) == 2:
                    self.entries[index].PRS1 = data["read_regs"]['int'][0]["index"]
                    self.entries[index].p1 = data["read_regs"]['int'][0]["p"]
                    self.entries[index].PRS2 = data["read_regs"]['int'][1]["index"]
                    self.entries[index].p2 = data["read_regs"]['int'][1]["p"]

        if "write_regs" in data:
            if 'int' in data['write_regs']:
                for reg_data in data['write_regs']['int']:
                    self.entries[index].Rd = reg_data["arch_index"]
                    self.entries[index].PRd = reg_data["index"]
                    self.entries[index].LPRd = reg_data["LPRd"]
        else:
            self.entries[index].Rd = None
            self.entries[index].PRd = None
            self.entries[index].LPRd = None
        
        self.entries[index].data = data

        
    # Recieve input data from:
    # 1) Frontend
    # 2) Function units
    # TODO:
    # Feed output data towards:
    # 1) Functions units
    # 2) BP
    def tick(self, data):
        if self.input_port is None:
            self.input_port = data
            return True
        else:
            return False

    # Processing internal ROB status
    def step(self):

        # 1. Handle input data

        # Handle 2 cases:
        # 1) instructions from ID stage
        # 2) results from EX stage
        # Workaround: Taint data with ROB tag
        processed_item = []
        for i, data in enumerate(self.input_port):
            # instructions from ID stage
            if "ROB_entry" not in data.keys():
                # allocate new entry
                if (len(self.free_entry_index) > 0) and (len(self.physical_register_file.freelist) > 0):
                    # rename
                    if "write_regs" in data:
                        # CSR no renaming
                        
                        # GPR
                        if 'int' in data['write_regs']:
                            for reg_data in data['write_regs']['int']:
                                if self.physical_register_file.has_free_register():
                                    phy_index = self.physical_register_file.rename(reg_data['index'])
                                    reg_data['arch_index'] = reg_data['index']
                                    reg_data['index'] = phy_index
                                    reg_data['LPRd'] = self.physical_register_file.get_physical_index(reg_data['arch_index'])

                    if 'read_regs' in data:
                        # CSR no renaming

                        # GPR
                        if 'int' in data['read_regs']:
                            for reg_data in data['read_regs']:
                                phy_index = self.physical_register_file.get_physical_index(reg_data['index'])
                                if phy_index is None:
                                    raise UserWarning("Invalid mapping of RS reg[{}]".format(reg_data['index']))
                                reg_data['index'] = phy_index
                                reg_data['p'] = self.physical_register_file.p[phy_index]

                    # allocate ROB entry
                    entry_index = self.get_new_entry()

                    # fill ROB entry
                    self.fill_entry(data, entry_index)

                    # taint
                    data['ROB_entry'] = entry_index

                    processed_item.append(i)
                else:
                    # ROB is full
                    pass
            
            # results from EX stage
            else:
                # TODO
                entry_index = data["ROB_entry"]
                if "write_regs" in data.keys():
                    # 1) write PRD register
                    # CSR

                    # GPR
                    if 'int' in data["write_regs"].keys():
                        for write_reg in data["write_regs"]['int']:
                            if "value" in write_reg.keys():
                                self.physical_register_file.write_physical_register(self.entries[entry_index].PRd, reg_type(write_reg["value"]))
                                
                    # Note: This step should be taken on committing
                    # # 2) deallocate LPRD
                    # self.physical_register_file.freelist.append(self.entries[index].LPRd)

                    # 3) update entries with dependent PRSx
                    for i in self.busy_entry_index:
                        if (self.entries[i].PRS1 == self.entries[entry_index].LPRd) and (self.entries[i].p1 is not True):
                            self.entries[i].p1 = True
                        if (self.entries[i].PRS2 == self.entries[entry_index].LPRd) and (self.entries[i].p2 is not True):
                            self.entries[i].p2 = True

                processed_item.append(i) 
        
        # After handling ID data, there may be data left
        if len(processed_item) > 0:
            self.input_port = [
                self.input_port[i]
                for i in len(self.input_port)
                if i not in processed_item
            ]
            # Clear and enable input_port if all added into ROB
            # TODO: partially enable
            if len(self.input_port) == 0:
                self.input_port = None


        # 2. Process internal data, aka. dispatching

        # check updated mapping table
        for entry_index in self.busy_entry_index:
            if (self.entries[entry_index].use is True) and (self.entries[entry_index].ex is False):
                if self.entries[entry_index].p1 is False:
                    self.entries[entry_index].p1 = self.physical_register_file.p[self.entries[entry_index].PRS1]
                if self.entries[entry_index].p2 is False:
                    self.entries[entry_index].p2 = self.physical_register_file.p[self.entries[entry_index].PRS2]
        
        # check entries that are ready to issue
        issue_number = 0
        for entry_index in self.busy_entry_index:
            if issue_number >= self.issue_number:
                break

            if self.entries[entry_index].ex is False and self.entries[entry_index].is_ready():
                # TODO: add FU status in input data from EX
                if data['FU'][self.entries[entry_index].opcode] > 0:
                    # self.output_port.append(self.)
                    pass





        # 3. Commit


        return super().step()

    def op(self, data):
        return super().op(data)

