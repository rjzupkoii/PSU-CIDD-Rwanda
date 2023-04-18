% rwa_ext_fig_3.m
%
% Generate a four panel spagetti plot that compares the projected
% trajectory of the 561H frequency, with formatting for the manuscript.
% Note the adjustment to the text label coordinates to ensure readablity.
clear;

STARTDATE = '2003-01-01';

% Load the data
data = readmatrix('../Analysis/ms_data/2024/datasets/rwa-pfpr-constant.csv');

% Plot the district data for Gasabo
subplot(2, 2, 1);
plot_district(data, STARTDATE, 8, 'Gasabo');
    xline(datenum('2014-09-30'), ':', 'LineWidth', 1.5);    
    scatter(datenum('2014-09-30'), 0.12, 25, 'black', 'filled');
    text(datenum('2014-09-30') + 75, 0.125, '0.12', 'FontWeight', 'bold');

    xline(datenum('2015-09-30'), ':', 'LineWidth', 1.5);
    scatter(datenum('2015-09-30'), 0.06, 25, 'black', 'filled');
    text(datenum('2015-09-30') + 75, 0.065, '0.06', 'FontWeight', 'bold');

    xline(datenum('2018-09-30'), ':', 'LineWidth', 1.5);
    scatter(datenum('2018-09-30'), 0.20, 25, 'black', 'filled');
    text(datenum('2018-09-30') - 375, 0.205, '0.20', 'FontWeight', 'bold');

    xline(datenum('2019-09-30'), ':', 'LineWidth', 1.5);
    scatter(datenum('2019-09-30'), 0.22, 25, 'black', 'filled');
    text(datenum('2019-09-30') + 75, 0.225, '0.22', 'FontWeight', 'bold');

% Plot the district data for Kayonza
subplot(2, 2, 2);
plot_district(data, STARTDATE, 3, 'Kayonza');
    xline(datenum('2018-09-30'), ':', 'LineWidth', 1.5);
    scatter(datenum('2018-09-30'), 0.10, 25, 'black', 'filled');
    text(datenum('2018-09-30') + 75, 0.105, '0.10', 'FontWeight', 'bold');

% Plot the district data for Kirehe
subplot(2, 2, 3);
plot_district(data, STARTDATE, 4, 'Kirehe');
    xline(datenum('2015-09-30'), ':', 'LineWidth', 1.5);
    scatter(datenum('2015-09-30'), 0.06, 25, 'black', 'filled');
    text(datenum('2015-09-30') + 75, 0.065, '0.06', 'FontWeight', 'bold');

% Plot the district data for Ngoma
subplot(2, 2, 4);
plot_district(data, STARTDATE, 5, 'Ngoma');
    xline(datenum('2015-09-30'), ':', 'LineWidth', 1.5);
    scatter(datenum('2015-09-30'), 0.02, 25, 'black', 'filled');
    text(datenum('2015-09-30') + 75, 0.025, '0.02', 'FontWeight', 'bold');

% Format all of the plots
format();

function [] = plot_district(data, startdate, district, name)
    hold on;
    filtered = data(data(:, 4) == district, :);
    for replicate = transpose(unique(filtered(:, 2)))
        plot(unique(filtered(filtered(:, 2) == replicate, 3)) + datenum(startdate), ...
            filtered(filtered(:, 2) == replicate, 9) ./ filtered(filtered(:, 2) == replicate, 5), ...
            'Color', [0.6 0.6 0.6]);
    end
    title(name);
end

function [] = format()
    % Find the axis limits
    ylimit = [intmax 0];
    for ndx = 1:4
        subplot(2, 2, ndx);
        values = ylim();
        ylimit(1) = min(values(1), ylimit(1));
        ylimit(2) = max(values(2), ylimit(2));
    end        

    % Apply the formatting
    for ndx = 1:4
        subplot(2, 2, ndx);
        datetick('x', 'yyyy');
        ylim(ylimit);
        xlim([datenum('2014-01-01') datenum('2035-01-01')]);
        if mod(ndx, 2) ~= 0
            ylabel('561H Frequency');
        end
        graphic = gca;
        graphic.FontSize = 16;
    end
end
