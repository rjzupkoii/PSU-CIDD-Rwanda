% rwa_figure2.m
%
% Generate the base image that is used for Figure 2 of the manuscript.
%
% Requires the files rwa-AL3-parsed.csv, rwa-AL5-parsed.csv, rwa-ALAQ-parsed.csv, 
% rwa-DHAPPQ-parsed.csv, rwa-MFT-parsed.csv, and rwa-ROTATION-parsed.csv,
% be present in the data directory. These are created by the
% rwa_plot_genotype.py script and are placed by the organize.sh script.
clear all;

% export figure as  8" by 8", fixed font size at 10, and save as SVG

all_labels_blank = true;

AL3=csvread('./March_31_2023/rwa-AL3-parsed.csv',1,0);
AL5=csvread('./March_31_2023/rwa-AL5-parsed.csv',1,0);
nr = size(AL3,1);

x1=AL3(1,1)+730+365;
x2=AL3(nr,1)-365;

day0 = 7305;
xticks = [7305:365:10955];

my_face_alpha = 0.33;
my_face_alpha2 = 0.33;

red1 = [166 54 3]/255; % this is the status quo, or AL3
red2 = [230 85 13]/255; % this is the most probably intervention, or AL5
red3 = [253 141 60]/255; % these are alternatives to AL5

blue1 = [8 81 156]/255; % this is the status quo, or AL3
blue2 = [49 130 189]/255; % this is the most probably intervention, or AL5
blue3 = [107 174 214]/255; % these are alternatives to AL5

gray1 = [37 37 37]/255; % this is the status quo, or AL3
gray2 = [99 99 99]/255; % this is the most probably intervention, or AL5
gray3 = [150 150 150]/255; % these are alternatives to AL5

stretch_r = 1.2;
stretch_u = 1.2;

% number of time points to trim at beginning and end
trm=1;

yb=0;
yt=5;
%yticks_r = [2.2 2.4 2.6 2.8 3 3.2 3.4 3.6 3.8 ];
yticks_r = 1:4;
yticks_l = 0.1:0.1:0.9;
AL3 = AL3(trm:nr-trm+1,:);
AL5 = AL5(trm:nr-trm+1,:);

lw=2;


%
% columns 
%
%   1       2      3        4       5       6           7       8
% date	tf-25	tf-50	tf-75	pfpr-25	 pfpr-50	pfpr-75	freq_561h-25	freq_561h-50	freq_561h-75



subplot(3,2,1)

fg = figure(1);
fg.Renderer='Painters'; % this ensures that the figure renders as vector;
                        % if you don't force this, Matlab will sometimes
                        % switch to raster if there are too many elements
                        % in the figure

                        % subplot(2,1,1)


% left then right
                        
yyaxis right
set(fg, 'defaultAxesColorOrder', [ blue2; 0 0 0]);

% plot prevalence
plot( AL3(:,1), AL3(:,6), '-', 'Color', gray1, 'Marker', 'none'); hold on;
                       
set(gca, 'XTick', xticks );
%set(gca, 'XTickLabel', {'0','1','2','3','4','5','6','7','8','9'});
set(gca, 'XTickLabel', {'','','','','','','','','',''});
set(gca, 'YTick', yticks_r );
set(gca, 'YTickLabel', {'','','',''} );
%set(gca, 'YTickLabel', {'0','1','2','3','4','5','6','7','8','9'});

axis([x1 x2 yb yt])

xx = transpose(AL5(:,1));
yy2 = transpose(AL5(:,7));
yy1 = transpose(AL5(:,5));
fill([xx fliplr(xx)], [yy1 fliplr(yy2)], gray2, 'FaceAlpha', my_face_alpha, 'LineStyle', 'none', 'Marker', 'none'); 

xx = transpose(AL3(:,1));
yy2 = transpose(AL3(:,7));
yy1 = transpose(AL3(:,5));
%fill([xx fliplr(xx)], [yy2 yy1], 'k','LineStyle','-', 'FaceAlpha', 1.0); 
%fill([xx fliplr(xx)], [yy2 yy1], [0.7 0.7 0.7]); 
fill([xx fliplr(xx)], [yy1 fliplr(yy2)], gray1, 'FaceAlpha', my_face_alpha, 'LineStyle', 'none', 'Marker', 'none'); 

