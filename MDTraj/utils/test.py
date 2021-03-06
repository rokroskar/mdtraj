##############################################################################
# MDTraj: A Python Library for Loading, Saving, and Manipulating
#         Molecular Dynamics Trajectories.
# Copyright 2012-2013 Stanford University and the Authors
#
# Authors: Robert McGibbon
# Contributors:
#
# MDTraj is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 2.1
# of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with MDTraj. If not, see <http://www.gnu.org/licenses/>.
##############################################################################

"""Tests for some of the utilities
"""
##############################################################################
# imports
##############################################################################

from __future__ import print_function, division
import numpy as np
from mdtraj.utils import ensure_type
from mdtraj.utils.validation import TypeCastPerformanceWarning
from mdtraj.utils.unit import in_units_of, _str_to_unit
from mdtraj.utils import import_, lengths_and_angles_to_box_vectors
from mdtraj.testing import raises, eq
import warnings

##############################################################################
# globals
##############################################################################

a = np.ones(10, dtype=np.float32)
b = np.ones((10,10), dtype=np.float64, order='F')

##############################################################################
# tests
##############################################################################

def test_unitcell_0():
    result = lengths_and_angles_to_box_vectors(1, 1, 1, 90.0, 90.0, 90.0)
    expected = (np.array([1, 0, 0]), np.array([ 0.,  1.,  0.]), np.array([ 0.,  0.,  1.]))
    for (a, b) in zip(result, expected):
        np.testing.assert_array_almost_equal(a, b)

def test_ensure_type_1():
    ensure_type(a, np.float32, 1, '', length=10)


def test_ensure_type_2():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        val = ensure_type(a, np.float64, 1, '', length=10)

        assert val.dtype == np.float64
        assert a.dtype == np.float32  # a should not be changed
        assert len(w) == 1
        assert issubclass(w[-1].category, TypeCastPerformanceWarning)


def test_ensure_type_25():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        val = ensure_type(a, np.float64, 1, '', length=10, warn_on_cast=False)

        assert val.dtype == np.float64
        assert a.dtype == np.float32  # a should not be changed
        assert len(w) == 0  # no warning since we set warn_on_cast to False


@raises(ValueError)
def test_ensure_type_3():
    ensure_type(a, np.float32, 1, '', length=11)


def test_ensure_type_4():
    ensure_type(None, np.float64, 1, '', length=11, can_be_none=True)


@raises(ValueError)
def test_ensure_type_5():
    ensure_type(a, np.float32, 1, '', length=11, can_be_none=True)


def test_ensure_type_6():
    val = ensure_type(b, np.float64, 2, '', shape=(10,10))
    assert val.flags.c_contiguous is True


def test_ensure_type_7():
    c = ensure_type(a, np.float32, ndim=2, name='', add_newaxis_on_deficient_ndim=True)
    assert c.shape == (1, len(a))


def test_ensure_type_8():
    c = ensure_type(np.zeros((5,10)), np.float32, ndim=2, name='', shape=(None, 10))
    assert c.shape == (5, 10)

@raises(ValueError)
def test_ensure_type_9():
    c = ensure_type(np.zeros((5,11)), np.float32, ndim=2, name='', shape=(None, 10))

@raises(TypeError)
def test_ensure_type_10():
    c = ensure_type([0,1], np.float32, ndim=2, name='')

def test_ensure_type_11():
    c = ensure_type(0, np.float32, ndim=1, name='', add_newaxis_on_deficient_ndim=True)
    assert c.shape == (1,)

@raises(TypeError)
def test_ensure_type_12():
    ensure_type(np.zeros((2,2)), np.float32, ndim=3)

@raises(ValueError)
def test_ensure_type_13():
    ensure_type(np.zeros((2,2)), np.float32, ndim=2, name='', shape=(None, None, None))

@raises(ImportError)
def test_delay_import_fail_1():
    import_('sdfsdfsfsfdsdf')

def test_delay_import():
    import_('scipy.sparse')

def test_unit_0():
    a = np.array([1.0])
    b = in_units_of(a, 'nanometers', 'angstroms', inplace=False)
    c = in_units_of(a, 'angstroms', 'nanometers', inplace=False)
    eq(b, np.array([10.0]))
    eq(c, np.array([0.1]))
    assert a.ctypes.data != b.ctypes.data
    assert a.ctypes.data != c.ctypes.data


def test_unit_1():
    a = np.array([1.0])
    b = in_units_of(a, 'nanometers', 'angstroms', inplace=True)
    eq(a, np.array([10.0]))
    eq(b, np.array([10.0]))
    # a and b point to the same memory
    assert a.ctypes.data == b.ctypes.data


def test_unit_2():
    a = np.array([1.0])
    a.flags['WRITEABLE'] = False
    b = in_units_of(a, 'nanometers', 'angstroms', inplace=True)

    eq(b, np.array([10.0]))
    # a and b do not point to the same memory, since a isn't writeable
    assert a.ctypes.data != b.ctypes.data


def test_unit_3():
    eq(1000000.0, in_units_of(1, 'meter**2/second', 'nanometers**2/picosecond'))
