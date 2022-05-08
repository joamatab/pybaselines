# -*- coding: utf-8 -*-
"""Tests for pybaselines.utils.

@author: Donald Erb
Created on March 20, 2021

"""

import numpy as np
from numpy.testing import assert_allclose, assert_array_equal
import pytest
from scipy.sparse import identity

from pybaselines import utils

from .conftest import gaussian


@pytest.fixture(scope='module')
def _x_data():
    """x-values for testing."""
    return np.linspace(-20, 20)


@pytest.mark.parametrize('sigma', [0.1, 1, 10])
@pytest.mark.parametrize('center', [-10, 0, 10])
@pytest.mark.parametrize('height', [0.1, 1, 10])
def test_gaussian(_x_data, height, center, sigma):
    """Ensures that gaussian function in pybaselines.utils is correct."""
    assert_allclose(
        utils.gaussian(_x_data, height, center, sigma),
        gaussian(_x_data, height, center, sigma), 1e-12, 1e-12
    )


@pytest.mark.parametrize('window_size', (1, 20, 100))
@pytest.mark.parametrize('sigma', (1, 2, 5))
def test_gaussian_kernel(window_size, sigma):
    """
    Tests gaussian_kernel for various window_sizes and sigma values.

    Ensures area is always 1, so that kernel is normalized.
    """
    kernel = utils.gaussian_kernel(window_size, sigma)

    assert kernel.size == window_size
    assert kernel.shape == (window_size,)
    assert_allclose(np.sum(kernel), 1)


def test_gaussian_kernel_0_windowsize(data_fixture):
    """
    Ensures the gaussian kernel with 0 window size gives an array of [1].

    Also ensures the convolution with the kernel gives the unchanged input.
    """
    kernel = utils.gaussian_kernel(0, 3)

    assert kernel.size == 1
    assert kernel.shape == (1,)
    assert_array_equal(kernel, 1)
    assert_allclose(np.sum(kernel), 1)

    x, y = data_fixture
    out = utils.padded_convolve(y, kernel)
    assert_array_equal(y, out)


@pytest.mark.parametrize('sign', (1, -1))
def test_relative_difference_scalar(sign):
    """Tests relative_difference to ensure it uses abs for scalars."""
    old = 3.0 * sign
    new = 4
    assert_allclose(utils.relative_difference(old, new), abs((old - new) / old))


def test_relative_difference_array():
    """Tests relative_difference to ensure it uses l2 norm for arrays."""
    a = np.array([1, 2, 3])
    b = np.array([4, 5, 6])
    norm_ab = np.sqrt(((a - b)**2).sum())
    norm_a = np.sqrt(((a)**2).sum())

    assert_allclose(utils.relative_difference(a, b), norm_ab / norm_a)


def test_relative_difference_array_l1():
    """Tests `norm_order` keyword for relative_difference."""
    a = np.array([1, 2, 3])
    b = np.array([4, 5, 6])
    norm_ab = np.abs(a - b).sum()
    norm_a = np.abs(a).sum()

    assert_allclose(utils.relative_difference(a, b, 1), norm_ab / norm_a)


def test_relative_difference_zero():
    """Ensures relative difference works when 0 is the denominator."""
    a = np.array([0, 0, 0])
    b = np.array([4, 5, 6])
    norm_ab = np.sqrt(((a - b)**2).sum())

    assert_allclose(utils.relative_difference(a, b), norm_ab / np.finfo(float).eps)


def test_interp_inplace():
    """Tests that _interp_inplace modified the input array inplace."""
    x = np.arange(10)
    y_actual = 2 + 5 * x

    y_calc = np.empty_like(y_actual)
    y_calc[0] = y_actual[0]
    y_calc[-1] = y_actual[-1]

    output = utils._interp_inplace(x, y_calc, y_calc[0], y_calc[-1])

    # output should be the same object as the input y array
    assert output is y_calc

    assert_allclose(y_calc, y_actual, 1e-12)


