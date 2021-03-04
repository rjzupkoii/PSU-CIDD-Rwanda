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

def beta_expfit(filename, population, treatment, pfpr):
    # Check the cache
    key = "{}:{}".format(population, treatment)
    if key not in cache:
        logging.debug("Fitting population {}, treatment {} (PfPR: {})".format(population, treatment, pfpr))

        # Load the data, filter by the population and treatment
        calibration = np.loadtxt(filename, delimiter=',', skiprows=1)
        calibration = calibration[calibration[:, 2] == population]
        calibration = calibration[calibration[:, 3] == treatment]

        # Extract the beta and PfPR columns
        calibrationPfpr = calibration[:, 6]     # x-data
        calibrationBeta = calibration[:, 4]     # y-data
        
        # Curve fit the function
        p0 = (0.5, 0.5, 0.5, 0.5)
        popt, _ = scipy.optimize.curve_fit(exp2, calibrationPfpr, calibrationBeta, p0, maxfev=10000)
        
        cache[key] = popt

    # Load the coefficients and return the beta
    coefficients = cache[key]
    return exp2(pfpr, coefficients[0], coefficients[1], coefficients[2], coefficients[3])


def exp2(x, a, b, c, d):
    return a * np.exp(b * x) + c * np.exp(d * x)


def beta_polyfit(filename, population, treatment, pfpr):
    # Check the cache
    key = "{}:{}".format(population, treatment)
    if key not in cache:
        print("Fitting population {}, treatment {}".format(population, treatment))

        # Load the data, filter by the population and treatment
        calibration = np.loadtxt(filename, delimiter=',', skiprows=1)
        calibration = calibration[calibration[:, 2] == population]
        calibration = calibration[calibration[:, 3] == treatment]

        # Extract the beta and PfPR columns
        calibrationBeta = calibration[:, 4]
        calibrationPfpr = calibration[:, 6]

        # Curve fit the function
        coefficients = np.polyfit(calibrationPfpr, calibrationBeta, 2)
        cache[key] = coefficients

    # Load the coefficients
    coefficients = cache[key]
    
    # Find the beta
    beta = coefficients[0] * pfpr ** 2 + coefficients[1] * pfpr + coefficients[2]
    return round(beta, 8)
    

def main():
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
#            result = beta_polyfit("data/calibration.csv", popBin, treatments[row][col], pfpr[row][col] * 100.0)
            target = round(pfpr[row][col] * 100.0, 8)
            result = beta_expfit("data/calibration.csv", popBin, treatments[row][col], target)
            beta[row].append(result)

    # Save the calculated beta values
    filename = "out/exp2_beta.asc"
#    filename = "out/poly2_beta.asc"
    print("Saving {}".format(filename))
    write_asc(ascHeader, beta, filename)


if __name__ == "__main__":

    # Enable logging statements if desired
    logging.basicConfig(level=logging.DEBUG)

    # Create the output directory if need be
    if not os.path.isdir('out'):
        os.mkdir('out')

    main()