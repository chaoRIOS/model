#![allow(unused)]
use crate::*;

pub fn decode_q00(i: u32) -> DecodingResult {
    match i >> 13 {
        0b000 if i == 0 => Ok(Instruction::Illegal),
        0b000 => Err(DecodingError::Unimplemented), // C.ADDI4SPN
        0b001 => Err(DecodingError::Unimplemented), // C.FLD
        0b010 => Ok(Instruction::Lw(IType(
            (((i & 0x1c00) << 13)      // imm[5:3]
            | ((i & 0x380) << 8)      // rs1[2:0]
            | ((i & 0x40) << 16)      // imm[2]
            | ((i & 0x20) << 21)      // imm[6]
            | ((i & 0x1c) << 5)       // rd[2:0]
            | 0b_01000_010_01000_0000011) as u64,
        ))),
        0b011 => Ok(Instruction::Ld(IType(
            // C.LD (C.FLW in RV32)
            (((i & 0x1c00) << 13)      // imm[5:3]
            | ((i & 0x380) << 8)      // rs1[2:0]
            | ((i & 0x60) << 21)      // imm[7:6]
            | ((i & 0x1c) << 5)       // rd[2:0]
            | 0b_01000_011_01000_0000011) as u64,
        ))),
        0b100 => Err(DecodingError::Unimplemented), // reserved
        0b101 => Err(DecodingError::Unimplemented), // C.FSD
        0b110 => Ok(Instruction::Sw(SType(
            // C.SW
            (((i & 0x1000) << 13)      // imm[5]
            | ((i & 0xc00))           // imm[4:3]
            | ((i & 0x380) << 8)      // rs1[2:0]
            | ((i & 0x40) << 3)       // imm[2]
            | ((i & 0x20) << 21)      // imm[6]
            | ((i & 0x1c) << 18)      // rs2[2:0]
            | 0b_01000_01000_010_00000_0100011) as u64,
        ))),
        0b111 => Ok(Instruction::Sd(SType(
            // C.SD (C.FSW in RV32)
            (((i & 0x1000) << 13)      // imm[5]
            | ((i & 0xc00))           // imm[4:3]
            | ((i & 0x380) << 8)      // rs1[2:0]
            | ((i & 0x60) << 21)      // imm[7:6]
            | ((i & 0x1c) << 18)      // rs2[2:0]
            | 0b_01000_01000_011_00000_0100011) as u64,
        ))),
        _ => Err(DecodingError::Unimplemented),
    }
}

pub fn decode_q01(_i: u32) -> DecodingResult {
    Err(DecodingError::Unimplemented)
}

pub fn decode_q10(_i: u32) -> DecodingResult {
    Err(DecodingError::Unimplemented)
}

