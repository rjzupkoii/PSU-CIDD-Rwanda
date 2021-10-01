% rainfall.m
%
% Use ERA5 mean daily rainfall to generate adjustments to the model beta parameter.
warning('off', 'MATLAB:MKDIR:DirectoryExists');

% Load the data, drop the Google Earth Engine column
raw = readmatrix('data/rwa-rainfall.csv');
raw = raw(:, 1:2);

% Shift the data to account for the Anopheles gambiae life cycle of about 10 - 11 days
daily = circshift(raw(:, 2), 10);

% Smooth the and normalize the data
daily = smoothdata(daily);
daily = (daily - min(daily)) / (max(daily) - min(daily));

% Plot the ERA5 rainfall data
subplot(2, 1, 1);
plot(raw(:, 1) + 1, raw(:, 2));
format('Mean Rainfall, 10 Year Mean');

% Plot the beta adjustments
subplot(2, 1, 2);
plot(raw(:, 1) + 1, daily);
xlim([1 365]);
format('Daily Beta Adjustment');

% Write the data to disk
mkdir('out');
writematrix(daily, 'out/rwa-adjustment.csv');

function [] = format(label) 
    xlim([1 365]);
    xlabel('Day of Year');
    ylabel(label);
    graphic = gca;
    graphic.FontSize = 18;
end