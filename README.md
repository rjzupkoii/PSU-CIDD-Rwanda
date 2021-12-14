# PSU-CIDD-Rwanda

This repository contains configuration, GIS, analysis files used for modeling the prevalence of malaria (*P. falciparum*) in Rwanda. These configurations are primarily intended to study 1) the development of antimalarial resistance in the parasite, and 2) possible interventions that the National Malaria Control Programme can implement.

The origin repository for the simulation can be found at [maciekboni/PSU-CIDD-Malaria-Simulation](https://github.com/maciekboni/PSU-CIDD-Malaria-Simulation), although the studies in this repository are intended to be run against 4.0.0 and 4.0.x versions that can be found under [rjzupkoii/PSU-CIDD-Malaria-Simulation](https://github.com/rjzupkoii/PSU-CIDD-Malaria-Simulation).

### Dependencies 

The following dependencies need to be installed for all of the scripts included in this repository to run:

- numpy : https://pypi.org/project/numpy/
- scipy : https://pypi.org/project/scipy/

## Organization

GIS     - GIS files for Rwanda, as prepared for the simulation. Note that two versions of the *Pf*PR<sub>2-10</sub> files are included. One based upon the original version of the Malaria Atlas project projections (`rwa_pfpr2to10_v2017.asc`) and one based upon the updated 2020 version (`rwa_pfpr_v2020.asc`). The `rwa_pfpr2to10.asc` is the canonical file for generating the beta values.

Scripts - Scripts used for model calibration and analysis.

Studies - Configuration files used for model validation and *de novo* mutation simulations.

## Model Execution

All simulations were performed on the Pennsylvania State University’s Institute for Computational and Data Sciences’ Roar supercomputer using the configurations present in [Studies](Studies/).
