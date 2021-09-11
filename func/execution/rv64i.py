import numpy as np
from config.data_types import *

import warnings


def LUI(data):
    data["write_regs"]["int"][0]["value"] = reg_type(data["imm"][0])
    return data

def AUIPC(data):
    data["write_regs"]["int"][0]["value"] = reg_type(data["pc"] + reg_type(data["imm"][0]))
    return data

def JAL(data):
    data["next_pc"] = reg_type(data["pc"]+ reg_type(data["imm"][0]))
    data["write_regs"]["int"][0]["value"] = reg_type(data["pc"]+data["insn_len"])
    return data

def JALR(data):
    data["next_pc"] = reg_type((data["read_regs"]["int"][0]["value"] + reg_type(data["imm"][0])) >> 1 << 1)
    data["write_regs"]["int"][0]["value"] = reg_type(data["pc"]+data["insn_len"])    
    return data

def BEQ(data):
    if data["read_regs"]["int"][0]["value"] == data["read_regs"]["int"][1]["value"]:
        data["next_pc"] = reg_type(data["pc"] + reg_type(data["imm"][0]))
        data["taken"] = True
    else:
        data["next_pc"] = reg_type(data["pc"] + data["insn_len"])
        data["taken"] = False
    return data

# TODO: fix binary complement
def BNE(data):
    if data["read_regs"]["int"][0]["value"] != data["read_regs"]["int"][1]["value"]:
        data["next_pc"] = reg_type(data["pc"] + reg_type(data["imm"][0]))
        data["taken"] = True
    else:
        data["next_pc"] = reg_type(data["pc"] + data["insn_len"])
        data["taken"] = False
    return data

def BLT(data):
    # binary complement
    lhs = (np.invert(data["read_regs"]["int"][0]["value"]) + 1) if data["read_regs"]["int"][0]["value"] & reg_type(0x8000_0000_0000_0000) == 0x8000_0000_0000_0000 else data["read_regs"]["int"][0]["value"]
    rhs = (np.invert(data["read_regs"]["int"][1]["value"]) + 1) if data["read_regs"]["int"][1]["value"] & reg_type(0x8000_0000_0000_0000) == 0x8000_0000_0000_0000 else data["read_regs"]["int"][1]["value"]
    if lhs < rhs:
        data["next_pc"] = reg_type(data["pc"] + reg_type(data["imm"][0]))
        data["taken"] = True
    else:
        data["next_pc"] = reg_type(data["pc"] + data["insn_len"])
        data["taken"] = False
    return data

def BGE(data):
    # binary complement
    lhs = (np.invert(data["read_regs"]["int"][0]["value"]) + 1) if data["read_regs"]["int"][0]["value"] & reg_type(0x8000_0000_0000_0000) == 0x8000_0000_0000_0000 else data["read_regs"]["int"][0]["value"]
    rhs = (np.invert(data["read_regs"]["int"][1]["value"]) + 1) if data["read_regs"]["int"][1]["value"] & reg_type(0x8000_0000_0000_0000) == 0x8000_0000_0000_0000 else data["read_regs"]["int"][1]["value"]
    if lhs >= rhs:
        data["next_pc"] = reg_type(data["pc"] + reg_type(data["imm"][0]))
        data["taken"] = True
    else:
        data["next_pc"] = reg_type(data["pc"] + data["insn_len"])
        data["taken"] = False
    return data

def BLTU(data):
    if data["read_regs"]["int"][0]["value"] < data["read_regs"]["int"][1]["value"]:
        data["next_pc"] = reg_type(data["pc"] + reg_type(data["imm"][0]))
        data["taken"] = True
    else:
        data["next_pc"] = reg_type(data["pc"] + data["insn_len"])
        data["taken"] = False
    return data

def BGEU(data):
    if data["read_regs"]["int"][0]["value"] >= data["read_regs"]["int"][1]["value"]:
        data["next_pc"] = reg_type(data["pc"] + reg_type(data["imm"][0]))
        data["taken"] = True
    else:
        data["next_pc"] = reg_type(data["pc"] + data["insn_len"])
        data["taken"] = False
    return data


def LB(data):
    data["load_mem"]= [{
        "addr": reg_type(data["read_regs"]["int"][0]["value"] + reg_type(data["imm"][0])),
        "len": 1
    }]
    return data

def LH(data):    
    data["load_mem"]= [{
        "addr": reg_type(data["read_regs"]["int"][0]["value"] + reg_type(data["imm"][0])),
        "len": 2
    }]
    return data

def LW(data):
    data["load_mem"]= [{
        "addr": reg_type(data["read_regs"]["int"][0]["value"] + reg_type(data["imm"][0])),
        "len": 4
    }]
    return data

