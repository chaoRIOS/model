#====================================================
# file:       decoder.py
# created by: chao wang
# notes:      to wrap rust-implemented decoder
#====================================================
from . import rustdecoder

# ------------------- 
# Decode word to instruction
# 
# Args:
#   `word`: 32-bit fetched raw data
# 
# Return value:
# struct DecodingResultPy {
#     inst: InstructionPy{
#         name: String,
#         imm: i32,
#         zimm: u32,
#         shamt: i32,
#         pred_succ: (u32,u32),
#         read_reg: [(String,u32)],
#         write_reg: [(String,u32)],
#     },
#     decode_error: String,
# }
# -------------------

def decode(word):
    return rustdecoder.decode_instruction(word)
