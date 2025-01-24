import pandas as pd

data_path = 'E:/Downloads/Caroline Dolehide v Coco Gauff Full Match  Australian Open 2024 Second Round - Run 1 - Tiebr.csv'
data = pd.read_csv(data_path)

max_instance_by_row = data.groupby('Row')['Instance number'].max().reset_index()
data_fin = max_instance_by_row.T

print(data_fin)