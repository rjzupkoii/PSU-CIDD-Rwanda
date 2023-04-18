% rwa_561h_splike.m
%
% Generate a three panel spagetti plot that compares the projected
% trajectory of the 561H frequency for at the national level; Gasabo and
% Kayoza districts.
clear;

startdate = '2003-01-01';

% Load the data
data = readmatrix('ms_data/2024/datasets/rwa-pfpr-constant.csv');

% Plot the district data for Gasabo
subplot(2, 2, 1);
plot_district(data, startdate, 8, 'Gasabo');
    scatter(datenum('2014-09-30'), 0.12, 25, 'black', 'filled');
    text(datenum('2014-09-30') + 75, 0.125, '\leftarrow 0.12', 'FontWeight', 'bold');
    scatter(datenum('2015-09-30'), 0.06, 25, 'black', 'filled');
    text(datenum('2015-09-30') + 75, 0.065, '\leftarrow 0.06', 'FontWeight', 'bold');
    scatter(datenum('2018-09-30'), 0.20, 25, 'black', 'filled');
    text(datenum('2018-09-30') - 575, 0.205, '0.20 \rightarrow', 'FontWeight', 'bold');
    scatter(datenum('2019-09-30'), 0.22, 25, 'black', 'filled');
    text(datenum('2019-09-30') + 75, 0.225, '\leftarrow 0.22', 'FontWeight', 'bold');

% Plot the district data for Kayonza
subplot(2, 2, 2);
plot_district(data, startdate, 3, 'Kayonza');
    scatter(datenum('2018-09-30'), 0.10, 25, 'black', 'filled');
    text(datenum('2018-09-30') + 75, 0.105, '\leftarrow 0.10', 'FontWeight', 'bold');

% Plot the district data for Kirehe
subplot(2, 2, 3);
plot_district(data, startdate, 4, 'Kirehe');
    scatter(datenum('2015-09-30'), 0.06, 25, 'black', 'filled');
    text(datenum('2015-09-30') + 75, 0.065, '\leftarrow 0.06', 'FontWeight', 'bold');

% Plot the district data for Ngoma
subplot(2, 2, 4);
plot_district(data, startdate, 5, 'Ngoma');
    scatter(datenum('2015-09-30'), 0.02, 25, 'black', 'filled');
    text(datenum('2015-09-30') + 75, 0.025, '\leftarrow 0.02', 'FontWeight', 'bold');

% Format all of the plots
format();

% Print the count
size(unique(data(:, 2)))

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

function [] = plot_national(data, startdate)
    hold on;

    % Calcluate the national frequency for each month
    months = unique(data(:, 3));
    for replicate = transpose(unique(data(:, 2)))
        frequency = zeros(size(months, 1), 1);
        filtered = data(data(:, 2) == replicate, :);
        for ndx = 1:size(months, 1)
            frequency(ndx) = sum(filtered(filtered(:, 3) == months(ndx), 9)) / sum(filtered(filtered(:, 3) == months(ndx), 5));
        end
        plot(months + datenum(startdate), frequency);
    end
    
    title('National');
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
        if ndx >= 3
            xlabel('Model Year');
        end
        graphic = gca;
        graphic.FontSize = 16;
    end
end
