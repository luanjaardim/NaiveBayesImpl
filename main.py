import pandas as pd
from sklearn.model_selection import train_test_split

def stop():
    while True:
        sla = 1

prob_for_zero_occurrences = 1e-4

class BayesProb:
        def __init__(self, train_data, stroke_occurencies) -> None:
            self.df_train = train_data
            self.stroke_occurencies_index = stroke_occurencies
            self.stroke_quant = len(self.stroke_occurencies_index) 
            self.stroke_occur_prob = self.stroke_quant / len(self.df_train)
            self.quantities = {}    
            self.list_of_all_possible_values = {} #shows every possible choose for each possible patient characteristic

        def add_possible_values(self, key, list_of_values):
            self.list_of_all_possible_values[key] = list_of_values

        def is_valid_value(self, key, value):
            if key in self.list_of_all_possible_values:
                return True if value in self.list_of_all_possible_values[key] else False
            else:
                return False

        def calculating_quants(self, key, list_of_possibilities):
            self.quantities[key] = {
                possibility : [
                       self.df_train[self.df_train[key] == possibility].shape[0],
                       len(set(self.df_train[self.df_train[key] == possibility].index.to_list()) & self.stroke_occurencies_index)
                ] for possibility in list_of_possibilities
            }
            self.add_possible_values(key, list_of_possibilities)

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
        the probability of the value when the stroke happened, P(B|A)
        '''
        def __calculating_value_cond_prob(self, key, value):
            return self.quantities[key][value][1] / len(self.df_train) if self.quantities[key][value][1] != 0 else prob_for_zero_occurrences
            
        '''
        list_of_characteristics may be a list of lists, every inner list must contain
        the characteristic and the corresponding possible value for it

        for simplicity we are assuming that the characteristics are independent on each other
        '''
        def calculating_probs(self, list_of_characteristic):
            probs = []
            for [key, value] in list_of_characteristic:
                if self.is_valid_value(key, value) == True:
                    probs.append(self.__calculating_value_cond_prob(key, value) / self.__calculating_value_prob(key, value))
                else:
                    return ValueError
            final_prob = self.stroke_occur_prob #P(A)
            for prob in probs:
                final_prob *= prob
            return final_prob #P(A|B, C, D) = P(A) * P(B|A) * P(C|A) * P(D|A) / P(B) * P(C) * P(D)
            
        def debug_info_quant(self):
            print(self.stroke_occur_prob)
            for key in self.quantities.keys():
                print(key, self.quantities[key])
    
df = pd.read_csv('stroke_train_data.csv')
set_stroke_ocurrences = set(df[df['stroke'] == 1].index.to_list())
bp = BayesProb(df, set_stroke_ocurrences)

#calculando as quantidades para cada coluna
bp.calculating_quants('gender', ['Male', 'Female', 'Other'])
bp.calculating_interval_quants('age', [age*5 + 5 for age in range(0, 17)])
bp.calculating_quants('hypertension', [0, 1])
bp.calculating_quants('heart_disease', [0, 1])
bp.calculating_quants('ever_married', ['Yes', 'No'])
bp.calculating_quants('work_type', ['Private', 'Govt_job', 'Self-employed', 'children', 'Nerver_worked'])
bp.calculating_quants('Residence_type', ['Urban', 'Rural'])
bp.calculating_interval_quants('avg_glucose_level', [gluc*10 + 65 for gluc in range(0, 22)])
bp.calculating_interval_quants('bmi', [bmi*5 + 15 for bmi in range(0, 18)])
bp.calculating_quants('smoking_status', ['never smoked', 'smokes', 'formerly smoked', 'Unknown'])

person = [['gender', 'Male'], ['age', 70], ['hypertension', 1], ['heart_disease', 1], ['ever_married', 'Yes'], ['work_type', 'Private'], ['Residence_type', 'Urban'], ['avg_glucose_level', 105], ['bmi', 75], ['smoking_status', 'smokes']]
prob = bp.calculating_probs(person)
print(prob)

#ABAIXO TEM APENAS RASCUNHOS DE CODIGOS PARA CHEGAR NO ATUAL E IDEIAS Q PODEM SER APROVEITADAS DEPOIS

#     0: 'gender',
#     1: 'age',
#     2: 'hypertension',
#     3: 'heart_disease',
#     4: 'ever_married',
#     5: 'work_type',
#     6: 'Residence_type',
#     7: 'avg_glucose_level',
#     8: 'bmi',
#     9: 'smoking_status',
#     # 10: 'stroke'
# }
# print( len(set(df_train[df_train['gender'] == "Male"].index.to_list()) & set_stroke_ocurrences))
# stop()
# gender_quant = {"Male": [df_train[df_train['gender'] == "Male"].shape[0],],
#                 "Female": df_train[df_train['gender'] == "Female"].shape[0],
#                 "Other": df_train[df_train['gender'] == "Other"].shape[0]
#                }

# age_intervals = [age*5 + 5 for age in range(0, 17)] #intevalos de idades, de 5 em cinco anos
# age_quant = {}
# accumulated = 0
# for some_age in age_intervals:
#     age_quant[some_age] = df_train[df_train['age'] <= some_age].shape[0] - accumulated
#     accumulated += age_quant[some_age]

# hypertension_quant = {
#                 0 : df_train[df_train['hypertension'] == 0].shape[0],
#                 1 : df_train[df_train['hypertension'] == 1].shape[0],
#         }
# heart_disease_quant = {
#                 0 : df_train[df_train['heart_disease'] == 0].shape[0],
#                 1 : df_train[df_train['heart_disease'] == 1].shape[0],
#         }   
 
# ever_married_quant = {
#                 "Yes": df_train[df_train['ever_married'] == "Yes"].shape[0],
#                 "No": df_train[df_train['ever_married'] == "No"].shape[0]
#         }

# work_type_quant = {
#                 "Private": df_train[df_train['work_type'] == "Private"].shape[0],
#                 "Govt_job": df_train[df_train['work_type'] == "Govt_job"].shape[0],
#                 "Self-employed": df_train[df_train['work_type'] == "Self-employed"].shape[0],
#                 "children": df_train[df_train['work_type'] == "children"].shape[0],
#                 "Never_worked": df_train[df_train['work_type'] == "Never_worked"].shape[0],
#         }

# residence_quant = {
#                 "Private": df_train[df_train['Residence_type'] == "Rural"].shape[0],
#                 "Urban": df_train[df_train['Residence_type'] == "Urban"].shape[0]
#         } 

# glucose_intervals = [] #intevalos de idades, de 5 em cinco anos
# glucose_quant = {}
# accumulated = 0
# for gluc in glucose_intervals:
#     glucose_quant[gluc] = df_train[df_train['avg_glucose_level'] <= gluc].shape[0] - accumulated
#     accumulated += glucose_quant[gluc]

# bmi_intervals = []
# bmi_quant = {}
# accumulated = 0
# for bmi in bmi_intervals:
#     bmi_quant[bmi] = df_train[df_train['bmi'] <= bmi].shape[0] - accumulated
#     accumulated += bmi_quant[bmi]
#     if type(bmi) != type(0.0) and type(bmi) != type(1):
#         print(type(bmi))
# bmi_quant['nan'] = LINE_TOTAL*(1 - TEST_SIZE) - accumulated

# smoking_status_quant = {
#                 f_train[df_train['smoking_status'] == "never smoked"].shape[0],
#                 n[df_train['smoking_status'] == "smokes"].shape[0],
#                 : df_train[df_train['smoking_status'] == "formerly smoked"].shape[0],
#                 in[df_train['smoking_status'] == "Unknown"].shape[0],
#        }

# stroke_quant = {
#             0: df_train[df_train['stroke'] == 0].shape[0],
#             1: df_train[df_train['stroke'] == 1].shape[0],
#         }

# soma_tudo(gender_quant)
# soma_tudo(age_quant)
# soma_tudo(hypertension_quant)
# soma_tudo(heart_disease_quant)
# soma_tudo(ever_married_quant)
# soma_tudo(work_type_quant)
# soma_tudo(residence_quant)
# soma_tudo(glucose_quant)
# soma_tudo(bmi_quant)
# soma_tudo(smoking_status_quant)
# soma_tudo(stroke_quant)
# stop()

# #calculando as probabilidades




# # class ProbData:
# #     def __init__(self) -> None:
# #         self.possibilities = {}
# #         for i in range(0, len(keys)):
# #             self.possibilities[keys[i]] = {}
# #     def add_parameter(self, parameter_name, possibilities_list):
# #         for word in possibilities_list:
# #             self.add_possibility(parameter_name, word)
# #     def add_possibility(self, key, label):
# #         if key in self.possibilities and label not in self.possibilities[key]:
# #             self.possibilities[key][label] = [0, 0]
# #     def increase_prob(self, key, label, stroke_value):
# #         self.possibilities[key][label][0] += 1
# #         if stroke_value == 1:
# #             self.possibilities[key][label][1] += 1
# #     def print_all(self):
# #         for key in self.possibilities:
# #             print(self.possibilities[key])

# #         # [0, 0] o primeiro é a quantidade de vezes que ele acontece, e o segundo a quantidade de vezes que o stroke ocorre quando ele ocorre

# # general_dict = ProbData()


# # interval = range(0, 4100) #intervalo de treino



# # for line in interval:
# #     for key in keys.values():
# #         print(data[key])
#         # print(data[key][data[key][line]], data[10][line])
#         # general_dict.increase_prob(data[key][data[key][line]], data[10][line])


# # general_dict.print_all()
# # val = []
# # for lines in data[keys[8]]:
# #     val.append(data[keys[8]][lines])
# # print(max(val))
# # print(min(val))

# # for word in ['Male', 'Female', 'Other']:
# #     general_dict.add_possibility(keys[0], word)

# # #min = 0.08  , max = 82.0
# # for word in [age_range*5 for age_range in range(0, 18)]: #dividido em range de idades, de 5 em 5 anos
# #     general_dict.add_possibility(keys[1], word)

# # for word in [0, 1]:
# #     general_dict.add_possibility(keys[2], word)
# # for word in [0, 1]:
# #     general_dict.add_possibility(keys[2], word)


# # EVER_MARRIED = 
# # WORK = []
# # RESIDENCE = []
# # AVG_GLUCOSE = []
# # BMI = []#indice de massa corporal
# # SMOOKING = []
# # STROKE = [0, 1]


    
#     # # print(keys)
#     # if keys == collumns[9]:
#     #     # print(keys)
#     #     for elements in data[keys]:
#     #         oi = data[keys][elements]
#     #         if oi not in SMOOKING:
#     #             print(oi)
#     #         # print(lines)
#     #         # if lines not in GENDER:
#     #         #     print("oi")
#     #         #     print(lines)
