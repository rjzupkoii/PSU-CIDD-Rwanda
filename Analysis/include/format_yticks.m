function [] = format_yticks()
% Format the yticks from log10 to base10, abbreviated to thousands (K)

    ticks = yticks;
    if max(floor(ticks)) >= 6
        labels = split(num2str(roundn(10 .^ ticks, min(floor(ticks))) / 10^6, '%.2fM;'), ';');
    else
        labels = split(num2str(roundn(10 .^ ticks, min(floor(ticks))) / 10^3, '%.1fK;'), ';');
    end
    labels(cellfun('isempty', labels)) = [];
    labels = strtrim(labels);
    yticklabels(labels);
end
