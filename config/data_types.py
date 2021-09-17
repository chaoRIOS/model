import numpy as np

byte_type = np.uint8
half_type = np.uint16
word_type = np.uint32
double_type = np.uint64

reg_type = np.uint64

signed_reg_type = np.int64


def sext_word_type(data):
    return word_type(data) | (
        double_type(0xFFFF_FFFF_0000_0000)
        if data & word_type(0x8000_0000) == 0x8000_0000
        else double_type(0)
    )
