function [column, label] = parse_type(type)
    % Parse out the type of intervention we are looking at
    if strcmp(type, 'infections')
        column = 5;
        label = 'Monthly Count of {\it P. falciparum} infected indivdiuals';
    elseif strcmp(type, 'occurrences')
        column = 7;
        label = 'Monthly Count of 561H Clones';
    elseif strcmp(type, 'weighted')
        column = 9;
        label = 'Indivdiual Weighted Count of 561H Clones';
    elseif strcmp(type, 'treatmentfailure')
        column = 10;
        label = 'Treatment Failures, log_{10}';
    elseif strcmp(type, '561H')
        column = -1;
        label = 'Monthly 561H Frequency';
    else
        error('Unknown data type: %s', type);
    end
end

