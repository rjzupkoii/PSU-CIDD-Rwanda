#!/usr/bin/python3

# curve_fit_beta.py
#
# Experimental generation of beta ASC file using curve fitting.
import logging
import os
import math
import numpy as np
import scipy.optimize
import sys

# Import our libraries
sys.path.append("../Calibration/include")
from ascFile import load_asc, write_asc
from calibrationLib import get_bin

cache = {}

# RWA constants
ZONE = 0
POPULATION_BINS = [2125, 5640, 8989, 12108, 15577, 20289, 27629, 49378, 95262, 286928]


def beta_exp2fit(filename, population, treatment, pfpr):
    # Check the cache, fit the curve if we don't already have the coefficients
    key = "{}:{}".format(population, treatment)
    if key not in cache:
        logging.debug("Fitting population {}, treatment {} (PfPR: {})".format(population, treatment, pfpr))

        # Starting point for the fitting, these were arbitrarily selected
        p0 = (0.5, 0.5, 0.5, 0.5)

        x, y = load(filename, population, treatment)
        coefficients, _ = scipy.optimize.curve_fit(exp2, x, y, p0, maxfev=10000)
        cache[key] = coefficients

    # Load the coefficients, return the beta
    coefficients = cache[key]
    return exp2(pfpr, coefficients[0], coefficients[1], coefficients[2], coefficients[3])


def exp2(x, a, b, c, d):
    return a * np.exp(b * x) + c * np.exp(d * x)


def beta_polyfit(filename, population, treatment, pfpr):
    # Check the cache, fit the curve if we don't already have the coefficients
    key = "{}:{}".format(population, treatment)
    if key not in cache:
        logging.debug("Fitting population {}, treatment {} (PfPR: {})".format(population, treatment, pfpr))

        x, y = load(filename, population, treatment)
        coefficients = np.polyfit(x, y, 2)
        cache[key] = coefficients

    # Load the coefficients, return the beta
    coefficients = cache[key]
    return (coefficients[0] * pfpr ** 2 + coefficients[1] * pfpr + coefficients[2])
    

# Load the calibration data, returned the filtered pfpr (x-values) and beta (y-values)
def load(filename, population, treatment):
    # Load the data, filter by the population and treatment
    calibration = np.loadtxt(filename, delimiter=',', skiprows=1)
    calibration = calibration[calibration[:, 2] == population]
    calibration = calibration[calibration[:, 3] == treatment]

    # Extract the beta and PfPR columns
    calibrationPfpr = calibration[:, 6]     # x-data
    calibrationBeta = calibration[:, 4]     # y-data

    # Return the values
    return calibrationPfpr, calibrationBeta


def main(method, filename):
    # Load the relevent ASC data
    [ascHeader, pfpr] = load_asc("../../GIS/rwa_pfpr2to10.asc")
    [_, population] = load_asc("../../GIS/rwa_population.asc")
    [_, treatments] = load_asc("../../GIS/rwa_treatment.asc")

    beta = []
    for row in range(0, ascHeader['nrows']):
        beta.append([])
        for col in range(0, ascHeader['ncols']):

            # Append no data and continue
            if pfpr[row][col] == ascHeader['nodata']:
                beta[row].append(ascHeader['nodata'])
                continue

            # If PfPR is zero, then beta is zero
            if pfpr[row][col] == 0:
                beta[row].append(0)
                continue

            # Get the population bin, find the beta for the cell
            popBin = get_bin(population[row][col], POPULATION_BINS)
            target = round(pfpr[row][col] * 100.0, 8)
            result = method("data/calibration.csv", popBin, treatments[row][col], target)
            beta[row].append(result)

    # Save the calculated beta values
    print("Saving {}".format(filename))
    write_asc(ascHeader, beta, filename)


if __name__ == "__main__":

    # Enable logging statements if desired
    logging.basicConfig(level=logging.DEBUG)

    # Create the output directory if need be
    if not os.path.isdir('out'):
        os.mkdir('out')

    method = beta_exp2fit
    filename = "out/exp2_beta.asc"

    # method = beta_polyfit
    # filename = "out/poly2_beta.asc"

    main(method, filename)