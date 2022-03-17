function [result] = format_title(data, type, intervention)
    % Cast the data and prepare the plot title as dictated by the type
    [~, divisor, ~] = parse_type(type);
    if strcmp(type, '561H')
        % IQR over the mean last year 561H frequency, per replicate
        iqr = prctile(mean(data(:, end - 11:end), 2), [25 50 75]);
        result = sprintf("%s: %.3f (IQR %.3f - %.3f)", intervention, iqr(2), iqr(1), iqr(3));
    else
        postfix = 'total';
        if divisor == 12
            postfix = 'per month';
        end

        % Median over the total data points of the last year, per replicate
        value = quantile(sum(data(:, end - 11:end), 2) / divisor, 0.5);
        if log10(value) >= 6
            result = sprintf("%s: %.2fM %s", intervention, value / 10^6, postfix);
        else
            result = sprintf("%s: %.1fK %s", intervention, value / 10^3, postfix);
        end
    end
end

