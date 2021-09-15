from utils.elf_parser import *
import pytest


def test_load_elf():
    data = load_elf("/opt/riscv-tests/coremark/coremark.riscv", 2049 * 1024 * 1024)
    assert data.tohost_addr == 0x80001000
    assert data.entry_pc == 0x80000000