@pytest.mark.parametrize('x', (np.array([-5, -2, 0, 1, 8]), np.array([1, 2, 3, 4, 5])))
@pytest.mark.parametrize(
    'coefs', (
        np.array([1, 2]), np.array([-1, 10, 0.2]), np.array([0, 1, 0]),
        np.array([0, 0, 0]), np.array([2, 1e-19])
    )
)
def test_convert_coef(x, coefs):
    """Checks that polynomial coefficients are correctly converted to the original domain."""
    original_domain = np.array([x.min(), x.max()])
    y = np.zeros_like(x)
    for i, coef in enumerate(coefs):
        y = y + coef * x**i

    fit_polynomial = np.polynomial.Polynomial.fit(x, y, coefs.size - 1)
    # fit_coefs correspond to the domain [-1, 1] rather than the original
    # domain of x
    fit_coefs = fit_polynomial.coef

    converted_coefs = utils._convert_coef(fit_coefs, original_domain)

    assert_allclose(converted_coefs, coefs, atol=1e-10)


@pytest.mark.parametrize('diff_order', (0, 1, 2, 3, 4, 5))
def test_difference_matrix(diff_order):
    """Tests common differential matrices."""
    diff_matrix = utils.difference_matrix(10, diff_order).toarray()
    numpy_diff = np.diff(np.eye(10), diff_order).T

    assert_array_equal(diff_matrix, numpy_diff)


def test_difference_matrix_order_2():
    """
    Tests the 2nd order differential matrix against the actual representation.

    The 2nd order differential matrix is most commonly used,
    so double-check that it is correct.
    """
    diff_matrix = utils.difference_matrix(8, 2).toarray()
    actual_matrix = np.array([
        [1, -2, 1, 0, 0, 0, 0, 0],
        [0, 1, -2, 1, 0, 0, 0, 0],
        [0, 0, 1, -2, 1, 0, 0, 0],
        [0, 0, 0, 1, -2, 1, 0, 0],
        [0, 0, 0, 0, 1, -2, 1, 0],
        [0, 0, 0, 0, 0, 1, -2, 1]
    ])

    assert_array_equal(diff_matrix, actual_matrix)


def test_difference_matrix_order_0():
    """
    Tests the 0th order differential matrix against the actual representation.

    The 0th order differential matrix should be the same as the identity matrix,
    so double-check that it is correct.
    """
    diff_matrix = utils.difference_matrix(10, 0).toarray()
    actual_matrix = identity(10).toarray()

    assert_array_equal(diff_matrix, actual_matrix)


def test_difference_matrix_order_neg():
    """Ensures differential matrix fails for negative order."""
    with pytest.raises(ValueError):
        utils.difference_matrix(10, diff_order=-2)


def test_difference_matrix_order_over():
    """
    Tests the (n + 1)th order differential matrix against the actual representation.

    If n is the number of data points and the difference order is greater than n,
    then differential matrix should have a shape of (0, n) with 0 stored elements,
    following a similar logic as np.diff.

    """
    diff_matrix = utils.difference_matrix(10, 11).toarray()
    actual_matrix = np.empty(shape=(0, 10))

    assert_array_equal(diff_matrix, actual_matrix)


def test_difference_matrix_size_neg():
    """Ensures differential matrix fails for negative data size."""
    with pytest.raises(ValueError):
        utils.difference_matrix(-1)


@pytest.mark.parametrize('form', ('dia', 'csc', 'csr'))
def test_difference_matrix_formats(form):
    """
    Ensures that the sparse format is correctly passed to the constructor.

    Tests both 0-order and 2-order, since 0-order uses a different constructor.
    """
    assert utils.difference_matrix(10, 2, form).format == form
    assert utils.difference_matrix(10, 0, form).format == form


def pad_func(array, pad_width, axis, kwargs):
    """A custom padding function for use with numpy.pad."""
    pad_val = kwargs.get('pad_val', 0)
    array[:pad_width[0]] = pad_val
    if pad_width[1] != 0:
        array[-pad_width[1]:] = pad_val


@pytest.mark.parametrize('kernel_size', (1, 10, 31, 1000, 2000, 4000))
@pytest.mark.parametrize('pad_mode', ('reflect', 'extrapolate', pad_func))
@pytest.mark.parametrize('list_input', (False, True))
def test_padded_convolve(kernel_size, pad_mode, list_input, data_fixture):
    """
    Ensures the output of the padded convolution is the same size as the input data.

    Notes
    -----
    `data_fixture` has 1000 data points, so test kernels with size less than, equal to,
    and greater than that size.

    """
    # make a simple uniform window kernel
    kernel = np.ones(kernel_size) / kernel_size
    _, data = data_fixture
    input_data = data.tolist() if list_input else data
    conv_output = utils.padded_convolve(input_data, kernel, pad_mode)

    assert isinstance(conv_output, np.ndarray)
    assert data.shape == conv_output.shape


