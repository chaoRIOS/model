#====================================================
# file:       decoder.py
# created by: chao wang
# notes:      decoder
#====================================================
import sys
sys.path.append('../..')

from utils.decoder_wrapper import decode


# ------------------- 
# Decode word to instruction
# -------------------
def decode_word(word):
    return decode(word)