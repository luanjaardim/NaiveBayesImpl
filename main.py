import pandas as pd
import bayes_model as bm
from sklearn.model_selection import train_test_split

df = bm.read_csv_file('healthcare-dataset-stroke-data.csv')

X_train, X_test, y_train, y_test = train_test_split(df.drop(['stroke'], axis=1), df['stroke'], test_size=0.5, random_state=0)

bp = bm.BayesProb()
bp.fit(X_train, y_train)

results = bp.predict(X_test)
acc = bp.model_accuracy(results, y_test)

print(acc)