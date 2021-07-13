#====================================================
# file:       elf_parser.py
# created by: cs
# notes:      to wrap rust-implemented elf parser
#====================================================

import elfparser

# ------------------- 
# Load elf file into Python object
# 
# Args:
#   `elf_path`: path to elf file
#   `memory_capacity`: allocated capacity for program
# 
# Return value:
# struct ElfContext {
#     memory: Memory{
#         data: Vec<u64>,
#     },
#     entry_pc: u64,
#     tohost_addr: u64,
# }
# -------------------
def load_elf(elf_path, memory_capacity):
    return elfparser.load_elf(elf_path, memory_capacity)