from scipy.fft._helper import next_fast_len, prev_fast_len
from scipy.fft._helper import _init_nd_shape_and_axes
from numpy.testing import assert_equal, assert_array_equal
from pytest import raises as assert_raises
import pytest
import numpy as np
import sys

_5_smooth_numbers = [
    2, 3, 4, 5, 6, 8, 9, 10,
    2 * 3 * 5,
    2**3 * 3**5,
    2**3 * 3**3 * 5**2,
]

def test_next_fast_len():
    for n in _5_smooth_numbers:
        assert_equal(next_fast_len(n), n)


def _assert_n_smooth(x, n):
    x_orig = x
    if n < 2:
        assert False

    while True:
        q, r = divmod(x, 2)
        if r != 0:
            break
        x = q

    for d in range(3, n+1, 2):
        while True:
            q, r = divmod(x, d)
            if r != 0:
                break
            x = q

    assert x == 1, \
           'x={} is not {}-smooth, remainder={}'.format(x_orig, n, x)


class TestNextFastLen:

    def test_next_fast_len(self):
        np.random.seed(1234)

        def nums():
            yield from range(1, 1000)
            yield 2**5 * 3**5 * 4**5 + 1

        for n in nums():
            m = next_fast_len(n)
            _assert_n_smooth(m, 11)
            assert m == next_fast_len(n, False)

            m = next_fast_len(n, True)
            _assert_n_smooth(m, 5)

    def test_np_integers(self):
        ITYPES = [np.int16, np.int32, np.int64, np.uint16, np.uint32, np.uint64]
        for ityp in ITYPES:
            x = ityp(12345)
            testN = next_fast_len(x)
            assert_equal(testN, next_fast_len(int(x)))

    def testnext_fast_len_small(self):
        hams = {
            1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 8, 8: 8, 14: 15, 15: 15,
            16: 16, 17: 18, 1021: 1024, 1536: 1536, 51200000: 51200000
        }
        for x, y in hams.items():
            assert_equal(next_fast_len(x, True), y)

    @pytest.mark.xfail(sys.maxsize < 2**32,
                       reason="Hamming Numbers too large for 32-bit",
                       raises=ValueError, strict=True)
    def testnext_fast_len_big(self):
        hams = {
            510183360: 510183360, 510183360 + 1: 512000000,
            511000000: 512000000,
            854296875: 854296875, 854296875 + 1: 859963392,
            196608000000: 196608000000, 196608000000 + 1: 196830000000,
            8789062500000: 8789062500000, 8789062500000 + 1: 8796093022208,
            206391214080000: 206391214080000,
            206391214080000 + 1: 206624260800000,
            470184984576000: 470184984576000,
            470184984576000 + 1: 470715894135000,
            7222041363087360: 7222041363087360,
            7222041363087360 + 1: 7230196133913600,
            # power of 5    5**23
            11920928955078125: 11920928955078125,
            11920928955078125 - 1: 11920928955078125,
            # power of 3    3**34
            16677181699666569: 16677181699666569,
            16677181699666569 - 1: 16677181699666569,
            # power of 2   2**54
            18014398509481984: 18014398509481984,
            18014398509481984 - 1: 18014398509481984,
            # above this, int(ceil(n)) == int(ceil(n+1))
            19200000000000000: 19200000000000000,
            19200000000000000 + 1: 19221679687500000,
            288230376151711744: 288230376151711744,
            288230376151711744 + 1: 288325195312500000,
            288325195312500000 - 1: 288325195312500000,
            288325195312500000: 288325195312500000,
            288325195312500000 + 1: 288555831593533440,
        }
        for x, y in hams.items():
            assert_equal(next_fast_len(x, True), y)

    def test_keyword_args(self):
        assert next_fast_len(11, real=True) == 12
        assert next_fast_len(target=7, real=False) == 7


