function [column, divisor, label] = parse_type(type)
    % Parse out the type of intervention we are looking at
    if strcmp(type, 'infections')
        column = 5;
        divisor = 12;
        label = 'Monthly Count of {\it P. falciparum} Infected Indivdiuals';
    elseif strcmp(type, 'clinical')
        column = 6;
        divisor = 1;
        label = 'Monthly Count of {\it P. falciparum} Clinical Cases';
    elseif strcmp(type, 'occurrences')
        column = 7;
        divisor = 12;
        label = 'Monthly Count of 561H Clones';
    elseif strcmp(type, 'weighted')
        column = 9;
        divisor = 12;
        label = 'Indivdiual Weighted Count of 561H Clones';
    elseif strcmp(type, 'treatmentfailure')
        column = 10;
        divisor = 1;
        label = 'Treatment Failures';
    elseif strcmp(type, '561H')
        column = -1;
        divisor = 1;
        label = 'Monthly 561H Frequency';
    else
        error('Unknown data type: %s', type);
    end
end

