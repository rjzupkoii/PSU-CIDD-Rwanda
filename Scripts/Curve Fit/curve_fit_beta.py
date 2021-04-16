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
import warnings

# Import our libraries
sys.path.append("../Calibration/include")
from ascFile import load_asc, write_asc
from calibrationLib import get_bin
from utility import progressBar

cache = {}

# RWA constants
ZONE = 0
POPULATION_BINS = [4973, 10818, 16518, 24639, 38186, 65194, 95262, 211246, 286928]


def beta_exp2fit(filename, population, treatment, pfpr):
    # Check the cache, fit the curve if we don't already have the coefficients
    key = "{}:{}".format(population, treatment)
    if key not in cache:
        logging.debug("Fitting population {}, treatment {} (PfPR: {})".format(population, treatment, pfpr))

        # Starting point for the fitting, these were arbitrarily selected
        p0 = (0.5, 0.5, 0.5, 0.5)

        # Load the data press on with an error if the values aren't present
        x, y = load(filename, population, treatment)
        if len(x) == 0 or len(y) == 0:
            sys.stderr.write("\nMissing or incomplete data, skipping population {} and treatment of {}\n".format(population, treatment))
            return None

        coefficients, _ = scipy.optimize.curve_fit(exp2, x, y, p0, maxfev=10000)
        cache[key] = coefficients
        logging.debug("coefficients: {}".format(coefficients))

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

        # Load the data press on with an error if the values aren't present
        x, y = load(filename, population, treatment)
        if len(x) == 0 or len(y) == 0:
            sys.stderr.write("\nMissing or incomplete data, skipping population {} and treatment of {}\n".format(population, treatment))
            return None

        coefficients = np.polyfit(x, y, 2)
        cache[key] = coefficients
        logging.debug("coefficients: {}".format(coefficients))

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


def main(method, filename, progress=True):
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

            # Check for errors before updating the array
            if result is None:
                sys.stderr.write("Null value returned for beta, exiting\n")
                sys.exit(1)
            if result < 0:
                sys.stderr.write("Projected beta {} is less than zero, exiting\n".format(result))
                # Only exit if the debug flag isn't set
                if progress:
                    sys.exit(1)
            beta[row].append(result)

        # Note the progress
        if progress:
            progressBar(row + 1, ascHeader['nrows'])            

    # Save the calculated beta values
    print("Saving {}".format(filename))
    write_asc(ascHeader, beta, filename)


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        print("Usage: ./curve_fit_beta.py [function]")
        print("function - exp2 or poly2")
        exit(0)

    # Set the function to be used for fitting
    if sys.argv[1] == 'exp2':
        print("Fitting using exponential, f(x) = a * exp(b * x) + c * exp(d * x)")
        method = beta_exp2fit
        filename = "out/exp2_beta.asc"
    elif sys.argv[1] == 'poly2':
        print("Fitting using second-order polynomial, f(x) = a * x ** 2 + b * x + c")
        method = beta_polyfit
        filename = "out/poly2_beta.asc"
    else:
        print("Unknown function: {}".format(sys.argv[1]))
        exit(1)

    # Create the output directory if need be
    if not os.path.isdir('out'):
        os.mkdir('out')

    # Enable / disable debug operations
    if len(sys.argv) == 3 and sys.argv[2] == 'debug':
        logging.basicConfig(level=logging.DEBUG)
        main(method, filename, False)
    else:
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        main(method, filename)
