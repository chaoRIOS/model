use pyo3::prelude::*;
use std::fs::File;
use std::io::Read;

pub mod elf_analyzer;
pub mod memory;

use elf_analyzer::ElfAnalyzer;
use memory::Memory;

#[pymodule]
fn elfparser(py: Python, m: &PyModule) -> PyResult<()> {
    // PyO3 aware function. All of our Python interfaces could be declared in a separate module.
    // Note that the `#[pyfn()]` annotation automatically converts the arguments from
    // Python objects to Rust values, and the Rust return value back into a Python object.
    // The `_py` argument represents that we're holding the GIL.
    #[pyfn(m)]
    #[pyo3(name = "load_elf")]
    fn load_elf_py(_py: Python, elf_path: String, capacity: u64) -> PyResult<ElfContext> {
        let out = load_elf(elf_path, capacity)?;
        Ok(out)
    }

    // Add the class to module
    m.add_class::<ElfContext>()?;

    Ok(())
}

#[pyclass]
struct ElfContext {
    // Currently set all member read-only in Python
    // #[pyo3(get)] requires both `IntoPy<PyObject>` and `Clone` traits.
    #[pyo3(get)]
    memory: Memory,
    #[pyo3(get)]
    entry_pc: u64,
    #[pyo3(get)]
    tohost_addr: u64,
    // @TODO: add 32/64-bit indicator
    // @TODO: add symbolmap for virtual address mapping (what for?)
}

#[pymethods]
impl ElfContext {
    #[new]
    pub fn new() -> Self {
        ElfContext {
            memory: Memory::new(),
            entry_pc: 0,
            tohost_addr: 0,
        }
    }
}

fn load_elf(elf_path: String, capacity: u64) -> std::io::Result<ElfContext> {
    // Get binary data from file system
    let mut elf_file = File::open(elf_path)?;
    let mut elf_contents = vec![];
    elf_file.read_to_end(&mut elf_contents)?;

    // Initialize elf context
    // Set given memory capacity
    let mut elf_context = ElfContext::new();
    elf_context.memory.init(capacity);

    // Initialize elf analyzer
    let analyzer = ElfAnalyzer::new(elf_contents);

    // Parse ELF file
    let header = analyzer.read_header();
    let section_headers = analyzer.read_section_headers(&header);

    let mut program_data_section_headers = vec![];
    let mut symbol_table_section_headers = vec![];
    let mut string_table_section_headers = vec![];

    for i in 0..section_headers.len() {
        match section_headers[i].sh_type {
            1 => program_data_section_headers.push(&section_headers[i]),
            2 => symbol_table_section_headers.push(&section_headers[i]),
            3 => string_table_section_headers.push(&section_headers[i]),
            _ => {}
        };
    }

    // Find program data section named `.tohost` to detect if the elf file is riscv-tests
    elf_context.tohost_addr = match analyzer
        .find_tohost_addr(&program_data_section_headers, &string_table_section_headers)
    {
        Some(address) => address,
        // Regular address
        None => 0x80001000,
        // @TODO: special config for lab3
        // None => 0x80000000,
    };

    // Write binary data
    for i in 0..program_data_section_headers.len() {
        let sh_addr = program_data_section_headers[i].sh_addr;
        let sh_offset = program_data_section_headers[i].sh_offset as usize;
        let sh_size = program_data_section_headers[i].sh_size as usize;
        if sh_addr >= 0x80000000 && sh_offset > 0 && sh_size > 0 {
            for j in 0..sh_size {
                elf_context.memory.write_byte(
                    // @TODO: add different masks for different memory models
                    (sh_addr + j as u64) & 0x7f_ffff_ffff,
                    analyzer.read_byte(sh_offset + j),
                );
            }
        }
    }

    // Set entry pc
    elf_context.entry_pc = header.e_entry;

    Ok(elf_context)
}

// fn main() {}
