function [column, divisor, label] = parse_type(type)
    settings = {
        % Type, Index, Divisor, Label
        'infections', 5, 12, 'Monthly Count of {\it P. falciparum} Infected Indivdiuals';
        'clinical', 6, 1, 'Monthly Count of {\it P. falciparum} Clinical Cases';
        'occurrences', 7, 12, 'Monthly Count of 561H Clones';
        'weighted', 9, 12, 'Indivdiual Weighted Count of 561H Clones';
        'treatmentfailure', 10, 1, 'Treatment Failures';
        'genotypecarriers', 11, 12, '561H Genotype Carriers';
        '561H', -1, 1, 'Monthly 561H Frequency'
    };

    % Find the match for the type
    for row = 1:size(settings, 1)
        if strcmp(type, settings{row, 1})
            column = settings{row, 2};
            divisor = settings{row, 3};
            label = settings{row, 4};
            return;
        end
    end

    % Or fail out of the function
    error('Unknown data type: %s', type);
end

