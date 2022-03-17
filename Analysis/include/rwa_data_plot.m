function [result, data] = rwa_data_plot(type, adjustment, dataFilename, intervention, startDate, interventionDate, imageFilename)
    % Generate a single data plot for an intervention.
    
    % Load the data and the unique datas
    raw = readmatrix(dataFilename);
    dates = unique(raw(:, 3));
    replicates = unique(raw(:, 2));
    
    % Parse out the national sums / frequency
    [column, ~, label] = parse_type(type);
    data = zeros(size(dates, 2), size(replicates, 2));
    for ndx = 1:size(replicates, 1)
        filtred = raw(raw(:, 2) == replicates(ndx), :);
        for ndy = 1:size(dates, 1)
            if strcmp(type, '561H')
                data(ndx, ndy) = sum(filtred(filtred(:, 3) == dates(ndy), 9)) / sum(filtred(filtred(:, 3) == dates(ndy), 5));
            else
                data(ndx, ndy) = sum(filtred(filtred(:, 3) == dates(ndy), column)) / adjustment;
            end
        end
    end
    
    % Cast the data and prepare the plot title as dictated by the type
    result = format_title(data, type, intervention);
    if ~strcmp(type, '561H')
        data = log10(data);
    end

    % Plot the data
    fig = figure;
    set(fig, 'Visible', 'off');
    hold on;
    dates = dates + datenum(startDate);
    plot(dates, quantile(data, 0.90), 'LineStyle', ':', 'color', [99 99 99] / 256.0);
    plot(dates, median(data), 'black');
    plot(dates, quantile(data, 0.05), 'LineStyle', ':', 'color', [99 99 99] / 256.0);
    if interventionDate ~= ""
        xline(datenum(interventionDate), '-', intervention);
    end
    
    % Format, save, and close the plot
    format_plot(type, result, label);
    save_plot(sprintf(imageFilename, strcat('-', type)));
end
