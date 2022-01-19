function [] = format_plot(type, plot_title, yaxis_label)
    % Format a single plot with the title and yaxis label provided
    title(plot_title);
    xlabel({'Model Year' '\fontsize{10} (date indicates end of year)'});
    ylabel(yaxis_label);

    % Format the x axis
    dates = datenum('2019-12-31'):datenum('2032-01-01');
    xlim([min(dates) max(dates)]);
    xticks(dates(1 : 365 : end));
    xticklabels(datestr(datetime(xticks, 'ConvertFrom', 'datenum'), 'yyyy'));

    % If this is not a 561H plot then relabel the y-axis
    if ~strcmp(type, '561H')
        format_yticks();
    end

    graphic = gca;
    graphic.FontSize = 18;
end