def test_padded_convolve_empty_kernel():
    """Ensures convolving with an empty kernel fails."""
    with pytest.raises(ValueError):
        utils.padded_convolve(np.arange(10), np.array([]))


@pytest.mark.parametrize(
    'pad_mode', ('reflect', 'REFLECT', 'extrapolate', 'edge', 'constant', pad_func)
)
@pytest.mark.parametrize('pad_length', (0, 1, 2, 20, 500, 1000, 2000, 4000))
@pytest.mark.parametrize('list_input', (False, True))
def test_pad_edges(pad_mode, pad_length, list_input, data_fixture):
    """Tests various inputs for utils.pad_edges."""
    _, data = data_fixture
    if list_input:
        data = data.tolist()

    np_pad_mode = pad_mode if callable(pad_mode) else pad_mode.lower()
    if np_pad_mode != 'extrapolate':
        expected_output = np.pad(data, pad_length, np_pad_mode)
    else:
        expected_output = None

    output = utils.pad_edges(data, pad_length, pad_mode)
    assert isinstance(output, np.ndarray)
    assert len(output) == len(data) + 2 * pad_length

    if expected_output is not None:
        assert_allclose(output, expected_output)


@pytest.mark.parametrize('pad_length', (0, 1, 2, 20, 500, 1000, 2000, 4000))
@pytest.mark.parametrize('extrapolate_window', (None, 1, 2, 10, 1001, (10, 20), (1, 1)))
@pytest.mark.parametrize('list_input', (False, True))
def test_pad_edges_extrapolate(pad_length, list_input, extrapolate_window, data_fixture):
    """Ensures extrapolation works for utils.pad_edges."""
    _, data = data_fixture
    if list_input:
        data = data.tolist()

    output = utils.pad_edges(data, pad_length, 'extrapolate', extrapolate_window)
    assert isinstance(output, np.ndarray)
    assert len(output) == len(data) + 2 * pad_length


def test_pad_edges_extrapolate_windows():
    """Ensures the separate extrapolate windows are correctly interpreted."""
    input_array = np.zeros(50)
    input_array[-10:] = 1.
    extrapolate_windows = [40, 10]
    pad_len = 20
    output = utils.pad_edges(input_array, pad_len, extrapolate_window=extrapolate_windows)

    assert_allclose(output[:pad_len], np.full(pad_len, 0.), 1e-14)
    assert_allclose(output[-pad_len:], np.full(pad_len, 1.), 1e-14)


@pytest.mark.parametrize('extrapolate_window', (0, (0, 0), (5, 0), (5, -1)))
def test_pad_edges_extrapolate_zero_window(extrapolate_window):
    """Ensures an extrapolate_window <= 0 raises an exception."""
    with pytest.raises(ValueError):
        utils.pad_edges(np.arange(10), 10, extrapolate_window=extrapolate_window)


@pytest.mark.parametrize('pad_mode', ('reflect', 'extrapolate'))
def test_pad_edges_negative_pad_length(pad_mode, data_fixture):
    """Ensures a negative pad length raises an exception."""
    with pytest.raises(ValueError):
        utils.pad_edges(data_fixture[1], -5, pad_mode)


@pytest.mark.parametrize('pad_mode', ('reflect', 'extrapolate'))
def test_get_edges_negative_pad_length(pad_mode, data_fixture):
    """Ensures a negative pad length raises an exception."""
    with pytest.raises(ValueError):
        utils._get_edges(data_fixture[1], -5, pad_mode)


def test_pad_edges_custom_pad_func():
    """Ensures pad_edges works with a callable padding function, same as numpy.pad."""
    input_array = np.arange(20)
    pad_val = 20
    pad_length = 10

    edge_array = np.full(pad_length, pad_val)
    expected_output = np.concatenate((edge_array, input_array, edge_array))

    actual_output = utils.pad_edges(input_array, pad_length, pad_func, pad_val=pad_val)

    assert_array_equal(actual_output, expected_output)


def test_get_edges_custom_pad_func():
    """Ensures _get_edges works with a callable padding function, same as numpy.pad."""
    input_array = np.arange(20)
    pad_val = 20
    pad_length = 10

    expected_output = np.full(pad_length, pad_val)

    left, right = utils._get_edges(input_array, pad_length, pad_func, pad_val=pad_val)

    assert_array_equal(left, expected_output)
    assert_array_equal(right, expected_output)