class TestPrevFastLen:

    def test_prev_fast_len(self):
        np.random.seed(1234)

        def nums():
            yield from range(1, 1000)
            yield 2**5 * 3**5 * 4**5 + 1

        for n in nums():
            m = prev_fast_len(n)
            _assert_n_smooth(m, 11)
            assert m == prev_fast_len(n, False)

            m = prev_fast_len(n, True)
            _assert_n_smooth(m, 5)

    def test_np_integers(self):
        ITYPES = [np.int16, np.int32, np.int64, np.uint16, np.uint32, 
                    np.uint64]
        for ityp in ITYPES:
            x = ityp(12345)
            testN = prev_fast_len(x)
            assert_equal(testN, prev_fast_len(int(x)))

            testN = prev_fast_len(x, real=True)
            assert_equal(testN, prev_fast_len(int(x), real=True))

    def testprev_fast_len_small(self):
        hams = {
            1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 6, 8: 8, 14: 12, 15: 15,
            16: 16, 17: 16, 1021: 1000, 1536: 1536, 51200000: 51200000
        }
        for x, y in hams.items():
            assert_equal(prev_fast_len(x, True), y)

        hams = {
            1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10,
            11: 11, 12: 12, 13: 12, 14: 14, 15: 15, 16: 16, 17: 16, 18: 18,
            19: 18, 20: 20, 21: 21, 22: 22, 120: 120, 121: 121, 122: 121,
            1021: 1008, 1536: 1536, 51200000: 51200000
        }
        for x, y in hams.items():
            assert_equal(prev_fast_len(x, False), y)

    @pytest.mark.xfail(sys.maxsize < 2**32,
                       reason="Hamming Numbers too large for 32-bit",
                       raises=ValueError, strict=True)
    def testprev_fast_len_big(self):
        hams = {
            # 2**6 * 3**13 * 5**1
            510183360: 510183360,
            510183360 + 1: 510183360,
            510183360 - 1: 509607936,  # 2**21 * 3**5
            # 2**6 * 5**6 * 7**1 * 73**1
            511000000: 510183360,
            511000000 + 1: 510183360,
            511000000 - 1: 510183360,  # 2**6 * 3**13 * 5**1
            # 3**7 * 5**8
            854296875: 854296875,
            854296875 + 1: 854296875,
            854296875 - 1: 850305600,  # 2**6 * 3**12 * 5**2
            # 2**22 * 3**1 * 5**6
            196608000000: 196608000000,
            196608000000 + 1: 196608000000,
            196608000000 - 1: 195910410240,  # 2**13 * 3**14 * 5**1
            # 2**5 * 3**2 * 5**15
            8789062500000: 8789062500000,
            8789062500000 + 1: 8789062500000,
            8789062500000 - 1: 8748000000000,  # 2**11 * 3**7 * 5**9
            # 2**24 * 3**9 * 5**4
            206391214080000: 206391214080000,
            206391214080000 + 1: 206391214080000,
            206391214080000 - 1: 206158430208000,  # 2**39 * 3**1 * 5**3
            # 2**18 * 3**15 * 5**3
            470184984576000: 470184984576000,
            470184984576000 + 1: 470184984576000,
            470184984576000 - 1: 469654673817600,  # 2**33 * 3**7 **5**2
            # 2**25 * 3**16 * 5**1
            7222041363087360: 7222041363087360,
            7222041363087360 + 1: 7222041363087360,
            7222041363087360 - 1: 7213895789838336,  # 2**40 * 3**8
            # power of 5    5**23
            11920928955078125: 11920928955078125,
            11920928955078125 + 1: 11920928955078125,
            11920928955078125 - 1: 11901557422080000,  # 2**14 * 3**19 * 5**4
            # power of 3    3**34
            16677181699666569: 16677181699666569,
            16677181699666569 + 1: 16677181699666569,
            16677181699666569 - 1: 16607531250000000,  # 2**7 * 3**12 * 5**12
            # power of 2   2**54
            18014398509481984: 18014398509481984,
            18014398509481984 + 1: 18014398509481984,
            18014398509481984 - 1: 18000000000000000,  # 2**16 * 3**2 * 5**15
            # 2**20 * 3**1 * 5**14
            19200000000000000: 19200000000000000,
            19200000000000000 + 1: 19200000000000000,
            19200000000000000 - 1: 19131876000000000,  # 2**11 * 3**14 * 5**9
            # 2**58
            288230376151711744: 288230376151711744,
            288230376151711744 + 1: 288230376151711744,
            288230376151711744 - 1: 288000000000000000,  # 2**20 * 3**2 * 5**15
            # 2**5 * 3**10 * 5**16
            288325195312500000: 288325195312500000,
            288325195312500000 + 1: 288325195312500000,
            288325195312500000 - 1: 288230376151711744,  # 2**58
        }
        for x, y in hams.items():
            assert_equal(prev_fast_len(x, True), y)

    def test_keyword_args(self):
        assert prev_fast_len(11, real=True) == 10
        assert prev_fast_len(target=7, real=False) == 7


