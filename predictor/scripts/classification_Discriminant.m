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
    
    for j = 1:num_iter
    
        myIndices = randperm(size(inputs,1));
        inputs = inputs(myIndices,:); 
        targets = targets(myIndices,:);
    
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
            classifier = ClassificationDiscriminant.fit(train_data(trainIdx,:), train_class(trainIdx),...
                'discrimType','pseudoLinear');
            %# test using test instances
            pred = classifier.predict(train_data(testIdx,:));
            
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
%disp(performance);
%csvwrite('classification_Tree.csv',result_matrix);
    