%plot( AL3(:,1), AL3(:,6), 'Color', gray1, 'LineStyle', '-', 'Marker', 'none' );
plot( AL5(:,1), AL5(:,6), 'Color', gray2, 'LineStyle', '-', 'Marker', 'none' );

%xlabel('Year');
%ylabel('PfPR')


% %
% % NOW MOVE TO THE LEFT AXIS AND PLOT THE 561H FREQUENCY
% %

yyaxis left

plot( AL3(:,1), AL3(:,9), 'Color', blue1, 'LineWidth', 3 , 'LineStyle', '-' , 'Marker', 'none' ); hold on;

xx = transpose(AL5(:,1));
yy2 = transpose(AL5(:,10));
yy1 = transpose(AL5(:,8));
fill([xx fliplr(xx)], [yy1 fliplr(yy2)], blue2, 'FaceAlpha', my_face_alpha2, 'LineStyle', 'none', 'Marker', 'none'); 

xx = transpose(AL3(:,1));
yy2 = transpose(AL3(:,10));
yy1 = transpose(AL3(:,8));
fill([xx fliplr(xx)], [yy1 fliplr(yy2)], blue1, 'FaceAlpha', my_face_alpha2, 'LineStyle', 'none', 'Marker', 'none'); 

plot( AL5(:,1), AL5(:,9), 'Color', blue2 , 'LineWidth', lw , 'LineStyle', '-' , 'Marker', 'none' ); 
plot( AL3(:,1), AL3(:,9), 'Color', blue1 , 'LineWidth', lw , 'LineStyle', '-' , 'Marker', 'none' ); 

set(gca, 'YTick', yticks_l );
if( all_labels_blank )
    set(gca, 'YTickLabel', {''} );
else
    ylabel({'561H frequency (blue)' , 'Treatment Failure', 'Rate (red)'});
end




%%% 
%%%  PLOT THE TREATMENT FAILURE RATE
%%%

xx = transpose(AL5(:,1));
yy2 = transpose(AL5(:,4));
yy1 = transpose(AL5(:,2));
fill([xx fliplr(xx)], [yy1 fliplr(yy2)], red2, 'FaceAlpha', my_face_alpha2, 'LineStyle', 'none', 'Marker', 'none'); 

xx = transpose(AL3(:,1));
yy2 = transpose(AL3(:,4));
yy1 = transpose(AL3(:,2));
fill([xx fliplr(xx)], [yy1 fliplr(yy2)], red1, 'FaceAlpha', my_face_alpha2, 'LineStyle', 'none', 'Marker', 'none'); 

plot( AL5(:,1), AL5(:,3), 'Color', red2 , 'LineWidth', lw, 'LineStyle', '-' );
plot( AL3(:,1), AL3(:,3), 'Color', red1 , 'LineWidth', lw, 'LineStyle', '-' ); 


axis([x1 x2 0.0 1.0]);
op = get( gca, 'outerposition');
set(gca, 'outerposition', op.*[1 1 stretch_r stretch_u] ) % numbers are left bottom width height
grid on;