class Test_init_nd_shape_and_axes:

    def test_py_0d_defaults(self):
        x = np.array(4)
        shape = None
        axes = None

        shape_expected = np.array([])
        axes_expected = np.array([])

        shape_res, axes_res = _init_nd_shape_and_axes(x, shape, axes)

        assert_equal(shape_res, shape_expected)
        assert_equal(axes_res, axes_expected)

    def test_np_0d_defaults(self):
        x = np.array(7.)
        shape = None
        axes = None

        shape_expected = np.array([])
        axes_expected = np.array([])

        shape_res, axes_res = _init_nd_shape_and_axes(x, shape, axes)

        assert_equal(shape_res, shape_expected)
        assert_equal(axes_res, axes_expected)

    def test_py_1d_defaults(self):
        x = np.array([1, 2, 3])
        shape = None
        axes = None

        shape_expected = np.array([3])
        axes_expected = np.array([0])

        shape_res, axes_res = _init_nd_shape_and_axes(x, shape, axes)

        assert_equal(shape_res, shape_expected)
        assert_equal(axes_res, axes_expected)

    def test_np_1d_defaults(self):
        x = np.arange(0, 1, .1)
        shape = None
        axes = None

        shape_expected = np.array([10])
        axes_expected = np.array([0])

        shape_res, axes_res = _init_nd_shape_and_axes(x, shape, axes)

        assert_equal(shape_res, shape_expected)
        assert_equal(axes_res, axes_expected)

    def test_py_2d_defaults(self):
        x = np.array([[1, 2, 3, 4],
                      [5, 6, 7, 8]])
        shape = None
        axes = None

        shape_expected = np.array([2, 4])
        axes_expected = np.array([0, 1])

        shape_res, axes_res = _init_nd_shape_and_axes(x, shape, axes)

        assert_equal(shape_res, shape_expected)
        assert_equal(axes_res, axes_expected)

    def test_np_2d_defaults(self):
        x = np.arange(0, 1, .1).reshape(5, 2)
        shape = None
        axes = None

        shape_expected = np.array([5, 2])
        axes_expected = np.array([0, 1])

        shape_res, axes_res = _init_nd_shape_and_axes(x, shape, axes)

        assert_equal(shape_res, shape_expected)
        assert_equal(axes_res, axes_expected)

    def test_np_5d_defaults(self):
        x = np.zeros([6, 2, 5, 3, 4])
        shape = None
        axes = None

        shape_expected = np.array([6, 2, 5, 3, 4])
        axes_expected = np.array([0, 1, 2, 3, 4])

        shape_res, axes_res = _init_nd_shape_and_axes(x, shape, axes)

        assert_equal(shape_res, shape_expected)
        assert_equal(axes_res, axes_expected)

    def test_np_5d_set_shape(self):
        x = np.zeros([6, 2, 5, 3, 4])
        shape = [10, -1, -1, 1, 4]
        axes = None

        shape_expected = np.array([10, 2, 5, 1, 4])
        axes_expected = np.array([0, 1, 2, 3, 4])

        shape_res, axes_res = _init_nd_shape_and_axes(x, shape, axes)

        assert_equal(shape_res, shape_expected)
        assert_equal(axes_res, axes_expected)

    def test_np_5d_set_axes(self):
        x = np.zeros([6, 2, 5, 3, 4])
        shape = None
        axes = [4, 1, 2]

        shape_expected = np.array([4, 2, 5])
        axes_expected = np.array([4, 1, 2])

        shape_res, axes_res = _init_nd_shape_and_axes(x, shape, axes)

        assert_equal(shape_res, shape_expected)
        assert_equal(axes_res, axes_expected)

    def test_np_5d_set_shape_axes(self):
        x = np.zeros([6, 2, 5, 3, 4])
        shape = [10, -1, 2]
        axes = [1, 0, 3]

        shape_expected = np.array([10, 6, 2])
        axes_expected = np.array([1, 0, 3])

        shape_res, axes_res = _init_nd_shape_and_axes(x, shape, axes)

        assert_equal(shape_res, shape_expected)
        assert_equal(axes_res, axes_expected)

    def test_shape_axes_subset(self):
        x = np.zeros((2, 3, 4, 5))
        shape, axes = _init_nd_shape_and_axes(x, shape=(5, 5, 5), axes=None)

        assert_array_equal(shape, [5, 5, 5])
        assert_array_equal(axes, [1, 2, 3])

    def test_errors(self):
        x = np.zeros(1)
        with assert_raises(ValueError, match="axes must be a scalar or "
                           "iterable of integers"):
            _init_nd_shape_and_axes(x, shape=None, axes=[[1, 2], [3, 4]])

        with assert_raises(ValueError, match="axes must be a scalar or "
                           "iterable of integers"):
            _init_nd_shape_and_axes(x, shape=None, axes=[1., 2., 3., 4.])

        with assert_raises(ValueError,
                           match="axes exceeds dimensionality of input"):
            _init_nd_shape_and_axes(x, shape=None, axes=[1])

        with assert_raises(ValueError,
                           match="axes exceeds dimensionality of input"):
            _init_nd_shape_and_axes(x, shape=None, axes=[-2])

        with assert_raises(ValueError,
                           match="all axes must be unique"):
            _init_nd_shape_and_axes(x, shape=None, axes=[0, 0])

        with assert_raises(ValueError, match="shape must be a scalar or "
                           "iterable of integers"):
            _init_nd_shape_and_axes(x, shape=[[1, 2], [3, 4]], axes=None)

        with assert_raises(ValueError, match="shape must be a scalar or "
                           "iterable of integers"):
            _init_nd_shape_and_axes(x, shape=[1., 2., 3., 4.], axes=None)

        with assert_raises(ValueError,
                           match="when given, axes and shape arguments"
                           " have to be of the same length"):
            _init_nd_shape_and_axes(np.zeros([1, 1, 1, 1]),
                                    shape=[1, 2, 3], axes=[1])

        with assert_raises(ValueError,
                           match="invalid number of data points"
                           r" \(\[0\]\) specified"):
            _init_nd_shape_and_axes(x, shape=[0], axes=None)

        with assert_raises(ValueError,
                           match="invalid number of data points"
                           r" \(\[-2\]\) specified"):
            _init_nd_shape_and_axes(x, shape=-2, axes=None)
