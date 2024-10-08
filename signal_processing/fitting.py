import numpy as np
import scipy.stats
import scipy.optimize
import scipy.odr as odr
from sklearn.metrics import r2_score
from ..uncertainties_math import to_numpy, ufloat
from .. import graphics

linear_regression = scipy.stats.linregress


def linear_fit(x, y, xerr=None, yerr=None, beta0=None, **kwargs):
	"""
	Linear regression

	Parameters
	----------
	x, y :              array_like
		Data
	xerr, yerr :        array_like, optional
		Deviations in 'x','y'. 'x','y' may also be sent as 'uncertainties' arrays, then 'xerr','yerr' are disregarded
	beta0 :             array_like, optional
		Initial parameter values, sent as a 2-tuple '(a, b)', where 'a' is the slope and 'b' is the intercept
	kwargs :            sent to odr.ODR

	Returns
	-------

	"""
	x, xerr = to_numpy(x, xerr)
	y, yerr = to_numpy(y, yerr)

	xerr[xerr == 0] = np.nan
	yerr[yerr == 0] = np.nan

	def f(B, x):
		return B[0] * x + B[1]

	linear_model = odr.Model(f)
	data = odr.RealData(x, y, xerr, yerr)

	out = odr.ODR(data, linear_model, beta0, **kwargs).run()

	# Calculate params
	y_pred = f(out.beta, x)

	slope = ufloat(out.beta[0], out.sd_beta[0])
	intercept = ufloat(out.beta[1], out.sd_beta[1])

	r_squared = r2_score(y, y_pred)

	return {"h":     out,
		"y_pred":    y_pred,
		"slope":     slope,
		"inetrcept": intercept,
		"r_squared": r_squared}


def curve_fit(fit_fcn, x, y, p0=None, x_err=None, y_err=None, plot=False, plot_kwargs=None, **kwargs):
	"""
	Use non-linear least squares to fit a function, f, to data.
	Assumes ``y = f(x, *params) + eps``.

	Parameters
	----------
	fit_fcn : callable
		The model function, f(x, ...). It must take the independent
		variable as the first argument and the parameters to fit as
		separate remaining arguments
	x : array_like
		The independent variable where the data is measured.
		Should usually be an M-length sequence or an (k,M)-shaped array for
		functions with k predictors, but can actually be any object
	y : array_like
		The dependent data, a length M array - nominally ``f(xdata, ...)``
	p0 : array_like, optional
		Initial guess for the parameters (length N). If None, then the
		initial values will all be 1 (if the number of parameters for the
		function can be determined using introspection, otherwise a
		ValueError is raised).
	x_err : array_like, optional
		Determines the uncertainty in `xdata`
	y_err : None or M-length sequence or MxM array, optional
		Determines the uncertainty in `ydata`. If we define residuals as
		``r = ydata - f(xdata, *popt)``, then the interpretation of `sigma`
		depends on its number of dimensions:
			- A 1-D `sigma` should contain values of standard deviations of
			  errors in `ydata`. In this case, the optimized function is
			  ``chisq = sum((r / sigma) ** 2)``.
			- A 2-D `sigma` should contain the covariance matrix of
			  errors in `ydata`. In this case, the optimized function is
			  ``chisq = r.T @ inv(sigma) @ r``.
			- None (default) is equivalent of 1-D `sigma` filled with ones
	plot :  boolean
		Set to 'True' if you want to plot the data
	plot_kwargs :
	kwargs :    sent to 'scipy.optimize.curve_fit()'

	Returns
	-------

	"""
	if plot_kwargs is None:
		plot_kwargs = {}

	x_err = np.asarray(x_err)
	if x_err.size == 1:
		x_err = np.repeat(x_err, len(x))
	y_err = np.asarray(y_err)
	if y_err.size == 1:
		y_err = np.repeat(y_err, len(y))

	# Curve-Fit
	(p_opt, p_cov) = scipy.optimize.curve_fit(fit_fcn, x, y, p0=p0, sigma=y_err, **kwargs)

	out = [p_opt, p_cov]

	if plot:
		out_plot = graphics.AxesLiron().plot_data_and_curve_fit(x, y, fit_fcn,
				xerr=x_err, yerr=y_err,
				p_opt=p_opt, p_cov=p_cov,
				**plot_kwargs)  # TODO fix
		out = [out, out_plot]

	return out
