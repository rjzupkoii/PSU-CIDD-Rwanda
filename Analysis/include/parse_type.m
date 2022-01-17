function [column, label] = parse_type(type)
    % Parse out the type of intervention we are looking at
    if strcmp(type, 'infections')
        column = 5;
        label = 'P. falciparum infected indivdiuals, log_{10}';
    elseif strcmp(type, 'occurrences')
        column = 7;
        label = '561H Occurrences (unweighted), log_{10}';
    elseif strcmp(type, 'weighted')
        column = 9;
        label = '561H Occurnaces (weighted), log_{10}';
    elseif strcmp(type, 'treatmentfailure')
        column = 10;
        label = 'Treatment Failures, log_{10}';
    elseif strcmp(type, '561H')
        column = -1;
        label = '561H Frequency';
    else
        error('Unknown data type: %s', type);
    end
end

