#!/bin/bash

# Basic organization script to copy and rename the files produced by 
# rwa_plot_genotype.py for the rwa_figure2.m script.

mkdir -p data
cp np/2024_rwa-pfpr-constant-parsed.csv data/rwa-AL3-parsed.csv
cp np/2024_rwa-ae-al-5-parsed.csv data/rwa-AL5-parsed.csv
cp np/2024_rwa-replacement-asaq-parsed.csv data/rwa-ASAQ-parsed.csv
cp np/2024_rwa-replacement-dhappq-parsed.csv data/rwa-DHAPPQ-parsed.csv
cp np/2024_rwa-mft-asaq-dhappq-0.25-parsed.csv data/rwa-MFT-parsed.csv
cp np/2024_rwa-rotation-al-5-parsed.csv data/rwa-ROTATION-parsed.csv
cp np/2024_rwa-tact-alaq-parsed.csv data/rwa-ALAQ-parsed.csv
cp np/2024_rwa-seq-al-asaq-parsed.csv data/rwa-AL-THEN-ASAQ-parsed.csv
cp np/2024_rwa-seq-al-dhappq-parsed.csv data/rwa-AL-THEN-DHAPPQ-345-parsed.csv
cp np/2024_rwa-seq-al-dhappq-pause-parsed.csv data/rwa-AL-THEN-DHAPPQ-789-parsed.csv