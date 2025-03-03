# -*- coding: utf-8 -*-
"""Tests for pybaselines.morphological.

@author: Donald Erb
Created on March 20, 2021

"""

from unittest import mock

import numpy as np
from numpy.testing import assert_allclose
import pytest

from pybaselines import _algorithm_setup, morphological

from .conftest import AlgorithmTester, get_data, has_pentapy


class TestMPLS(AlgorithmTester):
    """Class for testing mpls baseline."""

    func = morphological.mpls

    def test_unchanged_data(self, data_fixture):
        """Ensures that input data is unchanged by the function."""
        x, y = get_data()
        self._test_unchanged_data(data_fixture, y, None, y)

    def test_output(self):
        """Ensures that the output has the desired format."""
        self._test_output(self.y, self.y, checked_keys=('weights', 'half_window'))

    def test_list_input(self):
        """Ensures that function works the same for both array and list inputs."""
        y_list = self.y.tolist()
        self._test_algorithm_list(array_args=(self.y,), list_args=(y_list,))

    @pytest.mark.parametrize('diff_order', (1, 3))
    def test_diff_orders(self, diff_order):
        """Ensure that other difference orders work."""
        lam = {1: 1e4, 3: 1e10}[diff_order]
        self._call_func(self.y, lam=lam, diff_order=diff_order)

    @has_pentapy
    def test_pentapy_solver(self):
        """Ensure pentapy solver gives similar result to SciPy's solver."""
        with mock.patch.object(_algorithm_setup, '_HAS_PENTAPY', False):
            scipy_output = self._call_func(self.y)[0]
        pentapy_output = self._call_func(self.y)[0]

        assert_allclose(pentapy_output, scipy_output, 1e-4)

    @pytest.mark.parametrize('p', (-1, 2))
    def test_outside_p_fails(self, p):
        """Ensures p values outside of [0, 1] raise an exception."""
        with pytest.raises(ValueError):
            self._call_func(self.y, p=p)


class TestMor(AlgorithmTester):
    """Class for testing mor baseline."""

    func = morphological.mor

    def test_unchanged_data(self, data_fixture):
        """Ensures that input data is unchanged by the function."""
        x, y = get_data()
        self._test_unchanged_data(data_fixture, y, None, y)

    def test_output(self):
        """Ensures that the output has the desired format."""
        self._test_output(self.y, self.y, checked_keys=('half_window',))

    def test_list_input(self):
        """Ensures that function works the same for both array and list inputs."""
        y_list = self.y.tolist()
        self._test_algorithm_list(array_args=(self.y,), list_args=(y_list,))


class TestIMor(AlgorithmTester):
    """Class for testing imor baseline."""

    func = morphological.imor

    def test_unchanged_data(self, data_fixture):
        """Ensures that input data is unchanged by the function."""
        x, y = get_data()
        self._test_unchanged_data(data_fixture, y, None, y)

    def test_output(self):
        """Ensures that the output has the desired format."""
        self._test_output(self.y, self.y, checked_keys=('half_window', 'tol_history'))

    def test_list_input(self):
        """Ensures that function works the same for both array and list inputs."""
        y_list = self.y.tolist()
        self._test_algorithm_list(array_args=(self.y,), list_args=(y_list,))

    def test_tol_history(self):
        """Ensures the 'tol_history' item in the parameter output is correct."""
        max_iter = 5
        _, params = self._call_func(self.y, max_iter=max_iter, tol=-1)

        assert params['tol_history'].size == max_iter + 1


class TestAMorMol(AlgorithmTester):
    """Class for testing amormol baseline."""

    func = morphological.amormol

    def test_unchanged_data(self, data_fixture):
        """Ensures that input data is unchanged by the function."""
        x, y = get_data()
        self._test_unchanged_data(data_fixture, y, None, y)

    def test_output(self):
        """Ensures that the output has the desired format."""
        self._test_output(self.y, self.y, checked_keys=('half_window', 'tol_history'))

    def test_list_input(self):
        """Ensures that function works the same for both array and list inputs."""
        y_list = self.y.tolist()
        self._test_algorithm_list(array_args=(self.y,), list_args=(y_list,))

    def test_tol_history(self):
        """Ensures the 'tol_history' item in the parameter output is correct."""
        max_iter = 5
        _, params = self._call_func(self.y, max_iter=max_iter, tol=-1)

        assert params['tol_history'].size == max_iter + 1