// @TODO: Optimize
pub fn uncompress(halfword: u32) -> u32 {
    let op = halfword & 0x3; // [1:0]
    let funct3 = (halfword >> 13) & 0x7; // [15:13]

    match op {
        0 => match funct3 {
            0 => {
                // C.ADDI4SPN
                // addi rd+8, x2, nzuimm
                let rd = (halfword >> 2) & 0x7; // [4:2]
                let nzuimm = ((halfword >> 7) & 0x30) | // nzuimm[5:4] <= [12:11]
                    ((halfword >> 1) & 0x3c0) | // nzuimm{9:6] <= [10:7]
                    ((halfword >> 4) & 0x4) | // nzuimm[2] <= [6]
                    ((halfword >> 2) & 0x8); // nzuimm[3] <= [5]
                                             // nzuimm == 0 is reserved instruction
                if nzuimm != 0 {
                    return (nzuimm << 20) | (2 << 15) | ((rd + 8) << 7) | 0x13;
                }
            }
            1 => {
                // @TODO: Support C.LQ for 128-bit
                // C.FLD for 32, 64-bit
                // fld rd+8, offset(rs1+8)
                let rd = (halfword >> 2) & 0x7; // [4:2]
                let rs1 = (halfword >> 7) & 0x7; // [9:7]
                let offset = ((halfword >> 7) & 0x38) | // offset[5:3] <= [12:10]
                    ((halfword << 1) & 0xc0); // offset[7:6] <= [6:5]
                return (offset << 20) | ((rs1 + 8) << 15) | (3 << 12) | ((rd + 8) << 7) | 0x7;
            }
            2 => {
                // C.LW
                // lw rd+8, offset(rs1+8)
                let rs1 = (halfword >> 7) & 0x7; // [9:7]
                let rd = (halfword >> 2) & 0x7; // [4:2]
                let offset = ((halfword >> 7) & 0x38) | // offset[5:3] <= [12:10]
                    ((halfword >> 4) & 0x4) | // offset[2] <= [6]
                    ((halfword << 1) & 0x40); // offset[6] <= [5]
                return (offset << 20) | ((rs1 + 8) << 15) | (2 << 12) | ((rd + 8) << 7) | 0x3;
            }
            3 => {
                // @TODO: Support C.FLW in 32-bit mode
                // C.LD in 64-bit mode
                // ld rd+8, offset(rs1+8)
                let rs1 = (halfword >> 7) & 0x7; // [9:7]
                let rd = (halfword >> 2) & 0x7; // [4:2]
                let offset = ((halfword >> 7) & 0x38) | // offset[5:3] <= [12:10]
                    ((halfword << 1) & 0xc0); // offset[7:6] <= [6:5]
                return (offset << 20) | ((rs1 + 8) << 15) | (3 << 12) | ((rd + 8) << 7) | 0x3;
            }
            4 => {
                // Reserved
            }
            5 => {
                // C.FSD
                // fsd rs2+8, offset(rs1+8)
                let rs1 = (halfword >> 7) & 0x7; // [9:7]
                let rs2 = (halfword >> 2) & 0x7; // [4:2]
                let offset = ((halfword >> 7) & 0x38) | // uimm[5:3] <= [12:10]
                    ((halfword << 1) & 0xc0); // uimm[7:6] <= [6:5]
                let imm11_5 = (offset >> 5) & 0x7f;
                let imm4_0 = offset & 0x1f;
                return (imm11_5 << 25)
                    | ((rs2 + 8) << 20)
                    | ((rs1 + 8) << 15)
                    | (3 << 12)
                    | (imm4_0 << 7)
                    | 0x27;
            }
            6 => {
                // C.SW
                // sw rs2+8, offset(rs1+8)
                let rs1 = (halfword >> 7) & 0x7; // [9:7]
                let rs2 = (halfword >> 2) & 0x7; // [4:2]
                let offset = ((halfword >> 7) & 0x38) | // offset[5:3] <= [12:10]
                    ((halfword << 1) & 0x40) | // offset[6] <= [5]
                    ((halfword >> 4) & 0x4); // offset[2] <= [6]
                let imm11_5 = (offset >> 5) & 0x7f;
                let imm4_0 = offset & 0x1f;
                return (imm11_5 << 25)
                    | ((rs2 + 8) << 20)
                    | ((rs1 + 8) << 15)
                    | (2 << 12)
                    | (imm4_0 << 7)
                    | 0x23;
            }
            7 => {
                // @TODO: Support C.FSW in 32-bit mode
                // C.SD
                // sd rs2+8, offset(rs1+8)
                let rs1 = (halfword >> 7) & 0x7; // [9:7]
                let rs2 = (halfword >> 2) & 0x7; // [4:2]
                let offset = ((halfword >> 7) & 0x38) | // uimm[5:3] <= [12:10]
                    ((halfword << 1) & 0xc0); // uimm[7:6] <= [6:5]
                let imm11_5 = (offset >> 5) & 0x7f;
                let imm4_0 = offset & 0x1f;
                return (imm11_5 << 25)
                    | ((rs2 + 8) << 20)
                    | ((rs1 + 8) << 15)
                    | (3 << 12)
                    | (imm4_0 << 7)
                    | 0x23;
            }
            _ => {} // Not happens
        },
        1 => {
            match funct3 {
                0 => {
                    let r = (halfword >> 7) & 0x1f; // [11:7]
                    let imm = match halfword & 0x1000 {
                        0x1000 => 0xffffffc0,
                        _ => 0
                    } | // imm[31:6] <= [12]
                    ((halfword >> 7) & 0x20) | // imm[5] <= [12]
                    ((halfword >> 2) & 0x1f); // imm[4:0] <= [6:2]
                    if r == 0 && imm == 0 {
                        // C.NOP
                        // addi x0, x0, 0
                        return 0x13;
                    } else if r != 0 {
                        // C.ADDI
                        // addi r, r, imm
                        return (imm << 20) | (r << 15) | (r << 7) | 0x13;
                    }
                    // @TODO: Support HINTs
                    // r == 0 and imm != 0 is HINTs
                }
                1 => {
                    // @TODO: Support C.JAL in 32-bit mode
                    // C.ADDIW
                    // addiw r, r, imm
                    let r = (halfword >> 7) & 0x1f;
                    let imm = match halfword & 0x1000 {
                        0x1000 => 0xffffffc0,
                        _ => 0
                    } | // imm[31:6] <= [12]
                    ((halfword >> 7) & 0x20) | // imm[5] <= [12]
                    ((halfword >> 2) & 0x1f); // imm[4:0] <= [6:2]
                    if r != 0 {
                        return (imm << 20) | (r << 15) | (r << 7) | 0x1b;
                    }
                    // r == 0 is reserved instruction
                }
                2 => {
                    // C.LI
                    // addi rd, x0, imm
                    let r = (halfword >> 7) & 0x1f;
                    let imm = match halfword & 0x1000 {
                        0x1000 => 0xffffffc0,
                        _ => 0
                    } | // imm[31:6] <= [12]
                    ((halfword >> 7) & 0x20) | // imm[5] <= [12]
                    ((halfword >> 2) & 0x1f); // imm[4:0] <= [6:2]
                    if r != 0 {
                        return (imm << 20) | (r << 7) | 0x13;
                    }
                    // @TODO: Support HINTs
                    // r == 0 is for HINTs
                }
                3 => {
                    let r = (halfword >> 7) & 0x1f; // [11:7]
                    if r == 2 {
                        // C.ADDI16SP
                        // addi r, r, nzimm
                        let imm = match halfword & 0x1000 {
                            0x1000 => 0xfffffc00,
                            _ => 0
                        } | // imm[31:10] <= [12]
                        ((halfword >> 3) & 0x200) | // imm[9] <= [12]
                        ((halfword >> 2) & 0x10) | // imm[4] <= [6]
                        ((halfword << 1) & 0x40) | // imm[6] <= [5]
                        ((halfword << 4) & 0x180) | // imm[8:7] <= [4:3]
                        ((halfword << 3) & 0x20); // imm[5] <= [2]
                        if imm != 0 {
                            return (imm << 20) | (r << 15) | (r << 7) | 0x13;
                        }
                        // imm == 0 is for reserved instruction
                    }
                    if r != 0 && r != 2 {
                        // C.LUI
                        // lui r, nzimm
                        let nzimm = match halfword & 0x1000 {
                            0x1000 => 0xfffc0000,
                            _ => 0
                        } | // nzimm[31:18] <= [12]
                        ((halfword << 5) & 0x20000) | // nzimm[17] <= [12]
                        ((halfword << 10) & 0x1f000); // nzimm[16:12] <= [6:2]
                        if nzimm != 0 {
                            return nzimm | (r << 7) | 0x37;
                        }
                        // nzimm == 0 is for reserved instruction
                    }
                }
                4 => {
                    let funct2 = (halfword >> 10) & 0x3; // [11:10]
                    match funct2 {
                        0 => {
                            // C.SRLI
                            // c.srli rs1+8, rs1+8, shamt
                            let shamt = ((halfword >> 7) & 0x20) | // shamt[5] <= [12]
                                ((halfword >> 2) & 0x1f); // shamt[4:0] <= [6:2]
                            let rs1 = (halfword >> 7) & 0x7; // [9:7]
                            return (shamt << 20)
                                | ((rs1 + 8) << 15)
                                | (5 << 12)
                                | ((rs1 + 8) << 7)
                                | 0x13;
                        }
                        1 => {
                            // C.SRAI
                            // srai rs1+8, rs1+8, shamt
                            let shamt = ((halfword >> 7) & 0x20) | // shamt[5] <= [12]
                                ((halfword >> 2) & 0x1f); // shamt[4:0] <= [6:2]
                            let rs1 = (halfword >> 7) & 0x7; // [9:7]
                            return (0x20 << 25)
                                | (shamt << 20)
                                | ((rs1 + 8) << 15)
                                | (5 << 12)
                                | ((rs1 + 8) << 7)
                                | 0x13;
                        }
                        2 => {
                            // C.ANDI
                            // andi, r+8, r+8, imm
                            let r = (halfword >> 7) & 0x7; // [9:7]
                            let imm = match halfword & 0x1000 {
                                0x1000 => 0xffffffc0,
                                _ => 0
                            } | // imm[31:6] <= [12]
                            ((halfword >> 7) & 0x20) | // imm[5] <= [12]
                            ((halfword >> 2) & 0x1f); // imm[4:0] <= [6:2]
                            return (imm << 20)
                                | ((r + 8) << 15)
                                | (7 << 12)
                                | ((r + 8) << 7)
                                | 0x13;
                        }
                        3 => {
                            let funct1 = (halfword >> 12) & 1; // [12]
                            let funct2_2 = (halfword >> 5) & 0x3; // [6:5]
                            let rs1 = (halfword >> 7) & 0x7;
                            let rs2 = (halfword >> 2) & 0x7;
                            match funct1 {
                                0 => match funct2_2 {
                                    0 => {
                                        // C.SUB
                                        // sub rs1+8, rs1+8, rs2+8
                                        return (0x20 << 25)
                                            | ((rs2 + 8) << 20)
                                            | ((rs1 + 8) << 15)
                                            | ((rs1 + 8) << 7)
                                            | 0x33;
                                    }
                                    1 => {
                                        // C.XOR
                                        // xor rs1+8, rs1+8, rs2+8
                                        return ((rs2 + 8) << 20)
                                            | ((rs1 + 8) << 15)
                                            | (4 << 12)
                                            | ((rs1 + 8) << 7)
                                            | 0x33;
                                    }
                                    2 => {
                                        // C.OR
                                        // or rs1+8, rs1+8, rs2+8
                                        return ((rs2 + 8) << 20)
                                            | ((rs1 + 8) << 15)
                                            | (6 << 12)
                                            | ((rs1 + 8) << 7)
                                            | 0x33;
                                    }
                                    3 => {
                                        // C.AND
                                        // and rs1+8, rs1+8, rs2+8
                                        return ((rs2 + 8) << 20)
                                            | ((rs1 + 8) << 15)
                                            | (7 << 12)
                                            | ((rs1 + 8) << 7)
                                            | 0x33;
                                    }
                                    _ => {} // Not happens
                                },
                                1 => match funct2_2 {
                                    0 => {
                                        // C.SUBW
                                        // subw r1+8, r1+8, r2+8
                                        return (0x20 << 25)
                                            | ((rs2 + 8) << 20)
                                            | ((rs1 + 8) << 15)
                                            | ((rs1 + 8) << 7)
                                            | 0x3b;
                                    }
                                    1 => {
                                        // C.ADDW
                                        // addw r1+8, r1+8, r2+8
                                        return ((rs2 + 8) << 20)
                                            | ((rs1 + 8) << 15)
                                            | ((rs1 + 8) << 7)
                                            | 0x3b;
                                    }
                                    2 => {
                                        // Reserved
                                    }
                                    3 => {
                                        // Reserved
                                    }
                                    _ => {} // Not happens
                                },
                                _ => {} // No happens
                            };
                        }
                        _ => {} // not happens
                    };
                }
                5 => {
                    // C.J
                    // jal x0, imm
                    let offset = match halfword & 0x1000 {
                            0x1000 => 0xfffff000,
                            _ => 0
                        } | // offset[31:12] <= [12]
                        ((halfword >> 1) & 0x800) | // offset[11] <= [12]
                        ((halfword >> 7) & 0x10) | // offset[4] <= [11]
                        ((halfword >> 1) & 0x300) | // offset[9:8] <= [10:9]
                        ((halfword << 2) & 0x400) | // offset[10] <= [8]
                        ((halfword >> 1) & 0x40) | // offset[6] <= [7]
                        ((halfword << 1) & 0x80) | // offset[7] <= [6]
                        ((halfword >> 2) & 0xe) | // offset[3:1] <= [5:3]
                        ((halfword << 3) & 0x20); // offset[5] <= [2]
                    let imm = ((offset >> 1) & 0x80000) | // imm[19] <= offset[20]
                        ((offset << 8) & 0x7fe00) | // imm[18:9] <= offset[10:1]
                        ((offset >> 3) & 0x100) | // imm[8] <= offset[11]
                        ((offset >> 12) & 0xff); // imm[7:0] <= offset[19:12]
                    return (imm << 12) | 0x6f;
                }
                6 => {
                    // C.BEQZ
                    // beq r+8, x0, offset
                    let r = (halfword >> 7) & 0x7;
                    let offset = match halfword & 0x1000 {
                            0x1000 => 0xfffffe00,
                            _ => 0
                        } | // offset[31:9] <= [12]
                        ((halfword >> 4) & 0x100) | // offset[8] <= [12]
                        ((halfword >> 7) & 0x18) | // offset[4:3] <= [11:10]
                        ((halfword << 1) & 0xc0) | // offset[7:6] <= [6:5]
                        ((halfword >> 2) & 0x6) | // offset[2:1] <= [4:3]
                        ((halfword << 3) & 0x20); // offset[5] <= [2]
                    let imm2 = ((offset >> 6) & 0x40) | // imm2[6] <= [12]
                        ((offset >> 5) & 0x3f); // imm2[5:0] <= [10:5]
                    let imm1 = (offset & 0x1e) | // imm1[4:1] <= [4:1]
                        ((offset >> 11) & 0x1); // imm1[0] <= [11]
                    return (imm2 << 25) | ((r + 8) << 20) | (imm1 << 7) | 0x63;
                }
                7 => {
                    // C.BNEZ
                    // bne r+8, x0, offset
                    let r = (halfword >> 7) & 0x7;
                    let offset = match halfword & 0x1000 {
                            0x1000 => 0xfffffe00,
                            _ => 0
                        } | // offset[31:9] <= [12]
                        ((halfword >> 4) & 0x100) | // offset[8] <= [12]
                        ((halfword >> 7) & 0x18) | // offset[4:3] <= [11:10]
                        ((halfword << 1) & 0xc0) | // offset[7:6] <= [6:5]
                        ((halfword >> 2) & 0x6) | // offset[2:1] <= [4:3]
                        ((halfword << 3) & 0x20); // offset[5] <= [2]
                    let imm2 = ((offset >> 6) & 0x40) | // imm2[6] <= [12]
                        ((offset >> 5) & 0x3f); // imm2[5:0] <= [10:5]
                    let imm1 = (offset & 0x1e) | // imm1[4:1] <= [4:1]
                        ((offset >> 11) & 0x1); // imm1[0] <= [11]
                    return (imm2 << 25) | ((r + 8) << 20) | (1 << 12) | (imm1 << 7) | 0x63;
                }
                _ => {} // No happens
            };
        }
        2 => {
            match funct3 {
                0 => {
                    // C.SLLI
                    // slli r, r, shamt
                    let r = (halfword >> 7) & 0x1f;
                    let shamt = ((halfword >> 7) & 0x20) | // imm[5] <= [12]
                        ((halfword >> 2) & 0x1f); // imm[4:0] <= [6:2]
                    if r != 0 {
                        return (shamt << 20) | (r << 15) | (1 << 12) | (r << 7) | 0x13;
                    }
                    // r == 0 is reserved instruction?
                }
                1 => {
                    // C.FLDSP
                    // fld rd, offset(x2)
                    let rd = (halfword >> 7) & 0x1f;
                    let offset = ((halfword >> 7) & 0x20) | // offset[5] <= [12]
                        ((halfword >> 2) & 0x18) | // offset[4:3] <= [6:5]
                        ((halfword << 4) & 0x1c0); // offset[8:6] <= [4:2]
                    if rd != 0 {
                        return (offset << 20) | (2 << 15) | (3 << 12) | (rd << 7) | 0x7;
                    }
                    // rd == 0 is reseved instruction
                }
                2 => {
                    // C.LWSP
                    // lw r, offset(x2)
                    let r = (halfword >> 7) & 0x1f;
                    let offset = ((halfword >> 7) & 0x20) | // offset[5] <= [12]
                        ((halfword >> 2) & 0x1c) | // offset[4:2] <= [6:4]
                        ((halfword << 4) & 0xc0); // offset[7:6] <= [3:2]
                    if r != 0 {
                        return (offset << 20) | (2 << 15) | (2 << 12) | (r << 7) | 0x3;
                    }
                    // r == 0 is reseved instruction
                }
                3 => {
                    // @TODO: Support C.FLWSP in 32-bit mode
                    // C.LDSP
                    // ld rd, offset(x2)
                    let rd = (halfword >> 7) & 0x1f;
                    let offset = ((halfword >> 7) & 0x20) | // offset[5] <= [12]
                        ((halfword >> 2) & 0x18) | // offset[4:3] <= [6:5]
                        ((halfword << 4) & 0x1c0); // offset[8:6] <= [4:2]
                    if rd != 0 {
                        return (offset << 20) | (2 << 15) | (3 << 12) | (rd << 7) | 0x3;
                    }
                    // rd == 0 is reseved instruction
                }
                4 => {
                    let funct1 = (halfword >> 12) & 1; // [12]
                    let rs1 = (halfword >> 7) & 0x1f; // [11:7]
                    let rs2 = (halfword >> 2) & 0x1f; // [6:2]
                    match funct1 {
                        0 => {
                            if rs1 != 0 && rs2 == 0 {
                                // C.JR
                                // jalr x0, 0(rs1)
                                return (rs1 << 15) | 0x67;
                            }
                            // rs1 == 0 is reserved instruction
                            if rs1 != 0 && rs2 != 0 {
                                // C.MV
                                // add rs1, x0, rs2
                                // println!("C.MV RS1:{:x} RS2:{:x}", rs1, rs2);
                                return (rs2 << 20) | (rs1 << 7) | 0x33;
                            }
                            // rs1 == 0 && rs2 != 0 is Hints
                            // @TODO: Support Hints
                        }
                        1 => {
                            if rs1 == 0 && rs2 == 0 {
                                // C.EBREAK
                                // ebreak
                                return 0x00100073;
                            }
                            if rs1 != 0 && rs2 == 0 {
                                // C.JALR
                                // jalr x1, 0(rs1)
                                return (rs1 << 15) | (1 << 7) | 0x67;
                            }
                            if rs1 != 0 && rs2 != 0 {
                                // C.ADD
                                // add rs1, rs1, rs2
                                return (rs2 << 20) | (rs1 << 15) | (rs1 << 7) | 0x33;
                            }
                            // rs1 == 0 && rs2 != 0 is Hists
                            // @TODO: Supports Hinsts
                        }
                        _ => {} // Not happens
                    };
                }
                5 => {
                    // @TODO: Implement
                    // C.FSDSP
                    // fsd rs2, offset(x2)
                    let rs2 = (halfword >> 2) & 0x1f; // [6:2]
                    let offset = ((halfword >> 7) & 0x38) | // offset[5:3] <= [12:10]
                        ((halfword >> 1) & 0x1c0); // offset[8:6] <= [9:7]
                    let imm11_5 = (offset >> 5) & 0x3f;
                    let imm4_0 = offset & 0x1f;
                    return (imm11_5 << 25)
                        | (rs2 << 20)
                        | (2 << 15)
                        | (3 << 12)
                        | (imm4_0 << 7)
                        | 0x27;
                }
                6 => {
                    // C.SWSP
                    // sw rs2, offset(x2)
                    let rs2 = (halfword >> 2) & 0x1f; // [6:2]
                    let offset = ((halfword >> 7) & 0x3c) | // offset[5:2] <= [12:9]
                        ((halfword >> 1) & 0xc0); // offset[7:6] <= [8:7]
                    let imm11_5 = (offset >> 5) & 0x3f;
                    let imm4_0 = offset & 0x1f;
                    return (imm11_5 << 25)
                        | (rs2 << 20)
                        | (2 << 15)
                        | (2 << 12)
                        | (imm4_0 << 7)
                        | 0x23;
                }
                7 => {
                    // @TODO: Support C.FSWSP in 32-bit mode
                    // C.SDSP
                    // sd rs, offset(x2)
                    let rs2 = (halfword >> 2) & 0x1f; // [6:2]
                    let offset = ((halfword >> 7) & 0x38) | // offset[5:3] <= [12:10]
                        ((halfword >> 1) & 0x1c0); // offset[8:6] <= [9:7]
                    let imm11_5 = (offset >> 5) & 0x3f;
                    let imm4_0 = offset & 0x1f;
                    return (imm11_5 << 25)
                        | (rs2 << 20)
                        | (2 << 15)
                        | (3 << 12)
                        | (imm4_0 << 7)
                        | 0x23;
                }
                _ => {} // Not happens
            };
        }
        _ => {} // No happnes
    };
    0xffffffff // Return invalid value
}

#[cfg(test)]
mod tests {
    use super::Instruction::*;
    use super::*;

    #[test]
    fn q00() {
        assert_eq!(decode_q00(0x6188).unwrap(), Ld(IType(0x0005b503))); // ld a0,0(a1)
        assert_eq!(decode_q00(0x75e0).unwrap(), Ld(IType(0x0e85b403))); // ld s0,232(a1)
        assert_eq!(decode_q00(0x43b0).unwrap(), Lw(IType(0x0407a603))); // lw a2,64(a5)
        assert_eq!(decode_q00(0xe188).unwrap(), Sd(SType(0x00a5b023))); // sd a0,0(a1)
        assert_eq!(decode_q00(0xf5e0).unwrap(), Sd(SType(0x0e85b423))); // sd s0,232(a1)
        assert_eq!(decode_q00(0xc3b0).unwrap(), Sw(SType(0x04c7a023))); // sw a2,64(a5)
    }
}
