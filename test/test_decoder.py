from utils.decoder import *


def test_decoder():
    data = decode(0xbff00513)
    assert data == {'name': 'ADDI', 'imm': -1025, 'read_reg': {'int': [{'index': 0}]}, 'write_reg': {'int': [{'index': 10}]}}