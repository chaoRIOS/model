use pyo3::class::basic::PyObjectProtocol;
use pyo3::prelude::*;

use crate::csr_address;
use crate::decode;
use crate::instruction::Instruction;

#[pyclass]
pub struct DecodingResultPy {
    #[pyo3(get)]
    pub inst: Option<InstructionPy>,
    #[pyo3(get)]
    pub decode_error: Option<String>,
}

#[pymethods]
impl DecodingResultPy {
    #[new]
    pub fn new() -> Self {
        DecodingResultPy {
            inst: None,
            decode_error: None,
        }
    }
}

#[pyproto]
impl PyObjectProtocol for DecodingResultPy {
    fn __str__(&self) -> PyResult<String> {
        Ok(match &self.inst {
            Some(inst) => {
                format!(
                "Instruction:\n\tname:\t{:?}\n\timm:\t{:x?}\n\tzimm:\t{:x?}\n\tshamt:\t{:?}\n\tpred_succ:\t{:?}\n\tread_reg:\t{:?}\n\twrite_reg:\t{:?}\nError:\n\t{:?}",
                inst.name,
                inst.imm,
                inst.zimm,
                inst.shamt,
                inst.pred_succ,
                inst.read_reg,
                inst.write_reg,
                self.decode_error
            )
            }
            None => format!("{:?}", self.decode_error),
        })
    }
}

#[pyclass]
#[derive(Clone)]
pub struct InstructionPy {
    #[pyo3(get)]
    pub name: String,
    #[pyo3(get)]
    pub imm: Option<i64>,
    #[pyo3(get)]
    pub zimm: Option<u64>,
    #[pyo3(get)]
    pub shamt: Option<i64>,
    #[pyo3(get)]
    pub pred_succ: Option<(u64, u64)>,
    #[pyo3(get)]
    pub read_reg: Option<Vec<(String, u64)>>,
    #[pyo3(get)]
    pub write_reg: Option<Vec<(String, u64)>>,
    // @TODO: Load/Store decoding
    // #[pyo3(get)]
    // pub load_mem: Option<Vec<(u64, u64)>>,
    // #[pyo3(get)]
    // pub store_mem: Option<Vec<(u64, u64)>>,
}

#[pymethods]
impl InstructionPy {
    #[new]
    pub fn new() -> Self {
        InstructionPy {
            name: String::from(""),
            imm: None,
            zimm: None,
            shamt: None,
            pred_succ: None,
            read_reg: None,
            write_reg: None,
            // load_mem: None,
            // store_mem: None,
        }
    }
}

