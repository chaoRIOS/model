import numpy as np


reg_type = np.uint32

def LUI(data):
    return data

def AUIPC(data):
    data["write_regs"][0]["value"] = reg_type(data["pc"] + data["imm"][0])
    return data

def JAL(data):
    data["next_pc"] = reg_type(data["pc"]+ data["imm"][0])
    data["write_regs"][0]["value"] = reg_type(data["pc"]+data["insn_len"])
    return data

def JALR(data):
    data["next_pc"] = reg_type((data["read_regs"][0] + data["imm"][0]) >> 1 << 1)
    data["write_regs"][0]["value"] = reg_type(data["pc"]+data["insn_len"])    
    return data

def BEQ(data):
    if data["read_regs"][0]["value"] == data["read_regs"][1]["value"]:
        data["next_pc"] = reg_type(data["pc"] + data["imm"][0])
    else:
        data["next_pc"] = reg_type(data["pc"] + data["insn_len"])
    return data

def BNE(data):
    if data["read_regs"][0]["value"] != data["read_regs"][1]["value"]:
        data["next_pc"] = reg_type(data["pc"] + data["imm"][0])
    else:
        data["next_pc"] = reg_type(data["pc"] + data["insn_len"])
    return data

def BLT(data):
    if data["read_regs"][0]["value"] < data["read_regs"][1]["value"]:
        data["next_pc"] = reg_type(data["pc"] + data["imm"][0])
    else:
        data["next_pc"] = reg_type(data["pc"] + data["insn_len"])
    return data

def BGE(data):
    if data["read_regs"][0]["value"] >= data["read_regs"][1]["value"]:
        data["next_pc"] = reg_type(data["pc"] + data["imm"][0])
    else:
        data["next_pc"] = reg_type(data["pc"] + data["insn_len"])
    return data

def BLTU(data):
    if data["read_regs"][0]["value"] < data["read_regs"][1]["value"]:
        data["next_pc"] = reg_type(data["pc"] + data["imm"][0])
    else:
        data["next_pc"] = reg_type(data["pc"] + data["insn_len"])
    return data

def BGEU(data):
    if data["read_regs"][0]["value"] >= data["read_regs"][1]["value"]:
        data["next_pc"] = reg_type(data["pc"] + data["imm"][0])
    else:
        data["next_pc"] = reg_type(data["pc"] + data["insn_len"])
    return data

def LB(data):

    return data

def LH(data):

    return data

def LW(data):

    return data

def LBU(data):

    return data

def LHU(data):

    return data

def LWU(data):

    return data

def LD(data):

    return data

def SB(data):

    return data

def SH(data):

    return data

def SW(data):

    return data

def SD(data):

    return data

def ADDI(data):

    return data

def SLTI(data):

    return data

def SLTIU(data):

    return data

def XORI(data):

    return data

def ORI(data):

    return data

def ANDI(data):

    return data

def SLLI(data):

    return data

def SRLI(data):

    return data

def SRAI(data):

    return data

def ADD(data):

    return data

def SUB(data):

    return data

def SLL(data):

    return data

def SLT(data):

    return data

def SLTU(data):

    return data

def XOR(data):

    return data

def SRL(data):

    return data

def SRA(data):

    return data

def OR(data):

    return data

def AND(data):

    return data

def MUL(data):

    return data

def MULH(data):

    return data

def MULHSU(data):

    return data

def MULHU(data):

    return data

def DIV(data):

    return data

def DIVU(data):

    return data

def REM(data):

    return data

def REMU(data):

    return data

def FENCE(data):

    return data

def FENCEI(data):

    return data

def ECALL(data):

    return data

def EBREAK(data):

    return data

def URET(data):

    return data

def SRET(data):

    return data

def MRET(data):

    return data

def WFI(data):

    return data

def SFENCEVMA(data):

    return data

def CSRRW(data):

    return data

def CSRRS(data):

    return data

def CSRRC(data):

    return data

def CSRRWI(data):

    return data

def CSRRSI(data):

    return data

def CSRRCI(data):

    return data

def ADDIW(data):

    return data

def SLLIW(data):

    return data

def SRLIW(data):

    return data

def SRAIW(data):

    return data

def ADDW(data):

    return data

def SUBW(data):

    return data

def SLLW(data):

    return data

def SRLW(data):

    return data

def SRAW(data):

    return data

def MULW(data):

    return data

def DIVW(data):

    return data

def DIVUW(data):

    return data

def REMW(data):

    return data

def REMUW(data):

    return data