@pytest.mark.parametrize(
    'pad_mode', ('reflect', 'REFLECT', 'extrapolate', 'edge', 'constant', pad_func)
)
@pytest.mark.parametrize('pad_length', (0, 1, 2, 20, 500, 1000, 2000, 4000))
@pytest.mark.parametrize('list_input', (False, True))
def test_get_edges(pad_mode, pad_length, list_input, data_fixture):
    """Tests various inputs for utils._get_edges."""
    _, data = data_fixture
    if list_input:
        data = data.tolist()

    np_pad_mode = pad_mode if callable(pad_mode) else pad_mode.lower()
    if pad_length == 0:
        check_output = True
        expected_left = np.array([])
        expected_right = np.array([])
    elif np_pad_mode != 'extrapolate':
        check_output = True
        expected_left, _, expected_right = np.array_split(
            np.pad(data, pad_length, np_pad_mode), [pad_length, -pad_length]
        )
    else:
        check_output = False

    left, right = utils._get_edges(data, pad_length, pad_mode)
    assert isinstance(left, np.ndarray)
    assert len(left) == pad_length
    assert isinstance(right, np.ndarray)
    assert len(right) == pad_length

    if check_output:
        assert_allclose(left, expected_left)
        assert_allclose(right, expected_right)


@pytest.mark.parametrize('fill_scalar', (True, False))
@pytest.mark.parametrize('list_input', (True, False))
@pytest.mark.parametrize('nested_input', (True, False))
def test_check_scalar_scalar_input(fill_scalar, list_input, nested_input):
    """Ensures _check_scalar works with scalar values."""
    input_data = 5
    desired_length = 10
    if fill_scalar:
        desired_output = np.full(desired_length, input_data)
    else:
        desired_output = np.asarray(input_data)
    if nested_input:
        input_data = [input_data]
    if list_input:
        input_data = [input_data]

    output, was_scalar = utils._check_scalar(input_data, desired_length)

    assert was_scalar
    assert isinstance(output, np.ndarray)
    assert_array_equal(output, desired_output)


@pytest.mark.parametrize('fit_desired_length', (True, False))
@pytest.mark.parametrize('list_input', (True, False))
@pytest.mark.parametrize('nested_input', (True, False))
def test_check_scalar_array_input(fit_desired_length, list_input, nested_input):
    """Ensures _check_scalar works with array-like inputs."""
    desired_length = 20
    fill_value = 5
    if fit_desired_length:
        input_data = np.full(desired_length, fill_value)
    else:
        input_data = np.full(desired_length - 1, fill_value)

    if nested_input:
        input_data = input_data.reshape(-1, 1)
    if list_input:
        input_data = input_data.tolist()

    if fit_desired_length:
        output, was_scalar = utils._check_scalar(input_data, desired_length)

        assert not was_scalar
        assert isinstance(output, np.ndarray)
        assert_array_equal(output, np.asarray(input_data).reshape(-1))
    else:
        with pytest.raises(ValueError):
            utils._check_scalar(input_data, desired_length)


def test_check_scalar_asarray_kwargs():
    """Ensures kwargs are passed to np.asarray by _check_scalar."""
    for dtype in (int, float, np.float64, np.int64):
        output, _ = utils._check_scalar(20, 1, dtype=dtype)
        assert output.dtype == dtype

        output, _ = utils._check_scalar(20, 10, True, dtype=dtype)
        assert output.dtype == dtype

        output, _ = utils._check_scalar([20], 1, dtype=dtype)
        assert output.dtype == dtype

        output, _ = utils._check_scalar(np.array([1, 2, 3]), 3, dtype=dtype)
        assert output.dtype == dtype


@pytest.mark.parametrize('seed', (123, 98765))
def test_invert_sort(seed):
    """Ensures the inverted sort works."""
    # TODO replace with np.random.default_rng once minimum numpy version is >= 1.17
    values = np.random.RandomState(seed).normal(0, 10, 1000)
    sort_order = values.argsort(kind='mergesort')

    expected_inverted_sort = sort_order.argsort(kind='mergesort')
    inverted_order = utils._inverted_sort(sort_order)

    assert_array_equal(expected_inverted_sort, inverted_order)
    assert_array_equal(values, values[sort_order][inverted_order])
