result_matrix = zeros(100,3);
for dataset = 1:3
    if dataset == 1
        load('data/randomData');
        disp('Random Data');
    end
    if dataset == 2
        load('data/craftedData');
        disp('Crafted Data');
    end
    if dataset == 3
        load('data/industrialData');
        disp('Industrial Data');
    end
    
    performance_sum = 0;
    num_iter = 100;
    
    for j = 1:num_iter
        % Solve a Pattern Recognition Problem with a Neural Network
        % This script assumes these variables are defined:
        %   data - input data.
        %   Class - target data.

        inputs = data';
        targets = Class';
    
        % Create a Pattern Recognition Network
        hiddenLayerSize = 35;
        net = patternnet(hiddenLayerSize);

        % Setup Division of Data for Training, Validation, Testing
        net.divideParam.trainRatio = 70/100;
        net.divideParam.valRatio = 15/100;
        net.divideParam.testRatio = 15/100;

        % Train the Network
        [net,tr] = train(net,inputs,targets);

        % Test the Network
        outputs = net(inputs);
        errors = gsubtract(targets,outputs);
        performance = 1 - perform(net,targets,outputs);
        disp(performance);
        result_matrix(j,dataset) = performance;
        performance_sum = performance_sum + performance;
        % View the Network
        %view(net)

        % Plots
        % Uncomment these lines to enable various plots.
        %figure, plotperform(tr)
        %figure, plottrainstate(tr)
        %figure, plotconfusion(targets,outputs)
        %figure, ploterrhist(errors)
    end
    performance_avg = performance_sum/num_iter;
    performance_avg_str = strcat('Performance Average : ',num2str(performance_avg));  
    disp(performance_avg_str);
end    
csvwrite('classification_MLP35.csv',result_matrix);