# TODO: add 0-ext
def LBU(data):
    data["load_mem"]= [{
        "addr": reg_type(data["read_regs"]["int"][0]["value"] + reg_type(data["imm"][0])),
        "len": 1
    }]
    return data

def LHU(data):
    data["load_mem"]= [{
        "addr": reg_type(data["read_regs"]["int"][0]["value"] + reg_type(data["imm"][0])),
        "len": 2
    }]
    return data

def LWU(data):
    data["load_mem"]= [{
        "addr": reg_type(data["read_regs"]["int"][0]["value"] + reg_type(data["imm"][0])),
        "len": 4
    }]
    return data

def LD(data):
    data["load_mem"]= [{
        "addr": reg_type(data["read_regs"]["int"][0]["value"] + reg_type(data["imm"][0])),
        "len": 8
    }]
    return data

def SB(data):
    data["store_mem"]= [{
        "addr": reg_type(data["read_regs"]["int"][0]["value"] + reg_type(data["imm"][0])),
        "len": 1,
        "value": data["read_regs"]["int"][1]["value"]
    }]
    return data

def SH(data):
    data["store_mem"]= [{
        "addr": reg_type(data["read_regs"]["int"][0]["value"] + reg_type(data["imm"][0])),
        "len": 2,
        "value": data["read_regs"]["int"][1]["value"]
    }]
    return data

def SW(data):
    data["store_mem"]= [{
        "addr": reg_type(data["read_regs"]["int"][0]["value"] + reg_type(data["imm"][0])),
        "len": 4,
        "value": data["read_regs"]["int"][1]["value"]
    }]
    return data

def SD(data):
    data["store_mem"]= [{
        "addr": reg_type(data["read_regs"]["int"][0]["value"] + reg_type(data["imm"][0])),
        "len": 8,
        "value": data["read_regs"]["int"][1]["value"]
    }]
    return data

def ADDI(data):
    data["write_regs"]["int"][0]["value"] = reg_type(data["read_regs"]["int"][0]["value"] + reg_type(data["imm"][0]))
    return data

def SLTI(data):
    data["write_regs"]["int"][0]["value"] = reg_type(1 if data["read_regs"]["int"][0]["value"] < data["imm"][0] else 0)
    return data

def SLTIU(data):
    data["write_regs"]["int"][0]["value"] = reg_type(1 if data["read_regs"]["int"][0]["value"] < reg_type(data["imm"][0]) else 0)
    return data

def XORI(data):
    data["write_regs"]["int"][0]["value"] = reg_type(data["read_regs"]["int"][0]["value"] ^ reg_type(data["imm"][0]))
    return data

def ORI(data):
    data["write_regs"]["int"][0]["value"] = reg_type(data["read_regs"]["int"][0]["value"] | reg_type(data["imm"][0]))
    return data

def ANDI(data):
    data["write_regs"]["int"][0]["value"] = reg_type(data["read_regs"]["int"][0]["value"] & reg_type(data["imm"][0]))
    return data

def SLLI(data):
    data["write_regs"]["int"][0]["value"] = reg_type(data["read_regs"]["int"][0]["value"] << reg_type(data["imm"][0]))
    return data

# todo: comliment highest bit
def SRLI(data):
    data["write_regs"]["int"][0]["value"] = reg_type(data["read_regs"]["int"][0]["value"] >> reg_type(data["imm"][0]))

def SRAI(data):
    data["write_regs"]["int"][0]["value"] = reg_type(data["read_regs"]["int"][0]["value"] >> reg_type(data["imm"][0]))
    return data

def ADD(data):
    data["write_regs"]["int"][0]["value"] = reg_type(data["read_regs"]["int"][0]["value"] + data["read_regs"]["int"][1]["value"])
    return data

def SUB(data):
    data["write_regs"]["int"][0]["value"] = reg_type(data["read_regs"]["int"][0]["value"] - data["read_regs"]["int"][1]["value"])
    return data

def SLL(data):
    data["write_regs"]["int"][0]["value"] = reg_type(data["read_regs"]["int"][0]["value"] << data["read_regs"]["int"][1]["value"] )
    return data

def SLT(data):
    data["write_regs"]["int"][0]["value"] = reg_type(1 if data["read_regs"]["int"][0]["value"] < data["read_regs"]["int"][1]["value"] else 0)
    return data

def SLTU(data):
    data["write_regs"]["int"][0]["value"] = reg_type(1 if data["read_regs"]["int"][0]["value"] < data["read_regs"]["int"][1]["value"] else 0)
    return data

