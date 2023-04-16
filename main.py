import pandas as pd
import bayes_model as bm

df = bm.read_csv_file('stroke_train_data.csv')
bp = bm.BayesProb()
bp.fit(df)

df_test = bm.read_csv_file('stroke_test_data.csv')
new_df_test = df_test.drop(['age', 'gender', 'bmi', 'smoking_status'], axis=1)

results = bp.predict(new_df_test)
acc = bp.model_accuracy(results, new_df_test['stroke'])

print(acc)