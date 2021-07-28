#====================================================
# file:       decoder_wrapper.py
# created by: chao wang
# notes:      to wrap rust-implemented decoder
#====================================================
from . import rustdecoder
import numpy as np
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
#         read_regs: [(String,u32)],
#         write_regs: [(String,u32)],
#     },
#     decode_error: String,
# }
# -------------------

def decode(word):
    decoding_result = rustdecoder.decode_instruction(word)
    if decoding_result.decode_error is not None:
        return {'decode_error':decoding_result.decode_error}
    else:
        instruction = decoding_result.inst
        data = {
            'name':instruction.name,
            'imm':instruction.imm,
            'zimm':instruction.zimm,
            'shamt':instruction.shamt,
            'pred_succ':instruction.pred_succ,
            'read_regs':instruction.read_reg,
            'write_regs':instruction.write_reg,
        }
        if data['imm'] is not None:
            data['imm'] = [data['imm']]
        elif data['zimm'] is not None:
            data['imm'], data['zimm'] = [data['zimm']], None
        elif data['shamt'] is not None:
            data['imm'], data['shamt'] = [data['shamt']], None
        elif data['pred_succ'] is not None:
            data['imm'], data['pred_succ'] = list(data['pred_succ']), None

        data = {k: v for k,v in data.items() if v is not None}

        if 'imm' in data:
            data['imm'] = [np.uint64(i) for i in data['imm']]

        # Reorganize registers data format
        if 'read_regs' in data:
            read_regs = data['read_regs']
            data['read_regs'] = {}
            data['read_regs']['int'] = [{'index': v[1]} for v in read_regs if v[0] == 'int']
            data['read_regs']['csr'] = [{'index': v[1]} for v in read_regs if v[0] == 'csr']
            data['read_regs'] = {k: v for k,v in data['read_regs'].items() if len(v) != 0}

        if 'write_regs' in data:
            write_regs = data['write_regs']
            data['write_regs'] = {}
            data['write_regs']['int'] = [{'index': v[1]} for v in write_regs if v[0] == 'int']
            data['write_regs']['csr'] = [{'index': v[1]} for v in write_regs if v[0] == 'csr']
            data['write_regs'] = {k: v for k,v in data['write_regs'].items() if len(v) != 0}

        return data