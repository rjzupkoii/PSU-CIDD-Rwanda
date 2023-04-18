% rwa_rainfall.m
%
% Use ERA5 mean daily rainfall to generate adjustments to the model beta parameter.
%
% Bounding of 0.4 to 1.0 is based on USAID Global Health Supply Chain program figures
% https://www.ghsupplychain.org/news/data-driven-redistribution-ensures-availability-malaria-supplies-rwanda
warning('off', 'MATLAB:MKDIR:DirectoryExists');

% Set the floor for the beta, this is based on the 2.5x difference in cases
minima = 0.4;

% Load the data, drop the Google Earth Engine column
raw = readmatrix('../GIS/rwa_rainfall.csv');
raw = raw(:, 1:2);

% Shift the data to account for the Anopheles gambiae life cycle of about 10 - 11 days
daily = circshift(raw(:, 2), 10);

% Smooth the and normalize the data
daily = smoothdata(daily);
daily = (1 - minima) * (daily - min(daily)) / (max(daily) - min(daily)) + minima;

% Plot the ERA5 rainfall data
subplot(2, 1, 1);
plot(raw(:, 1) + 1, raw(:, 2));
format('Rainfall, 10 Year Mean (cm)');

% Plot the beta adjustments
subplot(2, 1, 2);
plot(raw(:, 1) + 1, daily);
yline(0.4, ':');
xlim([1 365]);
ylim([0 1]);
format('Relative Transmission Level');

% Write the data to disk
mkdir('out');
writematrix(daily, 'out/rwa_adjustment.csv');

function [] = format(label) 
    TICKS = [31 59 90 120 151 181 212 243 273 304 334 365];

    xlim([1 365]);
    xticks(TICKS);
    xlabel('Day of Year');
    ylabel(label);
    graphic = gca;
    graphic.FontSize = 18;
end