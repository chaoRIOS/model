#====================================================
# file:       decoder.py
# created by: chao wang
# notes:      to wrap rust-implemented decoder
#====================================================
from . import elfparser

from . import rustdecoder

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

def decode(word):
    return rustdecoder.decode_instruction(word)
