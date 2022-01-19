function [] = format_yticks()
% Format the yticks from log10 to base10, abbreviated to thousands (K)

    ticks = yticks;
    labels = split(num2str(roundn(10 .^ ticks, min(floor(ticks))) / 1000, '%.1fK;'), ';');
    labels(cellfun('isempty', labels)) = [];
    labels = strtrim(labels);
    yticklabels(labels);
end