class TestMorMol(AlgorithmTester):
    """Class for testing mormol baseline."""

    func = morphological.mormol

    def test_unchanged_data(self, data_fixture):
        """Ensures that input data is unchanged by the function."""
        x, y = get_data()
        self._test_unchanged_data(data_fixture, y, None, y)

    def test_output(self):
        """Ensures that the output has the desired format."""
        self._test_output(self.y, self.y, checked_keys=('half_window', 'tol_history'))

    def test_list_input(self):
        """Ensures that function works the same for both array and list inputs."""
        y_list = self.y.tolist()
        self._test_algorithm_list(array_args=(self.y,), list_args=(y_list,))

    def test_tol_history(self):
        """Ensures the 'tol_history' item in the parameter output is correct."""
        max_iter = 5
        _, params = self._call_func(self.y, max_iter=max_iter, tol=-1)

        assert params['tol_history'].size == max_iter + 1


class TestRollingBall(AlgorithmTester):
    """Class for testing rolling ball baseline."""

    func = morphological.rolling_ball

    @pytest.mark.parametrize('half_window', (None, 10))
    @pytest.mark.parametrize('smooth_half_window', (None, 0, 1))
    def test_unchanged_data(self, data_fixture, half_window, smooth_half_window):
        """Ensures that input data is unchanged by the function."""
        x, y = get_data()
        self._test_unchanged_data(data_fixture, y, None, y, half_window, smooth_half_window)

    def test_output(self):
        """Ensures that the output has the desired format."""
        self._test_output(self.y, self.y, checked_keys=('half_window',))

    def test_list_input(self):
        """Ensures that function works the same for both array and list inputs."""
        y_list = self.y.tolist()
        self._test_algorithm_list(array_args=(self.y,), list_args=(y_list,))

    @pytest.mark.parametrize('smooth_half_window', (None, 0, 10))
    def test_smooth_half_windows(self, smooth_half_window):
        """Ensures smooth-half-window is correctly processed."""
        output = self._call_func(self.y, smooth_half_window=smooth_half_window)

        assert output[0].shape == self.y.shape


class TestMWMV(AlgorithmTester):
    """Class for testing mwmv baseline."""

    func = morphological.mwmv

    def test_unchanged_data(self, data_fixture):
        """Ensures that input data is unchanged by the function."""
        x, y = get_data()
        self._test_unchanged_data(data_fixture, y, None, y)

    def test_output(self):
        """Ensures that the output has the desired format."""
        self._test_output(self.y, self.y, checked_keys=('half_window',))

    def test_list_input(self):
        """Ensures that function works the same for both array and list inputs."""
        y_list = self.y.tolist()
        self._test_algorithm_list(array_args=(self.y,), list_args=(y_list,))

    @pytest.mark.parametrize('smooth_half_window', (None, 0, 10))
    def test_smooth_half_windows(self, smooth_half_window):
        """Ensures smooth-half-window is correctly processed."""
        output = self._call_func(self.y, smooth_half_window=smooth_half_window)

        assert output[0].shape == self.y.shape


class TestTophat(AlgorithmTester):
    """Class for testing tophat baseline."""

    func = morphological.tophat

    def test_unchanged_data(self, data_fixture):
        """Ensures that input data is unchanged by the function."""
        x, y = get_data()
        self._test_unchanged_data(data_fixture, y, None, y)

    def test_output(self):
        """Ensures that the output has the desired format."""
        self._test_output(self.y, self.y, checked_keys=('half_window',))

    def test_list_input(self):
        """Ensures that function works the same for both array and list inputs."""
        y_list = self.y.tolist()
        self._test_algorithm_list(array_args=(self.y,), list_args=(y_list,))


