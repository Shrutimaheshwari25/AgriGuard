import pandas as pd
df = pd.read_csv('synthetic_crop_data.csv')
with open('stats.txt', 'w') as f:
    f.write(df.groupby('label').mean().to_string())
