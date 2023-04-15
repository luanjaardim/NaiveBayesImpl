import pandas as pd
from sklearn.model_selection import train_test_split

data = pd.read_csv('healthcare-dataset-stroke-data.csv', nrows=2000)
data_train, data_test = train_test_split(data, test_size=400)

data_test.to_csv('stroke_test_data.csv')
data_train.to_csv('stroke_train_data.csv')