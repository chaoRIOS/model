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
    data["load_mem"]= [{
        "addr": reg_type(data["read_regs"][0]["value"] + data["imm"][0]),
        "len": 1
    }]
    return data

def LH(data):    
    data["load_mem"]= [{
        "addr": reg_type(data["read_regs"][0]["value"] + data["imm"][0]),
        "len": 2
    }]
    return data

def LW(data):
    data["load_mem"]= [{
        "addr": reg_type(data["read_regs"][0]["value"] + data["imm"][0]),
        "len": 4
    }]
    return data

def LBU(data):
    data["load_mem"]= [{
        "addr": reg_type(data["read_regs"][0]["value"] + data["imm"][0]),
        "len": 1
    }]
    return data

def LHU(data):
    data["load_mem"]= [{
        "addr": reg_type(data["read_regs"][0]["value"] + data["imm"][0]),
        "len": 2
    }]
    return data

def LWU(data):
    data["load_mem"]= [{
        "addr": reg_type(data["read_regs"][0]["value"] + data["imm"][0]),
        "len": 4
    }]
    return data

def LD(data):
    data["load_mem"]= [{
        "addr": reg_type(data["read_regs"][0]["value"] + data["imm"][0]),
        "len": 8
    }]
    return data

def SB(data):
    data["store_mem"]= [{
        "addr": reg_type(data["read_regs"][0]["value"] + data["imm"][0]),
        "len": 1,
        "value": data["read_regs"][1]["value"]
    }]
    return data

def SH(data):
    data["store_mem"]= [{
        "addr": reg_type(data["read_regs"][0]["value"] + data["imm"][0]),
        "len": 2,
        "value": data["read_regs"][1]["value"]
    }]
    return data

def SW(data):
    data["store_mem"][0]= [{
        "addr": reg_type(data["read_regs"][0]["value"] + data["imm"][0]),
        "len": 4,
        "value": data["read_regs"][1]["value"]
    }]
    return data

def SD(data):
    data["store_mem"][0]= [{
        "addr": reg_type(data["read_regs"][0]["value"] + data["imm"][0]),
        "len": 8,
        "value": data["read_regs"][1]["value"]
    }]
    return data

def ADDI(data):
    data["write_regs"][0]["value"] = reg_type(data["read_regs"][0]["value"] + data["imm"][0])
    return data

def SLTI(data):
    data["write_regs"][0]["value"] = reg_type(1 if data["read_regs"][0]["value"] < data["imm"][0] else 0)
    return data

def SLTIU(data):
    data["write_regs"][0]["value"] = reg_type(1 if data["read_regs"][0]["value"] < data["imm"][0] else 0)
    return data

def XORI(data):
    data["write_regs"][0]["value"] = reg_type(data["read_regs"][0]["value"] ^ data["imm"][0])
    return data

def ORI(data):
    data["write_regs"][0]["value"] = reg_type(data["read_regs"][0]["value"] | data["imm"][0])
    return data

def ANDI(data):
    data["write_regs"][0]["value"] = reg_type(data["read_regs"][0]["value"] & data["imm"][0])
    return data

def SLLI(data):
    data["write_regs"][0]["value"] = reg_type(data["read_regs"][0]["value"] << data["imm"][0])
    return data

# todo: comliment highest bit
def SRLI(data):
    data["write_regs"][0]["value"] = reg_type(data["read_regs"][0]["value"] >> data["imm"][0])

def SRAI(data):
    data["write_regs"][0]["value"] = reg_type(data["read_regs"][0]["value"] >> data["imm"][0])
    return data

def ADD(data):
    data["write_regs"][0]["value"] = reg_type(data["read_regs"][0]["value"] + data["read_regs"][1]["value"])
    return data

def SUB(data):
    data["write_regs"][0]["value"] = reg_type(data["read_regs"][0]["value"] - data["read_regs"][1]["value"])
    return data

