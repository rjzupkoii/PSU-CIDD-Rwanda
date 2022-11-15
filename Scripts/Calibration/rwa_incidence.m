

clear;

data = readmatrix('data/incidence.csv');

population = unique(data(:, 3));
access = min(unique(data(:, 4)));

hold on;
for bin = transpose(population)
    filtered = data(data(:, 3) == bin, :);
    filtered = filtered(filtered(:, 4) == access, :);

    x = filtered(:, 6);
    y = filtered(:, 8);
    scatter(x, y, 'filled');
end
hold off;

xlabel('EIR');
ylabel('Cases per 1000');

plot = findobj(gca,'Type','Patch');
legend(plot, string(population))