import numpy as np
import pytest
from utils.bitsmanip import *

def setup_module():
    print("testing bits manip functions")
    
    

def encoding_check(encoding_func, decoding_func, num):
    assert decoding_func(encoding_func(num))==num, "checking {}/{} num={}".format(
        encoding_func.__name__, decoding_func.__name__, num)


# ---------- ----------
# test for float 32
# ---------- ----------

def test_float32():
    encoding_check(encode_float32, decode_float32,  1.0)
    encoding_check(encode_float32, decode_float32, -1.0)
    encoding_check(encode_float32, decode_float32,  255.0)
    encoding_check(encode_float64, decode_float64,  np.finfo('f').max )
    encoding_check(encode_float64, decode_float64,  np.finfo('f').min )
    encoding_check(encode_float64, decode_float64,  np.finfo('f').tiny )

@pytest.mark.xfail(reason="wrong type")
def test_float32_types():
    encoding_check(encode_float32, decode_float32,  "abcd")
    encoding_check(encode_float32, decode_float32,  [] )

# ---------- ----------
# test for float 64
# ---------- ----------

def test_float64():
    encoding_check(encode_float64, decode_float64,  1.0)
    encoding_check(encode_float64, decode_float64, -1.0)
    encoding_check(encode_float64, decode_float64,  np.finfo('d').max )
    encoding_check(encode_float64, decode_float64,  np.finfo('d').min )
    encoding_check(encode_float64, decode_float64,  np.finfo('d').tiny )

@pytest.mark.xfail(reason="wrong type")
def test_float64_types():
    encoding_check(encode_float64, decode_float64,  "abcd")
    encoding_check(encode_float64, decode_float64,  [] )

# ---------- ----------
# test for int 32
# ---------- ----------

def test_int32():
    encoding_check(encode_int32, decode_int32,  1)
    encoding_check(encode_int32, decode_int32,  -1)
    encoding_check(encode_int32, decode_int32,  0)
    encoding_check(encode_int32, decode_int32,  0x7fffffff)
    encoding_check(encode_int32, decode_int32,  np.iinfo('i').min )
    encoding_check(encode_int32, decode_int32,  np.iinfo('i').max )

@pytest.mark.xfail(reason="exceed limit")
def test_int32_limits():
    encoding_check(encode_int32, decode_int32,  0xffffffff)
    encoding_check(encode_int32, decode_int32,  np.iinfo('i').min-1 ) 
    encoding_check(encode_int32, decode_int32,  np.iinfo('i').max+1 )


@pytest.mark.xfail(reason="wrong type")
def test_int32_types():
    encoding_check(encode_int32, decode_int32,  1.0)
    encoding_check(encode_int32, decode_int32,  "abcd")
    encoding_check(encode_int32, decode_int32,  [] )

# ---------- ----------
# test for uint 32
# ---------- ----------

def test_uint32():
    encoding_check(encode_uint32, decode_uint32,  0)
    encoding_check(encode_uint32, decode_uint32,  1)
    encoding_check(encode_uint32, decode_uint32,  255)
    encoding_check(encode_uint32, decode_uint32,  65535)
    encoding_check(encode_uint32, decode_uint32,  0x7fffffff)
    encoding_check(encode_uint32, decode_uint32,  0xffffffff)
    encoding_check(encode_uint32, decode_uint32,  np.iinfo('I').min )
    encoding_check(encode_uint32, decode_uint32,  np.iinfo('I').max )

@pytest.mark.xfail(reason="exceed limit")
def test_uint32_limits():
    encoding_check(encode_uint32, decode_uint32,  -1)
    encoding_check(encode_uint32, decode_uint32,  np.iinfo('I').min-1 ) 
    encoding_check(encode_uint32, decode_uint32,  np.iinfo('I').min-1 ) 

@pytest.mark.xfail(reason="wrong type")
def test_int32_types():
    encoding_check(encode_uint32, decode_uint32,  1.0)
    encoding_check(encode_uint32, decode_uint32,  "abcd")
    encoding_check(encode_uint32, decode_uint32,  [] )


# ---------- ----------
# test for int 64
# ---------- ----------

def test_int64():
    encoding_check(encode_int64, decode_int64,  1)
    encoding_check(encode_int64, decode_int64,  -1)
    encoding_check(encode_int64, decode_int64,  0)
    encoding_check(encode_int64, decode_int64,  0x7fffffffffffffff)
    encoding_check(encode_int64, decode_int64,  np.iinfo('l').min )
    encoding_check(encode_int64, decode_int64,  np.iinfo('l').max )

@pytest.mark.xfail(reason="exceed limit")
def test_int64_limits():
    encoding_check(encode_int64, decode_int64,  0xffffffffffffffff)
    encoding_check(encode_int64, decode_int64,  np.iinfo('l').min-1 ) 
    encoding_check(encode_int64, decode_int64,  np.iinfo('l').max+1 )


@pytest.mark.xfail(reason="wrong type")
def test_int64_types():
    encoding_check(encode_int64, decode_int64,  1.0)
    encoding_check(encode_int64, decode_int64,  "abcd")
    encoding_check(encode_int64, decode_int64,  [] )


# ---------- ----------
# test for uint 64
# ---------- ----------

def test_uint64():
    encoding_check(encode_uint64, decode_uint64,  0)
    encoding_check(encode_uint64, decode_uint64,  1)
    encoding_check(encode_uint64, decode_uint64,  0xffffffffffffffff)
    encoding_check(encode_uint64, decode_uint64,  np.iinfo('L').min )
    encoding_check(encode_uint64, decode_uint64,  np.iinfo('L').max )

@pytest.mark.xfail(reason="exceed limit")
def test_uint64_limits():
    encoding_check(encode_uint64, decode_uint64,  0xffffffffffffffff)
    encoding_check(encode_uint64, decode_uint64,  np.iinfo('L').min-1 ) 
    encoding_check(encode_uint64, decode_uint64,  np.iinfo('L').max+1 )


@pytest.mark.xfail(reason="wrong type")
def test_uint64_types():
    encoding_check(encode_uint64, decode_uint64,  1.0)
    encoding_check(encode_uint64, decode_uint64,  "abcd")
    encoding_check(encode_uint64, decode_uint64,  [] )







