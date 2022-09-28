#!/bin/bash

# Basic organization script to copy and rename the files produced by 
# rwa_plot_genotype.py for the rwa_figure2.m script.

cp np/rwa-pfpr-constant-parsed.csv data/rwa-AL3-parsed.csv
cp np/rwa-ae-al-5-parsed.csv data/rwa-AL5-parsed.csv
cp np/rwa-replacement-dhappq-parsed.csv data/rwa-DHAPPQ-parsed.csv
cp np/rwa-mft-asaq-dhappq-0.25-parsed.csv data/rwa-MFT-parsed.csv
cp np/rwa-rotation-al-5-parsed.csv data/rwa-ROTATION-parsed.csv
cp np/rwa-tact-alaq-parsed.csv data/rwa-ALAQ-parsed.csv