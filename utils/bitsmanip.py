#====================================================
# file:       bitsmanip.py
# created by: cs
# notes:      to deal with bits manipulating
#             inorder to cooperate between different
#             environments
#====================================================

import numpy  as np 
import struct

# ------------------- 
# pack functions
# number to bytes
# -------------------

def pack_int32(num):
    return struct.pack('!i', num)
    
def pack_uint32(num):
    return struct.pack('!I', num)
    
def pack_int64(num):
    return struct.pack('!q', num)
    
def pack_uint64(num):
    return struct.pack('!Q', num)
    
def pack_float32(num):
    return struct.pack('!f', num)
    
def pack_float64(num):
    return struct.pack('!d', num)


# ------------------- 
# pack functions
# bytes to numbers
# -------------------

def unpack_int32(bytes):
    return np.int32(struct.unpack('!i', bytes)[0])
    
def unpack_uint32(bytes):
    return np.uint32(struct.unpack('!I', bytes)[0])
    
def unpack_int64(bytes):
    return np.int64(struct.unpack('!q', bytes)[0])
    
def unpack_uint64(bytes):
    return np.uint64(struct.unpack('!Q', bytes)[0])
    
def unpack_float32(bytes):
    return np.float32(struct.unpack('!f', bytes)[0])
    
def unpack_float64(bytes):
    return np.float64(struct.unpack('!d', bytes)[0])

# -------------------
# transform functions
# bytes to string
# -------------------

def bytes_to_bin(bytes):
    return '0b' + ''.join('{:0>8b}'.format(byte) for byte in bytes)

def bytes_to_hex(bytes):
    return '0x' + ''.join('{:0>2x}'.format(byte) for byte in bytes)

def str_to_bytes_32(byte_str):
    return pack_uint32(eval(hex_str)) 
    
def str_to_bytes_64(byte_str):
    return pack_uint64(eval(hex_str)) 

# ------------------- -----
# transforming functions
# to string / from string
# ------------------- -----

def encode_float32(num):
    return bytes_to_hex(pack_float32(num) )

def decode_float32(hex_str):
    return unpack_float32(pack_uint32(eval(hex_str)) )
    # it should be uint32 here, not int32, 
    # since eval() only generate unsigned numbers
    # but the result bytes comes the same

def encode_int32(num):
    return bytes_to_hex(pack_int32(num) )
    
def decode_int32(hex_str):
    return unpack_int32(pack_uint32(eval(hex_str)) )
    
    
def encode_uint32(num):
    return bytes_to_hex(pack_uint32(num) )
    
def decode_uint32(hex_str):
    return unpack_uint32( pack_uint32(eval(hex_str)) )
    
    
def encode_int64(num):
    return bytes_to_hex(pack_int64(num) )
    
def decode_int64(hex_str):
    return unpack_int64(pack_uint64(eval(hex_str)) )
    
def encode_uint64(num):
    return bytes_to_hex(pack_uint64(num) )
    
def decode_uint64(hex_str):
    return unpack_uint64(pack_uint64(eval(hex_str)) )    
    
    
    
    
