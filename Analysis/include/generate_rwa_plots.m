function [] = generate_rwa_plots(type, startDate, adjustment, studies)
    % Generate all of the 561H frequency plots for Rwanda, and summary plot.
    
    % Generate the single plots and store the values returned in cell arrays
    fprintf('Generating %s plots...\n', type);
    results = {};
    dataset = {};
    for ndx = 1:size(studies, 1)
        [results{end + 1}, dataset{end + 1}] = rwa_data_plot(type, adjustment, studies{ndx, 2}, studies{ndx, 3}, startDate, studies{ndx, 4}, studies{ndx, 5});
    end
    
    % Write the summary results to the out file
    writecell(transpose(results), sprintf('out/rwa-%s.txt', type), 'Delimiter', 'space');
    
    % Load the dates, these should all be the same throughout the data sets
    raw = readmatrix(studies{1, 2});
    dates = unique(raw(:, 3)) + datenum(startDate);
    dates = dates(end - 119:end);
    
    % Hide the plot during generation
    fig = figure;
    set(fig, 'Visible', 'off');

    % Generate the summary plot with the data sets
    ylimit = [9999 0];
    for ndx = 1:size(studies, 1)
        % Find the 75th percentile and the y-limit
        data = dataset{ndx}(:, end - 119:end);
        values = quantile(data, 0.75);
        ylimit(1) = min(ylimit(1), min(values));
        ylimit(2) = max(ylimit(2), max(values));
    
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
        ylim(ylimit);
        xticks(dates(12:12:end));
        datetick('x', 'yyyy', 'keepticks', 'keeplimits');

        % If this is not a 561H plot then relabel the y-axis
        if ~strcmp(type, '561H')
            labels = split(num2str(yticks, '10^{%.1f};'), ';');
            labels(cellfun('isempty', labels)) = [];
            yticklabels(labels);
        end        
    end

    % Format the common elements
    [~, label] = parse_type(type);
    handle = axes(fig, 'visible', 'off'); 
    handle.XLabel.Visible='on';
    handle.YLabel.Visible='on';
    ylabel(handle, label);
    xlabel(handle, 'Model Year');
    graphic = gca;
    graphic.FontSize = 18;
    
    % Save and close the plot
    save_plot(sprintf('plots/summary/rwa-%s-summary.png', type));
end