def SLL(data):
    data["write_regs"][0]["value"] = reg_type(data["read_regs"][0]["value"] << data["read_regs"][1]["value"] )
    return data

def SLT(data):
    data["write_regs"][0]["value"] = reg_type(1 if data["read_regs"][0]["value"] < data["read_regs"][1]["value"] else 0)
    return data

def SLTU(data):
    data["write_regs"][0]["value"] = reg_type(1 if data["read_regs"][0]["value"] < data["read_regs"][1]["value"] else 0)
    return data

def XOR(data):
    data["write_regs"][0]["value"] = reg_type(data["read_regs"][0]["value"] ^ data["read_regs"][1]["value"])
    return data

# shift right logic
# todo
def SRL(data):
    data["write_regs"][0]["value"] = reg_type(data["read_regs"][0]["value"] ^ data["read_regs"][1]["value"])
    return data

def SRA(data):
    data["write_regs"][0]["value"] = reg_type(data["read_regs"][0]["value"] ^ data["read_regs"][1]["value"])
    return data

def OR(data):
    data["write_regs"][0]["value"] = reg_type(data["read_regs"][0]["value"] | data["read_regs"][1]["value"])
    return data

def AND(data):
    data["write_regs"][0]["value"] = reg_type(data["read_regs"][0]["value"] & data["read_regs"][1]["value"])
    return data

def MUL(data):
    data["write_regs"][0]["value"] = reg_type(data["read_regs"][0]["value"] * data["read_regs"][1]["value"])
    return data

def MULH(data):
    data["write_regs"][0]["value"] = reg_type( (data["read_regs"][0]["value"] * data["read_regs"][1]["value"]) >> 32)
    return data

def MULHSU(data):
    data["write_regs"][0]["value"] = reg_type( (data["read_regs"][0]["value"] * data["read_regs"][1]["value"]) >> 32)
    return data

def MULHU(data):
    data["write_regs"][0]["value"] = reg_type( (data["read_regs"][0]["value"] * data["read_regs"][1]["value"]) >> 32)
    return data

def DIV(data):
    data["write_regs"][0]["value"] = reg_type( data["read_regs"][0]["value"] / data["read_regs"][1]["value"])
    return data

def DIVU(data):
    data["write_regs"][0]["value"] = reg_type( data["read_regs"][0]["value"] / data["read_regs"][1]["value"])
    return data

def REM(data):
    data["write_regs"][0]["value"] = reg_type( data["read_regs"][0]["value"] % data["read_regs"][1]["value"])
    return data

def REMU(data):
    data["write_regs"][0]["value"] = reg_type( data["read_regs"][0]["value"] % data["read_regs"][1]["value"])
    return data

def FENCE(data):
    raise UserWarning("not supported")
    return data

def FENCEI(data):
    raise UserWarning("not supported")
    return data

def ECALL(data):
    raise UserWarning("not supported")
    return data

def EBREAK(data):
    raise UserWarning("not supported")
    return data

def URET(data):
    raise UserWarning("not supported")
    return data

def SRET(data):
    raise UserWarning("not supported")
    return data

# mret
# pc = CSRs[mepc]
# previllage = CSRs[mstatus].MPP, 
# CSRs[mstatus].MIE = CSRs[mstatus].MPIE, 
# CSRs[mstatus].MPIE =1
def MRET(data):
    # pc = CSRs[mepc]
    data["next_pc"] = data["read_regs"][0]["value"] 
    # previllage = CSRs[mstatus].MPP
    raise UserWarning("not supported: no previllage definition yet") 
    # CSRs[mstatus].MIE = CSRs[mstatus].MPIE, 
    data["write_regs"][0]["value"] = data["read_regs"][1]["value"]
    # CSRs[mstatus].MPIE =1
    data["write_regs"][1]["value"] = reg_type(1)
    return data

def WFI(data):
    raise UserWarning("not supported")
    return data

