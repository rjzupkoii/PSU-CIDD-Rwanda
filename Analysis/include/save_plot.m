function [] = save_plot(filename)
    % Set the position, save and close the plot
    set(gcf, 'Position',  [0, 0, 2560, 1440]);
    print('-dpng', '-r150', filename);
    clf;
    close;
end