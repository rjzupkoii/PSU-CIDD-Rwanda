function [] = rwa_frequency_plots(startDate, studies)
    % Generate all of the 561H frequency plots for Rwanda, and summary plot.
    
    % Generate the single plots and store the values returned in cell arrays
    disp('Generating 561H frequency plots...')
    results = {};
    frequencies = {};
    for ndx = 1:size(studies, 1)
        [results{end + 1}, frequencies{end + 1}] = rwa_intervention_plot(studies{ndx, 2}, studies{ndx, 3}, startDate, studies{ndx, 4}, studies{ndx, 5});
    end
    
    % Write the summary results to the out file
    writecell(transpose(results), 'out/rwa-iqrs.txt', 'Delimiter', 'space');
    
    % Load the dates, these should all be the same throughout the data sets
    raw = readmatrix(studies{1, 2});
    dates = unique(raw(:, 3)) + datenum(startDate);
    dates = dates(end - 119:end);
    
    % Generate the summary plot with the data sets
    ylimit = 0;
    for ndx = 1:size(studies, 1)
        % Find the 75th percentile and the y-limit
        data = frequencies{ndx}(:, end - 119:end);
        values = quantile(data, 0.75);
        ylimit = max(ylimit, max(values));
    
        % Add the subplot
        subplot(6, 4, studies{ndx, 1});
        hold on;
        title(results{ndx});
        plot(dates, values, 'LineStyle', ':', 'color', [99 99 99] / 256.0);
        plot(dates, median(data), 'black');
        plot(dates, quantile(data, 0.25), 'LineStyle', ':', 'color', [99 99 99] / 256.0);
    end
    
    % Wrap up the formatting of the subplots
    for ndx = 1:size(studies, 1)
        subplot(6, 4, studies{ndx, 1});
        axis tight;
        ylim([0 ylimit]);
        xticks(dates(12:12:end));
        datetick('x', 'yyyy', 'keepticks', 'keeplimits');
    end
    
    % Save and close the plot
    save_plot('plots/summary/rwa-561h-summary.png');
end