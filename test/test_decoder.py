from utils.decoder import *


def test_decoder():
    data = decode(0xbff00513)
    assert data.inst.name == 'Addi'
    assert data.inst.imm == -1025
    assert data.inst.zimm == None
    assert data.inst.shamt == None
    assert data.inst.pred_succ == None
    assert data.inst.read_reg == [('int',0)]
    assert data.inst.write_reg == [('int',10)]
    assert data.decode_error == None
