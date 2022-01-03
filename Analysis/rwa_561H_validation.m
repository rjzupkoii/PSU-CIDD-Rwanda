% rwa_561h_splike.m
%
% Generate a nine panel plot that compares the status quo versus a 1% and
% 2% decline in the cell PfPR for Rwanda.
clear;

startdate = '2003-01-01';
gasabo = 8;         % District ID for Gasabo
kayonza = 3;        % District ID for Kayonza

% Load the data
data = readmatrix('data/rwa-validation-561h.csv');

% Plot the national data
subplot(3, 1, 1);
plot_national(data, startdate);

% Plot the district data for Gasabo
subplot(3, 1, 2);
plot_district(data, startdate, gasabo, 'Gasabo');

% Plot the district data for Kayonza
subplot(3, 1, 3);
plot_district(data, startdate, kayonza, 'Kayonza');    

format();

function [] = plot_district(data, startdate, district, name)
    hold on;

    filtered = data(data(:, 4) == district, :);
    for replicate = transpose(unique(filtered(:, 2)))
        plot(unique(filtered(filtered(:, 2) == replicate, 3)) + datenum(startdate), ...
            filtered(filtered(:, 2) == replicate, 8) ./ filtered(filtered(:, 2) == replicate, 5));
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
            frequency(ndx) = sum(filtered(filtered(:, 3) == months(ndx), 8)) / sum(filtered(filtered(:, 3) == months(ndx), 5));
        end
        plot(months + datenum(startdate), frequency);
    end
    
    title('National');
end

function [] = format()
    % Find the y-axis limits
    ylimit = [9999 0];
    for ndx = 1:3
        subplot(3, 1, ndx);
        values = ylim();
        ylimit(1) = min(values(1), ylimit(1));
        ylimit(2) = max(values(2), ylimit(2));
    end
    xlimit = xlim();

    % Apply the formatting
    for ndx = 1:3
        subplot(3, 1, ndx);
        datetick('x', 'yyyy');
        ylim(ylimit);
        xlim(xlimit);
        ylabel('561H Frequency');
        if ndx == 3
            xlabel('Model Year');
        end
    end
end