def SFENCEVMA(data):
    raise UserWarning("not supported")
    return data

# register sequence:
# csr/int/fp/other
def CSRRW(data):
    # rd = csr 
    data["write_regs"][1]["value"] = data["read_regs"][0]["value"]
    # csr = rs1
    data["write_regs"][0]["value"] = data["read_regs"][1]["value"]
    return data

def CSRRS(data):
    # rd = csr
    data["write_regs"][1]["value"] = data["read_regs"][0]["value"]
    # csr = (rs1 | csr)
    data["write_regs"][0]["value"] = data["read_regs"][1]["value"] | data["read_regs"][0]["value"]
    return data

def CSRRC(data):
    # rd = csr
    data["write_regs"][1]["value"] = data["read_regs"][0]["value"]
    # csr = (rs1 & csr)
    data["write_regs"][0]["value"] = data["read_regs"][1]["value"] & data["read_regs"][0]["value"]
    return data

def CSRRWI(data):
    # rd = csr
    data["write_regs"][1]["value"] = data["read_regs"][0]["value"]
    # csr = imm
    data["write_regs"][0]["value"] = data["imm"][0]
    return data

def CSRRSI(data):
    # rd = csr
    data["write_regs"][1]["value"] = data["read_regs"][0]["value"]
    # csr = (imm | csr)
    data["write_regs"][0]["value"] = data["imm"][0] | data["imm"][0]
    return data

def CSRRCI(data):
    # rd = csr
    data["write_regs"][1]["value"] = data["read_regs"][0]["value"]
    # csr = (imm & csr)
    data["write_regs"][0]["value"] = data["imm"][0] & data["read_regs"][0]["value"]
    return data


def ADDIW(data):
    data["write_regs"][0]["value"] = reg_type(data["read_regs"][0]["value"] + data["imm"][0])
    return data

def SLLIW(data):
    data["write_regs"][0]["value"] = reg_type(data["read_regs"][0]["value"] << data["imm"][0])
    return data

def SRLIW(data):
    data["write_regs"][0]["value"] = reg_type(data["read_regs"][0]["value"] >> data["imm"][0])
    return data

def SRAIW(data):
    data["write_regs"][0]["value"] = reg_type(data["read_regs"][0]["value"] >> data["imm"][0])
    return data

def ADDW(data):
    data["write_regs"][0]["value"] = reg_type(data["read_regs"][0]["value"] + data["read_regs"][1]["value"])
    return data

def SUBW(data):
    data["write_regs"][0]["value"] = reg_type(data["read_regs"][0]["value"] - data["read_regs"][1]["value"])
    return data

def SLLW(data):
    data["write_regs"][0]["value"] = reg_type(data["read_regs"][0]["value"] << data["read_regs"][1]["value"])
    return data

def SRLW(data):
    data["write_regs"][0]["value"] = reg_type(data["read_regs"][0]["value"] >> data["read_regs"][1]["value"])
    return data

def SRAW(data):
    data["write_regs"][0]["value"] = reg_type(data["read_regs"][0]["value"] ^ data["read_regs"][1]["value"])
    return data

def MULW(data):
    data["write_regs"][0]["value"] = reg_type(data["read_regs"][0]["value"] * data["read_regs"][1]["value"])
    return data

def DIVW(data):
    data["write_regs"][0]["value"] = reg_type( data["read_regs"][0]["value"] / data["read_regs"][1]["value"])
    return data

def DIVUW(data):
    data["write_regs"][0]["value"] = reg_type( data["read_regs"][0]["value"] / data["read_regs"][1]["value"])
    return data

def REMW(data):
    data["write_regs"][0]["value"] = reg_type( data["read_regs"][0]["value"] % data["read_regs"][1]["value"])
    return data

def REMUW(data):
    data["write_regs"][0]["value"] = reg_type( data["read_regs"][0]["value"] % data["read_regs"][1]["value"])
    return data


