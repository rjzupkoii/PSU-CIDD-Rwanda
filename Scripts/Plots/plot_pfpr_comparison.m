% plot_pfpr_comparison.m
%
% Plot the refernece versus simulated PfPR data.

FILENAME = "data/27227-verification-data.csv";
REFERENCE = "data/weighted_pfpr.csv";

plotSimuatedVsReferencePfPR(FILENAME, REFERENCE);

function [] = plotSimuatedVsReferencePfPR(simulatedFile, referenceFile)
    CENTER_MIN = 0; CENTER_MAX = 25;

    % Load the reference data
    reference = csvread(referenceFile);

    % Load and trim the evaluation data to post-burn-in
    data = csvread(simulatedFile, 1, 0);
    data = data(data(:, 1) >= (11 * 365), :);
    districts = unique(data(:, 2));

    % Prepare the color map
    colors = colormap(parula(size(districts, 1)));

    hold on;
    for district = transpose(districts)
        expected = reference(reference(:, 1) == district, 2);
        pfpr = data(data(:, 2) == district, 6); 

        % We want the seasonal maxima, filter out the local maxima, once
        % this is done we should only have six points left
        maxima = pfpr(pfpr > mean(pfpr));
        maxima = maxima(maxima > maxima - std(maxima));
        maxima = findpeaks(maxima);

        pfpr = pfpr .* -1;
        minima = pfpr(pfpr > mean(pfpr));
        minima = minima(minima > minima - std(minima));
        minima = findpeaks(minima);

        % Plot from the maxima to the minima, connected by a line
        line([expected expected], [mean(maxima) abs(mean(minima))], 'LineStyle', '--', 'LineWidth', 1.5, 'Color', 'black');
        scatter(expected, mean(maxima), 100, colors(district, :), 'filled', 'MarkerEdgeColor', 'black');
        scatter(expected, abs(mean(minima)), 75, [99 99 99] / 255, 'filled', 'MarkerEdgeColor', 'black');
    end
    hold off;

    % Set the limits
    xlim([CENTER_MIN CENTER_MAX]);
    ylim([CENTER_MIN CENTER_MAX]);
    pbaspect([1 1 1]);
    
    % Plot the reference error lines
    data = get(gca, 'YLim');
    line([data(1) data(2)], [data(1)*1.05 data(2)*1.1], 'Color', [0.5 0.5 0.5], 'LineStyle', '-.');
    % text(data(2) * 0.9, data(2) + 0.5, '+10%', 'FontSize', 16);
    line([data(1) data(2)], [data(1)*1.05 data(2)*1.05], 'Color', [0.5 0.5 0.5], 'LineStyle', '-.');
    % text(data(2)* 0.95, data(2) + 0.5, '+5%', 'FontSize', 16);
    line([data(1) data(2)], [data(1)*0.95 data(2)*0.95], 'Color', [0.5 0.5 0.5], 'LineStyle', '-.');
    text(data(2), data(2) * 0.95, '-5%', 'FontSize', 16);
    line([data(1) data(2)], [data(1)*0.95 data(2)*0.9], 'Color', [0.5 0.5 0.5], 'LineStyle', '-.');
    text(data(2), data(2) * 0.9, '-10%', 'FontSize', 16);
    
    % Plot the reference center line
    line([data(1) data(2)], [data(1) data(2)], 'Color', 'black', 'LineStyle', '-.');
    text(data(2), data(2) + 0.5, '\pm0%', 'FontSize', 16);
        
    ylabel('Simulated {\it Pf}PR_{2 to 10}, mean of peaks');
    xlabel('Reference {\it Pf}PR_{2 to 10}');

    title('Rwanda, Simuated versus Reference {\it Pf}PR_{2 to 10} values');

    graphic = gca;
    graphic.FontSize = 20;
end
