% rwa_spike_calibration.m
% 
% Generate a six panel plot with the national and regional spike
% calibration results.
addpath('include');
clear;

STARTDATE = '2003-01-01';
CONFIGURATION = {
    8, 'Gasabo';        % 2014, 2015, 2018, 2019
    3, 'Kayonza';       % 2015, 2018
    9, 'Kicukiro';      % 2019
    10, 'Nyarugenge';   % 2019
    17, 'Hyue';         % 2019
};

% Create the output directory
warning('off', 'MATLAB:MKDIR:DirectoryExists');
mkdir('plots/spikes');

% Iterate over all of the spike calibration files and generate the plots
files = dir('data/spikes');
for ndx = 1:length(files)
    if files(ndx).isdir, continue; end
    if strcmp(files(ndx).name(1), '.'), continue; end    
    filename = fullfile(files(ndx).folder, files(ndx).name);
    output = sprintf('plots/spikes/%s', strrep(files(ndx).name, 'csv', 'png'));
    report(filename, output, STARTDATE, CONFIGURATION);
end


function [] = report(filename, output, startdate, configuration)
    % Read the data
    data = readmatrix(filename);
    
    % Hide the plot during generation
    fig = figure;
    set(fig, 'Visible', 'off');

    % Plot the national data
    subplot(2, 3, 1);
    plot_national(data, startdate);
    
    for ndx = 1:size(configuration)
        subplot(2, 3, ndx + 1);
        plot_district(data, startdate, configuration{ndx, 1}, configuration{ndx, 2});
    
        switch configuration{ndx, 1}
            % Gasabo
            case 8
                xline(4290 + datenum(startdate), ':', '0.12069');
                xline(4650 + datenum(startdate), ':', '0.0603');
                xline(5730 + datenum(startdate), ':', '0.19608');
                xline(6090 + datenum(startdate), ':', '0.21918');
    
            % Kayonza
            case 3
                xline(4650 + datenum(startdate), ':', '0.00746');
                xline(5730 + datenum(startdate), ':', '0.09756');
    
            % Kicukiro
            case 9
                xline(6090 + datenum(startdate), ':', '0.21918');
    
            % Nyarugenge
            case 10
                xline(6090 + datenum(startdate), ':', '0.21918');            
    
            % Hyue
            case 17
                xline(6090 + datenum(startdate), ':', '0.12121');            
        end
    end 
    
    % Format and save the plot
    format();
    save_plot(output);
end

function [] = plot_district(data, startdate, district, name)
    filtered = data(data(:, 4) == district, :);
    plot(unique(filtered(:, 3)) + datenum(startdate), filtered(:, 9) ./ filtered(:, 5));
    title(name);
end

function [] = plot_national(data, startdate)
    hold on;

    % Calcluate the national frequency for each month
    months = unique(data(:, 3));
    frequency = zeros(size(months, 1), 1);
    for ndx = 1:size(months, 1)
        frequency(ndx) = sum(data(data(:, 3) == months(ndx), 9)) / sum(data(data(:, 3) == months(ndx), 5));
    end
    plot(months + datenum(startdate), frequency);
    
    title('National');
end

function [] = format()
    % Find the y-axis limits
    ylimit = [9999 0];
    for ndx = 1:6
        subplot(2, 3, ndx);
        values = ylim();
        ylimit(1) = min(values(1), ylimit(1));
        ylimit(2) = max(values(2), ylimit(2));
    end
    xlimit = xlim();

    % Apply the formatting
    for ndx = 1:6
        subplot(2, 3, ndx);
        datetick('x', 'yyyy');
        ylim(ylimit);
        xlim(xlimit);

        if mod(ndx, 3) == 1
            ylabel('561H Frequency');
        end
        if ndx >= 4
            xlabel('Model Year');
        end
    end
end