def XOR(data):
    data["write_regs"]["int"][0]["value"] = reg_type(data["read_regs"]["int"][0]["value"] ^ data["read_regs"]["int"][1]["value"])
    return data

# shift right logic
# todo
def SRL(data):
    data["write_regs"]["int"][0]["value"] = reg_type(data["read_regs"]["int"][0]["value"] ^ data["read_regs"]["int"][1]["value"])
    return data

def SRA(data):
    data["write_regs"]["int"][0]["value"] = reg_type(data["read_regs"]["int"][0]["value"] ^ data["read_regs"]["int"][1]["value"])
    return data

def OR(data):
    data["write_regs"]["int"][0]["value"] = reg_type(data["read_regs"]["int"][0]["value"] | data["read_regs"]["int"][1]["value"])
    return data

def AND(data):
    data["write_regs"]["int"][0]["value"] = reg_type(data["read_regs"]["int"][0]["value"] & data["read_regs"]["int"][1]["value"])
    return data

def MUL(data):
    data["write_regs"]["int"][0]["value"] = reg_type(data["read_regs"]["int"][0]["value"] * data["read_regs"]["int"][1]["value"])
    return data

def MULH(data):
    data["write_regs"]["int"][0]["value"] = reg_type( (data["read_regs"]["int"][0]["value"] * data["read_regs"]["int"][1]["value"]) >> 32)
    return data

def MULHSU(data):
    data["write_regs"]["int"][0]["value"] = reg_type( (data["read_regs"]["int"][0]["value"] * data["read_regs"]["int"][1]["value"]) >> 32)
    return data

def MULHU(data):
    data["write_regs"]["int"][0]["value"] = reg_type( (data["read_regs"]["int"][0]["value"] * data["read_regs"]["int"][1]["value"]) >> 32)
    return data

def DIV(data):
    data["write_regs"]["int"][0]["value"] = reg_type( data["read_regs"]["int"][0]["value"] / data["read_regs"]["int"][1]["value"])
    return data

def DIVU(data):
    data["write_regs"]["int"][0]["value"] = reg_type( data["read_regs"]["int"][0]["value"] / data["read_regs"]["int"][1]["value"])
    return data

def REM(data):
    data["write_regs"]["int"][0]["value"] = reg_type( data["read_regs"]["int"][0]["value"] % data["read_regs"]["int"][1]["value"])
    return data

def REMU(data):
    data["write_regs"]["int"][0]["value"] = reg_type( data["read_regs"]["int"][0]["value"] % data["read_regs"]["int"][1]["value"])
    return data

def FENCE(data):
    warnings.warn("not supported", UserWarning)
    return data

def FENCEI(data):
    warnings.warn("not supported", UserWarning)
    return data

def ECALL(data):
    warnings.warn("not supported", UserWarning)
    return data

def EBREAK(data):
    warnings.warn("not supported", UserWarning)
    return data

def URET(data):
    data["next_pc"] = data["read_regs"]["csr"][0]["value"] 
    warnings.warn("not supported", UserWarning)
    return data

def SRET(data):
    data["next_pc"] = data["read_regs"]["csr"][0]["value"] 
    warnings.warn("not supported", UserWarning)
    return data

# mret
# pc = CSRs[mepc]
# previllage = CSRs[mstatus].MPP, 
# CSRs[mstatus].MIE = CSRs[mstatus].MPIE, 
# CSRs[mstatus].MPIE =1
def MRET(data):
    # pc = CSRs[mepc]
    data["next_pc"] = data["read_regs"]["csr"][0]["value"] 
    # previllage = CSRs[mstatus].MPP
    warnings.warn("not supported: no previllage definition yet", UserWarning)
    # TODO: temp
    del data['write_regs'] 
    
    # CSRs[mstatus].MIE = CSRs[mstatus].MPIE, 
    # data["write_regs"]["csr"][0]["value"] = data["read_regs"]["csr"][1]["value"]
    # CSRs[mstatus].MPIE =1
    # data["write_regs"]["csr"][0]["value"] = reg_type(1)
    return data

def WFI(data):
    warnings.warn("not supported", UserWarning)
    return data

def SFENCEVMA(data):
    warnings.warn("not supported", UserWarning)
    return data

# register sequence:
# csr/int/fp/other
def CSRRW(data):
    # rd = csr 
    data["write_regs"]["int"][0]["value"] = data["read_regs"]["csr"][0]["value"]
    # csr = rs1
    data["write_regs"]["csr"][0]["value"] = data["read_regs"]["int"][0]["value"]
    return data

