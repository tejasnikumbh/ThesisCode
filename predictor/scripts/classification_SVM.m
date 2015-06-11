%result_matrix = zeros(10,3);
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
    num_iter = 1;
  

    % This script assumes these variables are defined:
    %   data - input data.
    %   Class - target data.
   
    inputs = data;
    targets = Class;
    
    % Random shuffling since we might actually end up considering only 80% 
    % of samples
    shuffle_order = randperm(size(inputs,1));
    inputs = inputs(shuffle_order,:);
    targets = targets(shuffle_order,:);
        
    for j = 1:num_iter
    
        % Splitting into train and test data
        % We use a 80-20 split here
        sz = size(inputs);
        num_samples = floor(1*sz(1));
        num_features = sz(2);
    
        train_data = inputs(1:num_samples,:);
        train_class = targets(1:num_samples,:);
        test_data = inputs(num_samples:end,:);
        test_class = targets(num_samples:end,:);
    
        %disp(size(train_data));
        %disp(size(train_class));
        %disp(size(test_data));
        %disp(size(test_class));
        %# number of cross-validation folds:
        %# If you have 50 samples, divide them into 10 groups of 5 samples each,
        %# then train with 9 groups (45 samples) and test with 1 group (5 samples).
        %# This is repeated ten times, with each group used exactly once as a test set.
        %# Finally the 10 results from the folds are averaged to produce a single 
        %# performance estimation.
        k=10;

        cvFolds = crossvalind('Kfold', train_class, k);   %# get indices of 10-fold CV
        cp = classperf(train_class);                      %# init performance tracker

        for i = 1:k                                  %# for each fold
            testIdx = (cvFolds == i);                %# get indices of test instances
            trainIdx = ~testIdx;                     %# get indices training instances

            %# train an SVM model over training instances
            asvmModel = svmtrain(train_data(trainIdx,:), train_class(trainIdx), ...
                 'Autoscale',true, 'Showplot',false, 'Method','QP', ...
                 'BoxConstraint',2e-1, 'Kernel_Function','rbf', 'RBF_Sigma',1);

            %# test using test instances
            pred = svmclassify(asvmModel, train_data(testIdx,:), 'Showplot',false);

            %# evaluate and update performance object
            cp = classperf(cp, pred, testIdx);
        end
        
        R = cp.CountingMatrix;
        disp(R);
        % Display statistics
        sat_incorrect = (100*R(1,2))/(R(2,2)+R(1,2));
        disp(strcat('SAT Incorrect Classification: ',num2str(sat_incorrect)));
        
        unsat_incorrect = (100*R(2,1))/(R(1,1)+R(2,1));
        disp(strcat('UNSAT Incorrect Classification: ',num2str(unsat_incorrect)));
        
        %# get accuracy
        performance_sum = performance_sum + cp.CorrectRate;
        disp(strcat('Prediction Accuracy: ',num2str(cp.CorrectRate)));
        
        %result_matrix(j,dataset) = cp.CorrectRate;
    end
end

%performance = performance_sum/num_iter;
%disp(performance)
%csvwrite('classification_SVM.csv',result_matrix);
    