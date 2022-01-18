function [] = format_plot(type, plot_title, yaxis_label)
    % Format a single plot with the title and yaxis label provided
    title(plot_title);
    xlabel('Model Year');
    ylabel(yaxis_label);
    datetick('x', 'yyyy');

    % If this is not a 561H plot then relabel the y-axis
    if ~strcmp(type, '561H')
        labels = split(num2str(yticks, '10^{%.1f};'), ';');
        labels(cellfun('isempty', labels)) = [];
        yticklabels(labels);
    end

    graphic = gca;
    graphic.FontSize = 18;
end