for spi=2:6

    odd = false;
    bottom = false;
    
    subplot(3,2,spi)
    if spi==2
        C = csvread('./March_31_2023/rwa-DHAPPQ-parsed.csv',1,0);
    end
    if spi==3
        C = csvread('./March_31_2023/rwa-MFT-parsed.csv',1,0);
        odd = true;
    end
    if spi==4
        C = csvread('./March_31_2023/rwa-ROTATION-parsed.csv',1,0);
    end
    if spi==5
        C = csvread('./March_31_2023/rwa-ALAQ-parsed.csv',1,0);
        odd = true;
        bottom = true;
    end
    if spi==6
        C = csvread('./March_31_2023/rwa-AL-THEN-DHAPPQ-789-parsed.csv',1,0);
        bottom = true;
    end
    C = C(trm:nr-trm+1,:);
       
    yyaxis right
    % plot prevalence
    plot( C(:,1), C(:,6), '-', 'Color', gray3, 'Marker', 'none'); hold on;
                
    set(gca, 'XTick', xticks );
    if( spi==5 && ~all_labels_blank )
        set(gca, 'XTickLabel', {'0','1','2','3','4','5','6','7','8','9'});
    else
        set(gca, 'XTickLabel', {'','','','','','','','','',''});
    end
    
    set(gca, 'YTick', yticks_r );
    if( spi==5 && ~all_labels_blank )        
        set(gca, 'YTickLabel', {'1%','2%','3%','4%'} );
        ylabel('PfPR')
    else
        set(gca, 'YTickLabel', {'','','',''} );
    end
    
    axis([x1 x2 yb yt])

    xx = transpose(AL5(:,1));
    yy2 = transpose(AL5(:,7));
    yy1 = transpose(AL5(:,5));
    fill([xx fliplr(xx)], [yy1 fliplr(yy2)], gray2, 'FaceAlpha', my_face_alpha, 'LineStyle', 'none', 'Marker', 'none'); 

    xx = transpose(C(:,1));
    yy2 = transpose(C(:,7));
    yy1 = transpose(C(:,5));
    fill([xx fliplr(xx)], [yy1 fliplr(yy2)], gray3, 'FaceAlpha', my_face_alpha, 'LineStyle', 'none', 'Marker', 'none'); 

    plot( C(:,1), C(:,6), 'Color', gray3, 'LineStyle', '-', 'Marker', 'none' );
    plot( AL5(:,1), AL5(:,6), 'Color', gray2, 'LineStyle', '-', 'Marker', 'none' );

    if( spi==5 && ~all_labels_blank )       
        xlabel('Year');
    end
    

    % %
    % % NOW MOVE TO THE LEFT AXIS AND PLOT THE 561H FREQUENCY
    % %

    yyaxis left
    
    xx = transpose(AL5(:,1));
    yy2 = transpose(AL5(:,10));
    yy1 = transpose(AL5(:,8));
    fill([xx fliplr(xx)], [yy1 fliplr(yy2)], blue2, 'FaceAlpha', my_face_alpha2, 'LineStyle', 'none', 'Marker', 'none'); 

    xx = transpose(C(:,1));
    yy2 = transpose(C(:,10));
    yy1 = transpose(C(:,8));
    fill([xx fliplr(xx)], [yy1 fliplr(yy2)], blue3, 'FaceAlpha', my_face_alpha2, 'LineStyle', 'none', 'Marker', 'none'); 

    plot( AL5(:,1), AL5(:,9), 'Color', blue2 , 'LineWidth', lw , 'LineStyle', '-' , 'Marker', 'none' ); 
    plot( C(:,1), C(:,9), 'Color', blue3 , 'LineWidth', lw , 'LineStyle', '-' , 'Marker', 'none' ); 

    set(gca, 'YTick', yticks_l );
    if( spi==2 || spi==4 || all_labels_blank )
        set(gca, 'YTickLabel', {''} );
    end
    
    if( odd && ~all_labels_blank )
        ylabel({'561H frequency (blue)' , 'Treatment Failure', 'Rate (red)'});
    end


    %%% 
    %%%  PLOT THE TREATMENT FAILURE RATE
    %%%

    xx = transpose(AL5(:,1));
    yy2 = transpose(AL5(:,4));
    yy1 = transpose(AL5(:,2));
    fill([xx fliplr(xx)], [yy1 fliplr(yy2)], red2, 'FaceAlpha', my_face_alpha2, 'LineStyle', 'none', 'Marker', 'none'); 

    xx = transpose(C(:,1));
    yy2 = transpose(C(:,4));
    yy1 = transpose(C(:,2));
    fill([xx fliplr(xx)], [yy1 fliplr(yy2)], red3, 'FaceAlpha', my_face_alpha2, 'LineStyle', 'none', 'Marker', 'none'); 

    plot( C(:,1), C(:,3), 'Color', red3 , 'LineWidth', lw, 'LineStyle', '-', 'Marker', 'none' ); 
    plot( AL5(:,1), AL5(:,3), 'Color', red2 , 'LineWidth', lw, 'LineStyle', '-', 'Marker', 'none' );

    axis([x1 x2 0.0 1.0]);
    op = get( gca, 'outerposition');
    set(gca, 'outerposition', op.*[1 1 stretch_r stretch_u] ) % numbers are left bottom width height
    grid on;


end