/// -------------------
///
/// Python wrapper
///
/// -------------------
#[pymodule]
fn rustdecoder(_py: Python, m: &PyModule) -> PyResult<()> {
    #[pyfn(m)]
    #[pyo3(name = "decode_instruction")]
    fn decode_instruction_py(_py: Python, word: u32) -> PyResult<DecodingResultPy> {
        let mut out = DecodingResultPy::new();
        match decode(word) {
            Ok(inst) => {
                // out.inst = Some(InstructionPy::new());

                let mut result_inst = InstructionPy::new();
                match inst {
                    // LUI
                    Instruction::Lui(u_type_inst) => {
                        result_inst.imm = Some(u_type_inst.imm() as i64);
                        result_inst.write_reg = Some(vec![(String::from("int"), u_type_inst.rd())]);
                        result_inst.name = String::from("LUI");
                    }

                    // AUIPC
                    Instruction::Auipc(u_type_inst) => {
                        result_inst.imm = Some(u_type_inst.imm() as i64);
                        result_inst.write_reg = Some(vec![(String::from("int"), u_type_inst.rd())]);
                        result_inst.name = String::from("AUIPC");
                    }

                    // Jal
                    Instruction::Jal(j_type_inst) => {
                        result_inst.imm = Some(j_type_inst.imm() as i64);
                        result_inst.write_reg = Some(vec![(String::from("int"), j_type_inst.rd())]);
                        result_inst.name = String::from("JAL");
                    }

                    // Jalr
                    Instruction::Jalr(i_type_inst) => {
                        result_inst.imm = Some(i_type_inst.imm() as i64);
                        result_inst.read_reg = Some(vec![(String::from("int"), i_type_inst.rs1())]);
                        result_inst.write_reg = Some(vec![(String::from("int"), i_type_inst.rd())]);
                        result_inst.name = String::from("JALR");
                    }

                    // Branch
                    Instruction::Beq(b_type_inst) => {
                        result_inst.imm = Some(b_type_inst.imm() as i64);
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), b_type_inst.rs1()),
                            (String::from("int"), b_type_inst.rs2()),
                        ]);
                        result_inst.name = String::from("BEQ");
                    }
                    Instruction::Bne(b_type_inst) => {
                        result_inst.imm = Some(b_type_inst.imm() as i64);
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), b_type_inst.rs1()),
                            (String::from("int"), b_type_inst.rs2()),
                        ]);
                        result_inst.name = String::from("BNE");
                    }
                    Instruction::Blt(b_type_inst) => {
                        result_inst.imm = Some(b_type_inst.imm() as i64);
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), b_type_inst.rs1()),
                            (String::from("int"), b_type_inst.rs2()),
                        ]);
                        result_inst.name = String::from("BLT");
                    }
                    Instruction::Bge(b_type_inst) => {
                        result_inst.imm = Some(b_type_inst.imm() as i64);
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), b_type_inst.rs1()),
                            (String::from("int"), b_type_inst.rs2()),
                        ]);
                        result_inst.name = String::from("BGE");
                    }
                    Instruction::Bltu(b_type_inst) => {
                        result_inst.imm = Some(b_type_inst.imm() as i64);
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), b_type_inst.rs1()),
                            (String::from("int"), b_type_inst.rs2()),
                        ]);
                        result_inst.name = String::from("BLTU");
                    }
                    Instruction::Bgeu(b_type_inst) => {
                        result_inst.imm = Some(b_type_inst.imm() as i64);
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), b_type_inst.rs1()),
                            (String::from("int"), b_type_inst.rs2()),
                        ]);
                        result_inst.name = String::from("BGEU");
                    }

                    // Load
                    Instruction::Lb(i_type_inst) => {
                        result_inst.imm = Some(i_type_inst.imm() as i64);
                        result_inst.read_reg = Some(vec![(String::from("int"), i_type_inst.rs1())]);
                        result_inst.write_reg = Some(vec![(String::from("int"), i_type_inst.rd())]);
                        result_inst.name = String::from("LB");
                    }
                    Instruction::Lh(i_type_inst) => {
                        result_inst.imm = Some(i_type_inst.imm() as i64);
                        result_inst.read_reg = Some(vec![(String::from("int"), i_type_inst.rs1())]);
                        result_inst.write_reg = Some(vec![(String::from("int"), i_type_inst.rd())]);
                        result_inst.name = String::from("LH");
                    }
                    Instruction::Lw(i_type_inst) => {
                        result_inst.imm = Some(i_type_inst.imm() as i64);
                        result_inst.read_reg = Some(vec![(String::from("int"), i_type_inst.rs1())]);
                        result_inst.write_reg = Some(vec![(String::from("int"), i_type_inst.rd())]);
                        result_inst.name = String::from("LW");
                    }
                    Instruction::Lbu(i_type_inst) => {
                        result_inst.imm = Some(i_type_inst.imm() as i64);
                        result_inst.read_reg = Some(vec![(String::from("int"), i_type_inst.rs1())]);
                        result_inst.write_reg = Some(vec![(String::from("int"), i_type_inst.rd())]);
                        result_inst.name = String::from("LBU");
                    }
                    Instruction::Lhu(i_type_inst) => {
                        result_inst.imm = Some(i_type_inst.imm() as i64);
                        result_inst.read_reg = Some(vec![(String::from("int"), i_type_inst.rs1())]);
                        result_inst.write_reg = Some(vec![(String::from("int"), i_type_inst.rd())]);
                        result_inst.name = String::from("LHU");
                    }
                    Instruction::Lwu(i_type_inst) => {
                        result_inst.imm = Some(i_type_inst.imm() as i64);
                        result_inst.read_reg = Some(vec![(String::from("int"), i_type_inst.rs1())]);
                        result_inst.write_reg = Some(vec![(String::from("int"), i_type_inst.rd())]);
                        result_inst.name = String::from("LWU");
                    }
                    Instruction::Ld(i_type_inst) => {
                        result_inst.imm = Some(i_type_inst.imm() as i64);
                        result_inst.read_reg = Some(vec![(String::from("int"), i_type_inst.rs1())]);
                        result_inst.write_reg = Some(vec![(String::from("int"), i_type_inst.rd())]);
                        result_inst.name = String::from("LD");
                    }

                    // Store
                    Instruction::Sb(s_type_inst) => {
                        result_inst.imm = Some(s_type_inst.imm() as i64);
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), s_type_inst.rs1()),
                            (String::from("int"), s_type_inst.rs2()),
                        ]);
                        result_inst.name = String::from("SB");
                    }
                    Instruction::Sh(s_type_inst) => {
                        result_inst.imm = Some(s_type_inst.imm() as i64);
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), s_type_inst.rs1()),
                            (String::from("int"), s_type_inst.rs2()),
                        ]);
                        result_inst.name = String::from("SH");
                    }
                    Instruction::Sw(s_type_inst) => {
                        result_inst.imm = Some(s_type_inst.imm() as i64);
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), s_type_inst.rs1()),
                            (String::from("int"), s_type_inst.rs2()),
                        ]);
                        result_inst.name = String::from("SW");
                    }
                    Instruction::Sd(s_type_inst) => {
                        result_inst.imm = Some(s_type_inst.imm() as i64);
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), s_type_inst.rs1()),
                            (String::from("int"), s_type_inst.rs2()),
                        ]);
                        result_inst.name = String::from("SD");
                    }

                    // OP-imm
                    Instruction::Addi(i_type_inst) => {
                        result_inst.imm = Some(i_type_inst.imm() as i64);
                        result_inst.read_reg = Some(vec![(String::from("int"), i_type_inst.rs1())]);
                        result_inst.write_reg = Some(vec![(String::from("int"), i_type_inst.rd())]);
                        result_inst.name = String::from("ADDI");
                    }
                    Instruction::Slti(i_type_inst) => {
                        result_inst.imm = Some(i_type_inst.imm() as i64);
                        result_inst.read_reg = Some(vec![(String::from("int"), i_type_inst.rs1())]);
                        result_inst.write_reg = Some(vec![(String::from("int"), i_type_inst.rd())]);
                        result_inst.name = String::from("SLTI");
                    }
                    Instruction::Sltiu(i_type_inst) => {
                        result_inst.imm = Some(i_type_inst.imm() as i64);
                        result_inst.read_reg = Some(vec![(String::from("int"), i_type_inst.rs1())]);
                        result_inst.write_reg = Some(vec![(String::from("int"), i_type_inst.rd())]);
                        result_inst.name = String::from("SLTIU");
                    }
                    Instruction::Xori(i_type_inst) => {
                        result_inst.imm = Some(i_type_inst.imm() as i64);
                        result_inst.read_reg = Some(vec![(String::from("int"), i_type_inst.rs1())]);
                        result_inst.write_reg = Some(vec![(String::from("int"), i_type_inst.rd())]);
                        result_inst.name = String::from("XORI");
                    }
                    Instruction::Ori(i_type_inst) => {
                        result_inst.imm = Some(i_type_inst.imm() as i64);
                        result_inst.read_reg = Some(vec![(String::from("int"), i_type_inst.rs1())]);
                        result_inst.write_reg = Some(vec![(String::from("int"), i_type_inst.rd())]);
                        result_inst.name = String::from("ORI");
                    }
                    Instruction::Andi(i_type_inst) => {
                        result_inst.imm = Some(i_type_inst.imm() as i64);
                        result_inst.read_reg = Some(vec![(String::from("int"), i_type_inst.rs1())]);
                        result_inst.write_reg = Some(vec![(String::from("int"), i_type_inst.rd())]);
                        result_inst.name = String::from("ANDI");
                    }
                    Instruction::Slli(shift_type_inst) => {
                        result_inst.shamt = Some(shift_type_inst.shamt() as i64);
                        result_inst.read_reg =
                            Some(vec![(String::from("int"), shift_type_inst.rs1())]);
                        result_inst.write_reg =
                            Some(vec![(String::from("int"), shift_type_inst.rd())]);
                        result_inst.name = String::from("SLLI");
                    }
                    Instruction::Srli(shift_type_inst) => {
                        result_inst.shamt = Some(shift_type_inst.shamt() as i64);
                        result_inst.read_reg =
                            Some(vec![(String::from("int"), shift_type_inst.rs1())]);
                        result_inst.write_reg =
                            Some(vec![(String::from("int"), shift_type_inst.rd())]);
                        result_inst.name = String::from("SRLI");
                    }
                    Instruction::Srai(shift_type_inst) => {
                        result_inst.shamt = Some(shift_type_inst.shamt() as i64);
                        result_inst.read_reg =
                            Some(vec![(String::from("int"), shift_type_inst.rs1())]);
                        result_inst.write_reg =
                            Some(vec![(String::from("int"), shift_type_inst.rd())]);
                        result_inst.name = String::from("SRAI");
                    }

                    // OP
                    Instruction::Add(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("ADD");
                    }
                    Instruction::Sub(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("SUB");
                    }
                    Instruction::Sll(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("SLL");
                    }
                    Instruction::Slt(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("SLT");
                    }
                    Instruction::Sltu(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("SLTU");
                    }
                    Instruction::Xor(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("XOR");
                    }
                    Instruction::Srl(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("SRL");
                    }
                    Instruction::Sra(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("SRA");
                    }
                    Instruction::Or(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("OR");
                    }
                    Instruction::And(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("AND");
                    }
                    Instruction::Mul(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("MUL");
                    }
                    Instruction::Mulh(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("MULH");
                    }
                    Instruction::Mulhsu(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("MULHSU");
                    }
                    Instruction::Mulhu(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("MULHU");
                    }
                    Instruction::Div(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("DIV");
                    }
                    Instruction::Divu(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("DIVU");
                    }
                    Instruction::Rem(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("REM");
                    }
                    Instruction::Remu(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("REMU");
                    }

                    // Misc-mem
                    Instruction::Fence(fence_type_inst) => {
                        result_inst.name = String::from("FENCE");
                        result_inst.pred_succ =
                            Some((fence_type_inst.pred(), fence_type_inst.succ()));
                    }
                    Instruction::FenceI => {
                        result_inst.name = String::from("FENCEI");
                    }

                    // System
                    Instruction::Ecall => {
                        result_inst.name = String::from("ECALL");
                    }
                    Instruction::Ebreak => {
                        result_inst.name = String::from("EBREAK");
                    }
                    Instruction::Uret => {
                        result_inst.name = String::from("URET");
                        result_inst.read_reg = Some(vec![
                            (String::from("csr"), csr_address::CSR_UEPC_ADDRESS as u64),
                            (String::from("csr"), csr_address::CSR_USTATUS_ADDRESS as u64),
                        ]);
                        result_inst.write_reg = Some(vec![(
                            String::from("csr"),
                            csr_address::CSR_USTATUS_ADDRESS as u64,
                        )]);
                    }
                    Instruction::Sret => {
                        result_inst.name = String::from("SRET");
                        result_inst.read_reg = Some(vec![
                            (String::from("csr"), csr_address::CSR_SEPC_ADDRESS as u64),
                            (String::from("csr"), csr_address::CSR_SSTATUS_ADDRESS as u64),
                        ]);
                        result_inst.write_reg = Some(vec![(
                            String::from("csr"),
                            csr_address::CSR_SSTATUS_ADDRESS as u64,
                        )]);
                    }
                    Instruction::Mret => {
                        result_inst.name = String::from("MRET");
                        result_inst.read_reg = Some(vec![
                            (String::from("csr"), csr_address::CSR_MEPC_ADDRESS as u64),
                            (String::from("csr"), csr_address::CSR_MSTATUS_ADDRESS as u64),
                        ]);
                        result_inst.write_reg = Some(vec![(
                            String::from("csr"),
                            csr_address::CSR_MSTATUS_ADDRESS as u64,
                        )]);
                    }
                    Instruction::Wfi => {
                        result_inst.name = String::from("WFI");
                    }
                    Instruction::SfenceVma(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("SFENCEVMA");
                    }
                    Instruction::Csrrw(csr_type_inst) => {
                        result_inst.name = String::from("CSRRW");
                        result_inst.read_reg = Some(vec![
                            (String::from("csr"), csr_type_inst.csr()),
                            (String::from("int"), csr_type_inst.rs1()),
                        ]);
                        result_inst.write_reg = Some(vec![
                            (String::from("csr"), csr_type_inst.csr()),
                            (String::from("int"), csr_type_inst.rd()),
                        ]);
                    }
                    Instruction::Csrrs(csr_type_inst) => {
                        result_inst.name = String::from("CSRRS");
                        result_inst.read_reg = Some(vec![
                            (String::from("csr"), csr_type_inst.csr()),
                            (String::from("int"), csr_type_inst.rs1()),
                        ]);
                        result_inst.write_reg = Some(vec![
                            (String::from("csr"), csr_type_inst.csr()),
                            (String::from("int"), csr_type_inst.rd()),
                        ]);
                    }
                    Instruction::Csrrc(csr_type_inst) => {
                        result_inst.name = String::from("CSRRC");
                        result_inst.read_reg = Some(vec![
                            (String::from("csr"), csr_type_inst.csr()),
                            (String::from("int"), csr_type_inst.rs1()),
                        ]);
                        result_inst.write_reg = Some(vec![
                            (String::from("csr"), csr_type_inst.csr()),
                            (String::from("int"), csr_type_inst.rd()),
                        ]);
                    }
                    Instruction::Csrrwi(csri_type_inst) => {
                        result_inst.name = String::from("CSRRWI");
                        result_inst.zimm = Some(csri_type_inst.zimm());
                        result_inst.read_reg =
                            Some(vec![(String::from("csr"), csri_type_inst.csr())]);
                        result_inst.write_reg = Some(vec![
                            (String::from("csr"), csri_type_inst.csr()),
                            (String::from("int"), csri_type_inst.rd()),
                        ]);
                    }
                    Instruction::Csrrsi(csri_type_inst) => {
                        result_inst.name = String::from("CSRRSI");
                        result_inst.zimm = Some(csri_type_inst.zimm());
                        result_inst.read_reg =
                            Some(vec![(String::from("csr"), csri_type_inst.csr())]);
                        result_inst.write_reg = Some(vec![
                            (String::from("csr"), csri_type_inst.csr()),
                            (String::from("int"), csri_type_inst.rd()),
                        ]);
                    }
                    Instruction::Csrrci(csri_type_inst) => {
                        result_inst.name = String::from("CSRRCI");
                        result_inst.zimm = Some(csri_type_inst.zimm());
                        result_inst.read_reg =
                            Some(vec![(String::from("csr"), csri_type_inst.csr())]);
                        result_inst.write_reg = Some(vec![
                            (String::from("csr"), csri_type_inst.csr()),
                            (String::from("int"), csri_type_inst.rd()),
                        ]);
                    }

                    // OP-imm 32
                    Instruction::Addiw(i_type_inst) => {
                        result_inst.imm = Some(i_type_inst.imm() as i64);
                        result_inst.read_reg = Some(vec![(String::from("int"), i_type_inst.rs1())]);
                        result_inst.write_reg = Some(vec![(String::from("int"), i_type_inst.rd())]);
                        result_inst.name = String::from("ADDIW");
                    }
                    Instruction::Slliw(shift_type_inst) => {
                        result_inst.shamt = Some(shift_type_inst.shamt() as i64);
                        result_inst.read_reg =
                            Some(vec![(String::from("int"), shift_type_inst.rs1())]);
                        result_inst.write_reg =
                            Some(vec![(String::from("int"), shift_type_inst.rd())]);
                        result_inst.name = String::from("SLLIW");
                    }
                    Instruction::Srliw(shift_type_inst) => {
                        result_inst.shamt = Some(shift_type_inst.shamt() as i64);
                        result_inst.read_reg =
                            Some(vec![(String::from("int"), shift_type_inst.rs1())]);
                        result_inst.write_reg =
                            Some(vec![(String::from("int"), shift_type_inst.rd())]);
                        result_inst.name = String::from("SRLIW");
                    }
                    Instruction::Sraiw(shift_type_inst) => {
                        result_inst.shamt = Some(shift_type_inst.shamt() as i64);
                        result_inst.read_reg =
                            Some(vec![(String::from("int"), shift_type_inst.rs1())]);
                        result_inst.write_reg =
                            Some(vec![(String::from("int"), shift_type_inst.rd())]);
                        result_inst.name = String::from("SRAIW");
                    }

                    // OP 32
                    Instruction::Addw(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("ADDW");
                    }
                    Instruction::Subw(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("SUBW");
                    }
                    Instruction::Sllw(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("SLLW");
                    }
                    Instruction::Srlw(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("SRLW");
                    }
                    Instruction::Sraw(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("SRAW");
                    }
                    Instruction::Mulw(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("MULW");
                    }
                    Instruction::Divw(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("DIVW");
                    }
                    Instruction::Divuw(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("DIVUW");
                    }
                    Instruction::Remw(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("REMW");
                    }
                    Instruction::Remuw(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("REMUW");
                    }

                    // Illegal
                    Instruction::Illegal => {
                        result_inst.name = String::from("ILLEGAL");
                    }

                    Instruction::__Nonexhaustive => {
                        result_inst.name = String::from("NONEXHAUSTIVE");
                    }
                }

                out.inst = Some(result_inst);
            }
            Err(decoding_error) => {
                out.decode_error = Some(format!("{:x?}", decoding_error));
            }
        }

        Ok(out)
    }

    Ok(())
}