def CSRRS(data):
    # rd = csr
    data["write_regs"]["int"][0]["value"] = data["read_regs"]["csr"][0]["value"]
    # csr = (rs1 | csr)
    data["write_regs"]["csr"][0]["value"] = data["read_regs"]["int"][0]["value"] | data["read_regs"]["csr"][0]["value"]
    return data

def CSRRC(data):
    # rd = csr
    data["write_regs"]["int"][0]["value"] = data["read_regs"]["csr"][0]["value"]
    # csr = (rs1 & csr)
    data["write_regs"][0]["value"] = data["read_regs"]["int"][0]["value"] & data["read_regs"]["csr"][0]["value"]
    return data

def CSRRWI(data):
    # rd = csr
    data["write_regs"]["int"][0]["value"] = data["read_regs"]["csr"][0]["value"]
    # csr = imm
    data["write_regs"]["csr"][0]["value"] = reg_type(data["imm"][0])
    return data

def CSRRSI(data):
    # rd = csr
    data["write_regs"]["int"][0]["value"] = data["read_regs"]["csr"][0]["value"]
    # csr = (imm | csr)
    data["write_regs"]["csr"][0]["value"] = data["read_regs"]["csr"][0]["value"] | reg_type(data["imm"][0])
    return data

def CSRRCI(data):
    # rd = csr
    data["write_regs"]["int"][0]["value"] = data["read_regs"]["csr"][0]["value"]
    # csr = (imm & csr)
    data["write_regs"][0]["value"] = reg_type(data["imm"][0]) & data["read_regs"]["csr"][0]["value"]
    return data


def ADDIW(data):
    data["write_regs"]["int"][0]["value"] = reg_type(sext_word_type(data["read_regs"]["int"][0]["value"] + reg_type(data["imm"][0])))
    return data

def SLLIW(data):
    data["write_regs"]["int"][0]["value"] = reg_type(sext_word_type(data["read_regs"]["int"][0]["value"] << reg_type(data["imm"][0])))
    return data

def SRLIW(data):
    data["write_regs"]["int"][0]["value"] = reg_type(sext_word_type(data["read_regs"]["int"][0]["value"] >> reg_type(data["imm"][0])))
    return data

def SRAIW(data):
    data["write_regs"]["int"][0]["value"] = reg_type(sext_word_type(data["read_regs"]["int"][0]["value"] >> reg_type(data["imm"][0])))
    return data

def ADDW(data):
    data["write_regs"]["int"][0]["value"] = reg_type(sext_word_type(data["read_regs"]["int"][0]["value"] + data["read_regs"]["int"][1]["value"]))
    return data

def SUBW(data):
    data["write_regs"]["int"][0]["value"] = reg_type(sext_word_type(data["read_regs"]["int"][0]["value"] - data["read_regs"]["int"][1]["value"]))
    return data

def SLLW(data):
    data["write_regs"]["int"][0]["value"] = reg_type(sext_word_type(data["read_regs"]["int"][0]["value"] << data["read_regs"]["int"][1]["value"]))
    return data

def SRLW(data):
    data["write_regs"]["int"][0]["value"] = reg_type(sext_word_type(data["read_regs"]["int"][0]["value"] >> data["read_regs"]["int"][1]["value"]))
    return data

def SRAW(data):
    data["write_regs"]["int"][0]["value"] = reg_type(sext_word_type(data["read_regs"]["int"][0]["value"] ^ data["read_regs"]["int"][1]["value"]))
    return data

def MULW(data):
    data["write_regs"]["int"][0]["value"] = reg_type(sext_word_type(data["read_regs"]["int"][0]["value"] * data["read_regs"]["int"][1]["value"]))
    return data

def DIVW(data):
    data["write_regs"]["int"][0]["value"] = reg_type(sext_word_type(data["read_regs"]["int"][0]["value"] / data["read_regs"]["int"][1]["value"]))
    return data

def DIVUW(data):
    data["write_regs"]["int"][0]["value"] = reg_type(sext_word_type(data["read_regs"]["int"][0]["value"] / data["read_regs"]["int"][1]["value"]))
    return data

def REMW(data):
    data["write_regs"]["int"][0]["value"] = reg_type(sext_word_type(data["read_regs"]["int"][0]["value"] % data["read_regs"]["int"][1]["value"]))
    return data

def REMUW(data):
    data["write_regs"]["int"][0]["value"] = reg_type(sext_word_type(data["read_regs"]["int"][0]["value"] % data["read_regs"]["int"][1]["value"]))
    return data

# =============================================================

insn_dict = {}

with open("../config/insn_list_rv64i.txt") as insn_file:
    for line in insn_file:
        insn_name = line.split()[0]
        insn_dict[insn_name] = eval(insn_name)


