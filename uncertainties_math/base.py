import numpy as np
import uncertainties
from uncertainties import unumpy
from uncertainties import ufloat


def is_unumpy(arr):
	try:
		return any([isinstance(arr[i], uncertainties.core.AffineScalarFunc) for i in range(len(arr))])
	except TypeError:
		return False


def is_ufloat(x):
	return hasattr(x, "std_dev")


def to_numpy(x, xerr=None):
	"""
	Convert unumpy->numpy and ufloat->float. If already numpy, return as is.
	Args:
		x ():           unumpy or ufloat. In this case, don't need to provide xerr as it is already contained in x
		xerr ():        Needed only in case x is numpy instead of unumpy

	Returns:

	"""

	def unumpy_to_numpy(arr):
		val = unumpy.nominal_values(arr)
		dev = unumpy.std_devs(arr)
		if not np.any(dev):
			dev = None
		return val, dev

	def ufloat_to_float(x):
		val = uncertainties.nominal_value(x)
		dev = uncertainties.std_dev(x)
		if dev == 0:
			dev = None
		return val, dev

	if is_unumpy(x):
		x, xerr = unumpy_to_numpy(x)

	elif is_ufloat(x):
		x, xerr = ufloat_to_float(x)

	return x, xerr


def from_numpy(x, xerr=0):
	if type(x) is float:
		return ufloat(x, xerr)
	else:
		return unumpy.uarray(x, xerr)


def val(x, xerr=None):
	return to_numpy(x, xerr)[0]


def dev(x, xerr=None):
	return to_numpy(x, xerr)[1]


def make_independent(x, xerr=None):
	x, xerr = to_numpy(x, xerr)

	return unumpy.uarray(x, xerr)
