import pandas as pd

#if some value doesn't happen on training
prob_for_zero_occurrences = 1e-4

ALL_DATASET_POSSIBLE_VALUES = {
      'gender'            : ['Male', 'Female', 'Other'],
      'age'               : [age*5 + 5 for age in range(0, 17)],
      'hypertension'      : [0, 1],
      'heart_disease'     : [0, 1],
      'ever_married'      : ['Yes', 'No'],
      'work_type'         : ['Private', 'Govt_job', 'Self-employed', 'children', 'Nerver_worked'],
      'Residence_type'    : ['Urban', 'Rural'],
      'avg_glucose_level' : [gluc*10 + 65 for gluc in range(0, 22)],
      'bmi'               : [bmi*5 + 15 for bmi in range(0, 18)],
      'smoking_status'    : ['never smoked', 'smokes', 'formerly smoked', 'Unknown'],
      'stroke'            : [0, 1]
}

def read_csv_file(file):
    return pd.read_csv(file).drop(['id'], axis=1)

class BayesProb:
        def __init__(self) -> None:
            self.quantities = {}    
            self.list_of_all_possible_values = {} #shows every possible choose for each possible patient characteristic

        def fit(self, x_data, y_data):
            x_data['stroke'] = pd.DataFrame(y_data)['stroke']
            self.df_train = x_data
            self.stroke_occurencies_index = set(self.df_train[self.df_train['stroke'] == 1].index.tolist())
            self.stroke_quant = len(self.stroke_occurencies_index)
            self.stroke_occur_prob = self.stroke_quant / len(self.df_train)
            self.calculating_all_quants()

        def add_possible_values(self, key, list_of_values):
            self.list_of_all_possible_values[key] = list_of_values

        def is_valid_value(self, key, value):
            if key in self.list_of_all_possible_values:
                return True if value in self.list_of_all_possible_values[key] else False
            else:
                return False

        '''
        calculating all quantities for every possible value on each column
        '''
        def calculating_all_quants(self):
          for key in self.df_train:
              if key in ['age', 'bmi', 'avg_glucose_level']:
                  self.calculating_interval_quants(key, ALL_DATASET_POSSIBLE_VALUES[key])
              else:
                  self.calculating_quants(key, ALL_DATASET_POSSIBLE_VALUES[key])
        
        '''
        calculating the number of occurences for every possible value, and the number of occurences that the value and the stoke happened
        '''
        def calculating_quants(self, key, list_of_possibilities):
            self.quantities[key] = {
                possibility : [
                       self.df_train[self.df_train[key] == possibility].shape[0],
                       len(set(self.df_train[self.df_train[key] == possibility].index.to_list()) & self.stroke_occurencies_index)
                ] for possibility in list_of_possibilities
            }
            self.add_possible_values(key, list_of_possibilities)

        '''
        for ranged values, here we find the group of the value
        '''
        def __find_corresponding_range(self, key, value):
            ar = self.list_of_all_possible_values[key]
            for val in ar:
                if value <= val:
                    return val

        '''
        for our dataset there are numerical values sparsely distributed, here we agroup them in ranges
        '''
        def calculating_interval_quants(self, key, list_of_range_possibilities):
            lower_limit = 0
            self.quantities[key] = { range : [0, 0] for range in list_of_range_possibilities }
            for upper_limit in list_of_range_possibilities:
                for (values, ind) in zip(self.df_train[key], self.df_train[key].index):
                    if values > lower_limit and values <= upper_limit:
                        self.quantities[key][upper_limit][0] += 1
                        if self.df_train['stroke'][ind] == 1:
                            self.quantities[key][upper_limit][1] += 1
                lower_limit = upper_limit
            self.add_possible_values(key, list_of_range_possibilities)

        '''
        the probability of the value happening, P(B)
        '''
        def __calculating_value_prob(self, key, value):
            return self.quantities[key][value][0] / len(self.df_train) if self.quantities[key][value][0] != 0 else prob_for_zero_occurrences
        
        '''
        the probability of the value when the stroke happened 'y'(P(B|A)) or the value happened when the stroke does not occur 'n'(P(B|~A))
        '''
        def __calculating_value_cond_prob(self, key, value, yes_no_occcur):
            if yes_no_occcur == 'y':
                return self.quantities[key][value][1] / self.stroke_quant if self.quantities[key][value][1] != 0 else prob_for_zero_occurrences
            elif yes_no_occcur == 'n':
                return (self.quantities[key][value][0] - self.quantities[key][value][1]) / (len(self.df_train) - self.stroke_quant) if self.quantities[key][value][1] != 0 else prob_for_zero_occurrences
            
        '''
        list_of_characteristics may be a list of lists, every inner list must contain
        the characteristic and the corresponding possible value for it

        return 1 if the prevision is that the stroke will occur, 0 otherwise
        '''
        def calculating_probs(self, list_of_characteristic):
            probs = []
            for [key, value] in list_of_characteristic:
                if self.is_valid_value(key, value) == True:
                    value_prob = self.__calculating_value_prob(key, value)
                    probs.append([self.__calculating_value_cond_prob(key, value, 'y') / value_prob,
                                  self.__calculating_value_cond_prob(key, value, 'n') / value_prob]) #P(X|A) / P(X) and P(X|~A) / P(X)
                else:
                    probs.append([prob_for_zero_occurrences, prob_for_zero_occurrences])
            final_prob = [self.stroke_occur_prob, 1 - self.stroke_occur_prob ] #P(A) and P(~A)
            for prob in probs:
                final_prob[0] *= prob[0]
                final_prob[1] *= prob[1]
            return 1 if final_prob[0] >= final_prob[1] else 0 
            #final_prob[0] = P(A|B, C, D) = P(A) * P(B|A) * P(C|A) * P(D|A) / P(B) * P(C) * P(D)
            #final_prob[1] = P(~A|B, C, D) = P(~A) * P(B|~A) * P(C|~A) * P(D|~A) / P(B) * P(C) * P(D)

        '''
        receive a DataFrame and send it to the calculating function, then return the result of the calculation
        '''
        def predict(self, input):
            input_data = {}
            for key in input:
                if key in self.list_of_all_possible_values and key != 'stroke':
                    input_data[key] = input[key].values.tolist()

            results = []
            values = []
            for key in input_data:
                if key in ['age', 'avg_glucose_level', 'bmi']:
                    values.append([[key, self.__find_corresponding_range(key, value)] for value in input_data[key]])
                else:
                    values.append([[key, value] for value in input_data[key]])
            for ind in range(len(values[0])):
                results.append(self.calculating_probs([values[key][ind] for key in range(len(values))]))
            return results

        def model_accuracy(self, predict_result, result):
            correct_prediction = 0
            for (predicted_value, real_value) in zip(predict_result, result):
                if(predicted_value == real_value):
                    correct_prediction += 1
            return correct_prediction / len(result)