class TestMpsline(AlgorithmTester):
    """Class for testing mpsline baseline."""

    func = morphological.mpspline

    def test_unchanged_data(self, data_fixture):
        """Ensures that input data is unchanged by the function."""
        x, y = get_data()
        self._test_unchanged_data(data_fixture, y, None, y)

    def test_output(self):
        """Ensures that the output has the desired format."""
        self._test_output(self.y, self.y, checked_keys=('weights', 'half_window'))

    def test_no_x(self):
        """Ensures that function output is the same when no x is input."""
        self._test_algorithm_no_x(
            with_args=(self.y,), without_args=(self.y,), with_kwargs={'x_data': self.x}
        )

    def test_list_input(self):
        """Ensures that function works the same for both array and list inputs."""
        y_list = self.y.tolist()
        self._test_algorithm_list(array_args=(self.y,), list_args=(y_list,))

    @pytest.mark.parametrize('diff_order', (1, 3))
    def test_diff_orders(self, diff_order):
        """Ensure that other difference orders work."""
        lam = {1: 1e1, 3: 1e6}[diff_order]
        self._call_func(self.y, lam=lam, diff_order=diff_order)

    @pytest.mark.parametrize('spline_degree', (2, 4))
    def test_spline_degrees(self, spline_degree):
        """Ensure that other spline degrees work."""
        self._call_func(self.y, spline_degree=spline_degree)

    @pytest.mark.parametrize('p', (-1, 2))
    def test_outside_p_fails(self, p):
        """Ensures p values outside of [0, 1] raise an exception."""
        with pytest.raises(ValueError):
            self._call_func(self.y, p=p)


class TestJBCD(AlgorithmTester):
    """Class for testing jbcd baseline."""

    func = morphological.jbcd

    @pytest.mark.parametrize('robust_opening', (False, True))
    def test_unchanged_data(self, data_fixture, robust_opening):
        """Ensures that input data is unchanged by the function."""
        x, y = get_data()
        self._test_unchanged_data(data_fixture, y, None, y, robust_opening=robust_opening)

    def test_output(self):
        """Ensures that the output has the desired format."""
        self._test_output(self.y, self.y, checked_keys=('half_window', 'tol_history', 'signal'))

    def test_list_input(self):
        """Ensures that function works the same for both array and list inputs."""
        y_list = self.y.tolist()
        self._test_algorithm_list(array_args=(self.y,), list_args=(y_list,))

    @pytest.mark.parametrize('diff_order', (2, 3))
    def test_diff_orders(self, diff_order):
        """Ensure that other difference orders work."""
        factor = {2: 1e4, 3: 1e10}[diff_order]

        self._call_func(self.y, beta=factor, gamma=factor, diff_order=diff_order)

    @has_pentapy
    def test_pentapy_solver(self):
        """Ensure pentapy solver gives similar result to SciPy's solver."""
        with mock.patch.object(morphological, '_HAS_PENTAPY', False):
            scipy_output = self._call_func(self.y, diff_order=2)[0]
        pentapy_output = self._call_func(self.y, diff_order=2)[0]

        assert_allclose(pentapy_output, scipy_output, 1e-4)

    def test_zero_gamma_passes(self):
        """Ensures gamma can be 0, which just does baseline correction without denoising."""
        self._call_func(self.y, gamma=0)

    def test_zero_beta_fails(self):
        """Ensures a beta equal to 0 raises an exception."""
        with pytest.raises(ValueError):
            self._call_func(self.y, beta=0)

    def test_array_beta_gamma_fails(self):
        """Ensures array-like beta or gamma values raise an exception."""
        array_vals = np.ones_like(self.y)
        with pytest.raises(ValueError):
            self._call_func(self.y, beta=array_vals)
        with pytest.raises(ValueError):
            self._call_func(self.y, gamma=array_vals)
