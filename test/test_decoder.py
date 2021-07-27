from utils.decoder_wrapper import *


def test_decoder():
    data = decode(0xbff00513)
    assert data == {'name': 'ADDI', 'imm': -1025, 'read_regs': {'int': [{'index': 0}]}, 'write_regs': {'int': [{'index': 10}]}}