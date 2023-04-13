#!/usr/bin/env python3

# rwa_plot_heatmap.py
#
# Plot genotype frequency heatmaps.
import matplotlib.pyplot as plt
import os
import pandas as pd
import seaborn as sns


STUDIES = {
    'rwa-pfpr-constant'        : 'AL (3-day course)', 
    'rwa-ae-al-5'              : 'AL (5-day course)',
    'rwa-replacement-dhappq'   : 'DHA-PPQ',
    'rwa-mft-asaq-dhappq-0.25' : 'ASAQ (75%) + DHA-PPQ (25%)',
    'rwa-tact-alaq'            : 'ALAQ',
    'rwa-seq-al-asaq'          : 'AL, then ASAQ345',
    'rwa-rotation-al-5'        : 'DHA-PPQ three years, then AL (5-day course, 50%) + ASAQ (50%)',
    'rwa-mft-al-dhappq-0.25'   : 'AL (75%) + DHA-PPQ (25%)',
}


def make_plot(filename, output, threshold = 1e-3):
        
    # Load the data
    data = pd.read_csv(filename)

    # Prepare the years
    start_year = min(data['year'])
    days = data["dayselapsed"].unique()
    days.sort()
    years = [round(start_year + i / 12) if i % 12 == 0 else '' for i, x in enumerate(days)]
    
    # Update the frequency based upon our threshold, prepare to plot
    data.loc[data['frequency'] < threshold, 'frequency'] = None
    data = data.pivot("name", "dayselapsed", "frequency")
    data = data.dropna(how='all')
    
    # Set up the matplotlib figure
    sns.set_theme()
    fig, ax = plt.subplots(figsize=(11, 8))

    # Generate a custom diverging colormap
    cmap = sns.color_palette("coolwarm", as_cmap=True)

    # Draw the heatmap with the mask and correct aspect ratio
    plot = sns.heatmap(data, xticklabels=years, cmap=cmap, center=0.1, vmin=threshold, vmax=1.0)
    plot.set_facecolor('white')
    
    title = filename.split('/')[4].replace('.csv', '').split('_')
    key = title[0]
    plt.title('{} [{} - {}], frequency > {}'.format(STUDIES[key], title[1], title[2], threshold))
    plt.ylabel('Genotype')
    plt.xlabel('')
    plt.xticks(rotation=90)
    
    # Save the figure
    figure = plot.get_figure()    
    figure.savefig(os.path.join('out', output), dpi=300)
    print('Saved {}...'.format(os.path.join('out', output)))
    plt.close()
   

def main(directory):
    for file in os.listdir(directory):
        if not file.endswith('csv'): continue
        make_plot(os.path.join(directory, file), file.replace('.csv', '.png'))


if __name__ == '__main__':
    main('../Analysis/data/heatmaps')