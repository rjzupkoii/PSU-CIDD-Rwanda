function [] = format_plot(plot_title, yaxis_label)
    % Format a single plot with the title and yaxis label provided
    title(plot_title);
    xlabel('Model Year');
    ylabel(yaxis_label);
    datetick('x', 'yyyy');
    graphic = gca;
    graphic.FontSize = 18;
end