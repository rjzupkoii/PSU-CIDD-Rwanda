% Generate a summary plot of the treatment interventions.
function [result, frequencies] = rwa_intervention_plot(dataFilename, intervention, startDate, interventionDate, imageFilename)
    % Load the data and the unique datas
    raw = readmatrix(dataFilename);
    dates = unique(raw(:, 3));
    replicates = unique(raw(:, 2));
    
    % Parse out the frequency for each block of dates
    frequencies = zeros(size(dates, 2), size(replicates, 2));
    for ndx = 1:size(replicates, 1)
        data = raw(raw(:, 2) == replicates(ndx), :);
        for ndy = 1:size(dates, 1)
            frequencies(ndx, ndy) = sum(data(data(:, 3) == dates(ndy), 9)) / sum(data(data(:, 3) == dates(ndy), 5));
        end
    end
    
    % Note the median and IQR of the last month
    iqr = prctile(frequencies(:, end), [25 50 70]);
    result = sprintf("%s: %.3f (IQR %.3f - %.3f)", intervention, iqr(1), iqr(2), iqr(3));
    
    % Plot the intervention data
    fig = figure;
    set(fig, 'Visible', 'off');
    hold on;
    dates = dates + datenum(startDate);
    plot(dates, quantile(frequencies, 0.75), 'LineStyle', ':', 'color', [99 99 99] / 256.0);
    plot(dates, median(frequencies), 'black');
    plot(dates, quantile(frequencies, 0.25), 'LineStyle', ':', 'color', [99 99 99] / 256.0);
    if interventionDate ~= ""
        xline(datenum(interventionDate), '-', 'AL 3-1-1 Introduction');
    end
    
    % Format the plot
    title(result);
    xlabel('Model Year');
    ylabel('561H Frequency');
    datetick('x', 'yyyy');
    graphic = gca;
    graphic.FontSize = 18;

    % Save and close the plot
    set(gcf, 'Position',  [0, 0, 2560, 1440]);
    print('-dpng', '-r150', imageFilename);
    clf;
    close;
end

