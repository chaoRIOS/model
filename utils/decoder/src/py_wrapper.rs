use pyo3::class::basic::PyObjectProtocol;
use pyo3::prelude::*;

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
    pub imm: Option<i32>,
    #[pyo3(get)]
    pub zimm: Option<u32>,
    #[pyo3(get)]
    pub shamt: Option<i32>,
    #[pyo3(get)]
    pub pred_succ: Option<(u32, u32)>,
    #[pyo3(get)]
    pub read_reg: Option<Vec<(String, u32)>>,
    #[pyo3(get)]
    pub write_reg: Option<Vec<(String, u32)>>,
    // @TODO: Load/Store decoding
    // #[pyo3(get)]
    // pub load_mem: Option<Vec<(u32, u32)>>,
    // #[pyo3(get)]
    // pub store_mem: Option<Vec<(u32, u32)>>,
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
                        result_inst.imm = Some(u_type_inst.imm() as i32);
                        result_inst.write_reg = Some(vec![(String::from("int"), u_type_inst.rd())]);
                        result_inst.name = String::from("Lui");
                    }

                    // AUIPC
                    Instruction::Auipc(u_type_inst) => {
                        result_inst.imm = Some(u_type_inst.imm() as i32);
                        result_inst.write_reg = Some(vec![(String::from("int"), u_type_inst.rd())]);
                        result_inst.name = String::from("Auipc");
                    }

                    // Jal
                    Instruction::Jal(j_type_inst) => {
                        result_inst.imm = Some(j_type_inst.imm() as i32);
                        result_inst.write_reg = Some(vec![(String::from("int"), j_type_inst.rd())]);
                        result_inst.name = String::from("Jal");
                    }

                    // Jalr
                    Instruction::Jalr(i_type_inst) => {
                        result_inst.imm = Some(i_type_inst.imm() as i32);
                        result_inst.read_reg = Some(vec![(String::from("int"), i_type_inst.rs1())]);
                        result_inst.write_reg = Some(vec![(String::from("int"), i_type_inst.rd())]);
                        result_inst.name = String::from("Jalr");
                    }

                    // Branch
                    Instruction::Beq(b_type_inst) => {
                        result_inst.imm = Some(b_type_inst.imm() as i32);
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), b_type_inst.rs1()),
                            (String::from("int"), b_type_inst.rs2()),
                        ]);
                        result_inst.name = String::from("Beq");
                    }
                    Instruction::Bne(b_type_inst) => {
                        result_inst.imm = Some(b_type_inst.imm() as i32);
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), b_type_inst.rs1()),
                            (String::from("int"), b_type_inst.rs2()),
                        ]);
                        result_inst.name = String::from("Bne");
                    }
                    Instruction::Blt(b_type_inst) => {
                        result_inst.imm = Some(b_type_inst.imm() as i32);
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), b_type_inst.rs1()),
                            (String::from("int"), b_type_inst.rs2()),
                        ]);
                        result_inst.name = String::from("Blt");
                    }
                    Instruction::Bge(b_type_inst) => {
                        result_inst.imm = Some(b_type_inst.imm() as i32);
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), b_type_inst.rs1()),
                            (String::from("int"), b_type_inst.rs2()),
                        ]);
                        result_inst.name = String::from("Bge");
                    }
                    Instruction::Bltu(b_type_inst) => {
                        result_inst.imm = Some(b_type_inst.imm() as i32);
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), b_type_inst.rs1()),
                            (String::from("int"), b_type_inst.rs2()),
                        ]);
                        result_inst.name = String::from("Bltu");
                    }
                    Instruction::Bgeu(b_type_inst) => {
                        result_inst.imm = Some(b_type_inst.imm() as i32);
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), b_type_inst.rs1()),
                            (String::from("int"), b_type_inst.rs2()),
                        ]);
                        result_inst.name = String::from("Bgeu");
                    }

                    // Load
                    Instruction::Lb(i_type_inst) => {
                        result_inst.imm = Some(i_type_inst.imm() as i32);
                        result_inst.read_reg = Some(vec![(String::from("int"), i_type_inst.rs1())]);
                        result_inst.write_reg = Some(vec![(String::from("int"), i_type_inst.rd())]);
                        result_inst.name = String::from("Lb");
                    }
                    Instruction::Lh(i_type_inst) => {
                        result_inst.imm = Some(i_type_inst.imm() as i32);
                        result_inst.read_reg = Some(vec![(String::from("int"), i_type_inst.rs1())]);
                        result_inst.write_reg = Some(vec![(String::from("int"), i_type_inst.rd())]);
                        result_inst.name = String::from("Lh");
                    }
                    Instruction::Lw(i_type_inst) => {
                        result_inst.imm = Some(i_type_inst.imm() as i32);
                        result_inst.read_reg = Some(vec![(String::from("int"), i_type_inst.rs1())]);
                        result_inst.write_reg = Some(vec![(String::from("int"), i_type_inst.rd())]);
                        result_inst.name = String::from("Lw");
                    }
                    Instruction::Lbu(i_type_inst) => {
                        result_inst.imm = Some(i_type_inst.imm() as i32);
                        result_inst.read_reg = Some(vec![(String::from("int"), i_type_inst.rs1())]);
                        result_inst.write_reg = Some(vec![(String::from("int"), i_type_inst.rd())]);
                        result_inst.name = String::from("Lbu");
                    }
                    Instruction::Lhu(i_type_inst) => {
                        result_inst.imm = Some(i_type_inst.imm() as i32);
                        result_inst.read_reg = Some(vec![(String::from("int"), i_type_inst.rs1())]);
                        result_inst.write_reg = Some(vec![(String::from("int"), i_type_inst.rd())]);
                        result_inst.name = String::from("Lhu");
                    }
                    Instruction::Lwu(i_type_inst) => {
                        result_inst.imm = Some(i_type_inst.imm() as i32);
                        result_inst.read_reg = Some(vec![(String::from("int"), i_type_inst.rs1())]);
                        result_inst.write_reg = Some(vec![(String::from("int"), i_type_inst.rd())]);
                        result_inst.name = String::from("Lwu");
                    }
                    Instruction::Ld(i_type_inst) => {
                        result_inst.imm = Some(i_type_inst.imm() as i32);
                        result_inst.read_reg = Some(vec![(String::from("int"), i_type_inst.rs1())]);
                        result_inst.write_reg = Some(vec![(String::from("int"), i_type_inst.rd())]);
                        result_inst.name = String::from("Ld");
                    }

                    // Store
                    Instruction::Sb(s_type_inst) => {
                        result_inst.imm = Some(s_type_inst.imm() as i32);
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), s_type_inst.rs1()),
                            (String::from("int"), s_type_inst.rs2()),
                        ]);
                        result_inst.name = String::from("Sb");
                    }
                    Instruction::Sh(s_type_inst) => {
                        result_inst.imm = Some(s_type_inst.imm() as i32);
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), s_type_inst.rs1()),
                            (String::from("int"), s_type_inst.rs2()),
                        ]);
                        result_inst.name = String::from("Sh");
                    }
                    Instruction::Sw(s_type_inst) => {
                        result_inst.imm = Some(s_type_inst.imm() as i32);
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), s_type_inst.rs1()),
                            (String::from("int"), s_type_inst.rs2()),
                        ]);
                        result_inst.name = String::from("Sw");
                    }
                    Instruction::Sd(s_type_inst) => {
                        result_inst.imm = Some(s_type_inst.imm() as i32);
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), s_type_inst.rs1()),
                            (String::from("int"), s_type_inst.rs2()),
                        ]);
                        result_inst.name = String::from("Sd");
                    }

                    // OP-imm
                    Instruction::Addi(i_type_inst) => {
                        result_inst.imm = Some(i_type_inst.imm() as i32);
                        result_inst.read_reg = Some(vec![(String::from("int"), i_type_inst.rs1())]);
                        result_inst.write_reg = Some(vec![(String::from("int"), i_type_inst.rd())]);
                        result_inst.name = String::from("Addi");
                    }
                    Instruction::Slti(i_type_inst) => {
                        result_inst.imm = Some(i_type_inst.imm() as i32);
                        result_inst.read_reg = Some(vec![(String::from("int"), i_type_inst.rs1())]);
                        result_inst.write_reg = Some(vec![(String::from("int"), i_type_inst.rd())]);
                        result_inst.name = String::from("Slti");
                    }
                    Instruction::Sltiu(i_type_inst) => {
                        result_inst.imm = Some(i_type_inst.imm() as i32);
                        result_inst.read_reg = Some(vec![(String::from("int"), i_type_inst.rs1())]);
                        result_inst.write_reg = Some(vec![(String::from("int"), i_type_inst.rd())]);
                        result_inst.name = String::from("Sltiu");
                    }
                    Instruction::Xori(i_type_inst) => {
                        result_inst.imm = Some(i_type_inst.imm() as i32);
                        result_inst.read_reg = Some(vec![(String::from("int"), i_type_inst.rs1())]);
                        result_inst.write_reg = Some(vec![(String::from("int"), i_type_inst.rd())]);
                        result_inst.name = String::from("Xori");
                    }
                    Instruction::Ori(i_type_inst) => {
                        result_inst.imm = Some(i_type_inst.imm() as i32);
                        result_inst.read_reg = Some(vec![(String::from("int"), i_type_inst.rs1())]);
                        result_inst.write_reg = Some(vec![(String::from("int"), i_type_inst.rd())]);
                        result_inst.name = String::from("Ori");
                    }
                    Instruction::Andi(i_type_inst) => {
                        result_inst.imm = Some(i_type_inst.imm() as i32);
                        result_inst.read_reg = Some(vec![(String::from("int"), i_type_inst.rs1())]);
                        result_inst.write_reg = Some(vec![(String::from("int"), i_type_inst.rd())]);
                        result_inst.name = String::from("Andi");
                    }
                    Instruction::Slli(shift_type_inst) => {
                        result_inst.shamt = Some(shift_type_inst.shamt() as i32);
                        result_inst.read_reg =
                            Some(vec![(String::from("int"), shift_type_inst.rs1())]);
                        result_inst.write_reg =
                            Some(vec![(String::from("int"), shift_type_inst.rd())]);
                        result_inst.name = String::from("Slli");
                    }
                    Instruction::Srli(shift_type_inst) => {
                        result_inst.shamt = Some(shift_type_inst.shamt() as i32);
                        result_inst.read_reg =
                            Some(vec![(String::from("int"), shift_type_inst.rs1())]);
                        result_inst.write_reg =
                            Some(vec![(String::from("int"), shift_type_inst.rd())]);
                        result_inst.name = String::from("Srli");
                    }
                    Instruction::Srai(shift_type_inst) => {
                        result_inst.shamt = Some(shift_type_inst.shamt() as i32);
                        result_inst.read_reg =
                            Some(vec![(String::from("int"), shift_type_inst.rs1())]);
                        result_inst.write_reg =
                            Some(vec![(String::from("int"), shift_type_inst.rd())]);
                        result_inst.name = String::from("Srai");
                    }

                    // OP
                    Instruction::Add(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("Add");
                    }
                    Instruction::Sub(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("Sub");
                    }
                    Instruction::Sll(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("Sll");
                    }
                    Instruction::Slt(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("Slt");
                    }
                    Instruction::Sltu(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("Sltu");
                    }
                    Instruction::Xor(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("Xor");
                    }
                    Instruction::Srl(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("Srl");
                    }
                    Instruction::Sra(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("Sra");
                    }
                    Instruction::Or(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("Or");
                    }
                    Instruction::And(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("And");
                    }
                    Instruction::Mul(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("Mul");
                    }
                    Instruction::Mulh(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("Mulh");
                    }
                    Instruction::Mulhsu(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("Mulhsu");
                    }
                    Instruction::Mulhu(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("Mulhu");
                    }
                    Instruction::Div(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("Div");
                    }
                    Instruction::Divu(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("Divu");
                    }
                    Instruction::Rem(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("Rem");
                    }
                    Instruction::Remu(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("Remu");
                    }

                    // Misc-mem
                    Instruction::Fence(fence_type_inst) => {
                        result_inst.name = String::from("Fence");
                        result_inst.pred_succ =
                            Some((fence_type_inst.pred(), fence_type_inst.succ()));
                    }
                    Instruction::FenceI => {
                        result_inst.name = String::from("FenceI");
                    }

                    // System
                    Instruction::Ecall => {
                        result_inst.name = String::from("Ecall");
                    }
                    Instruction::Ebreak => {
                        result_inst.name = String::from("Ebreak");
                    }
                    Instruction::Uret => {
                        result_inst.name = String::from("Uret");
                    }
                    Instruction::Sret => {
                        result_inst.name = String::from("Sret");
                    }
                    Instruction::Mret => {
                        result_inst.name = String::from("Mret");
                    }
                    Instruction::Wfi => {
                        result_inst.name = String::from("Wfi");
                    }
                    Instruction::SfenceVma(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("SfenceVma");
                    }
                    Instruction::Csrrw(csr_type_inst) => {
                        result_inst.name = String::from("Csrrw");
                        result_inst.read_reg = Some(vec![
                            (String::from("csr"), csr_type_inst.csr()),
                            (String::from("int"), csr_type_inst.rs1()),
                        ]);
                        result_inst.write_reg =
                            Some(vec![(String::from("int"), csr_type_inst.rd())]);
                    }
                    Instruction::Csrrs(csr_type_inst) => {
                        result_inst.name = String::from("Csrrs");
                        result_inst.read_reg = Some(vec![
                            (String::from("csr"), csr_type_inst.csr()),
                            (String::from("int"), csr_type_inst.rs1()),
                        ]);
                        result_inst.write_reg =
                            Some(vec![(String::from("int"), csr_type_inst.rd())]);
                    }
                    Instruction::Csrrc(csr_type_inst) => {
                        result_inst.name = String::from("Csrrc");
                        result_inst.read_reg = Some(vec![
                            (String::from("csr"), csr_type_inst.csr()),
                            (String::from("int"), csr_type_inst.rs1()),
                        ]);
                        result_inst.write_reg =
                            Some(vec![(String::from("int"), csr_type_inst.rd())]);
                    }
                    Instruction::Csrrwi(csri_type_inst) => {
                        result_inst.name = String::from("Csrrwi");
                        result_inst.zimm = Some(csri_type_inst.zimm());
                        result_inst.read_reg =
                            Some(vec![(String::from("csr"), csri_type_inst.csr())]);
                        result_inst.write_reg =
                            Some(vec![(String::from("int"), csri_type_inst.rd())]);
                    }
                    Instruction::Csrrsi(csri_type_inst) => {
                        result_inst.name = String::from("Csrrsi");
                        result_inst.zimm = Some(csri_type_inst.zimm());
                        result_inst.read_reg =
                            Some(vec![(String::from("csr"), csri_type_inst.csr())]);
                        result_inst.write_reg =
                            Some(vec![(String::from("int"), csri_type_inst.rd())]);
                    }
                    Instruction::Csrrci(csri_type_inst) => {
                        result_inst.name = String::from("Csrrci");
                        result_inst.zimm = Some(csri_type_inst.zimm());
                        result_inst.read_reg =
                            Some(vec![(String::from("csr"), csri_type_inst.csr())]);
                        result_inst.write_reg =
                            Some(vec![(String::from("int"), csri_type_inst.rd())]);
                    }

                    // OP-imm 32
                    Instruction::Addiw(i_type_inst) => {
                        result_inst.imm = Some(i_type_inst.imm() as i32);
                        result_inst.read_reg = Some(vec![(String::from("int"), i_type_inst.rs1())]);
                        result_inst.write_reg = Some(vec![(String::from("int"), i_type_inst.rd())]);
                        result_inst.name = String::from("Addiw");
                    }
                    Instruction::Slliw(shift_type_inst) => {
                        result_inst.shamt = Some(shift_type_inst.shamt() as i32);
                        result_inst.read_reg =
                            Some(vec![(String::from("int"), shift_type_inst.rs1())]);
                        result_inst.write_reg =
                            Some(vec![(String::from("int"), shift_type_inst.rd())]);
                        result_inst.name = String::from("Slliw");
                    }
                    Instruction::Srliw(shift_type_inst) => {
                        result_inst.shamt = Some(shift_type_inst.shamt() as i32);
                        result_inst.read_reg =
                            Some(vec![(String::from("int"), shift_type_inst.rs1())]);
                        result_inst.write_reg =
                            Some(vec![(String::from("int"), shift_type_inst.rd())]);
                        result_inst.name = String::from("Srliw");
                    }
                    Instruction::Sraiw(shift_type_inst) => {
                        result_inst.shamt = Some(shift_type_inst.shamt() as i32);
                        result_inst.read_reg =
                            Some(vec![(String::from("int"), shift_type_inst.rs1())]);
                        result_inst.write_reg =
                            Some(vec![(String::from("int"), shift_type_inst.rd())]);
                        result_inst.name = String::from("Sraiw");
                    }

                    // OP 32
                    Instruction::Addw(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("Addw");
                    }
                    Instruction::Subw(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("Subw");
                    }
                    Instruction::Sllw(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("Sllw");
                    }
                    Instruction::Srlw(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("Srlw");
                    }
                    Instruction::Sraw(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("Sraw");
                    }
                    Instruction::Mulw(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("Mulw");
                    }
                    Instruction::Divw(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("Divw");
                    }
                    Instruction::Divuw(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("Divuw");
                    }
                    Instruction::Remw(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("Remw");
                    }
                    Instruction::Remuw(r_type_inst) => {
                        result_inst.read_reg = Some(vec![
                            (String::from("int"), r_type_inst.rs1()),
                            (String::from("int"), r_type_inst.rs2()),
                        ]);
                        result_inst.write_reg = Some(vec![(String::from("int"), r_type_inst.rd())]);
                        result_inst.name = String::from("Remuw");
                    }

                    // Illegal
                    Instruction::Illegal => {
                        result_inst.name = String::from("Illegal");
                    }

                    Instruction::__Nonexhaustive => {
                        result_inst.name = String::from("Nonexhaustive");
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
