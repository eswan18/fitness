import pandas as pd

# Download my logging into mapmyfitness and then going to https://www.mapmyfitness.com/workout/export/csv
FILEPATH = '~/Downloads/run_history.csv'

# Some known "misspellings" of shoes.
TRANSFORMS = {
    'M1080K10': 'New Balance M1080K10',
    'M1080R10': 'New Balance M1080R10',
}

df = pd.read_csv(FILEPATH)
df['Shoes'] = df['Notes'].str.extract(r"b'.*Shoes: ([^\\]*)'")
df['Shoes'] = df['Shoes'].str.strip().replace(TRANSFORMS)

by_shoes = df.groupby('Shoes')['Distance (mi)'].sum().sort_values(ascending=False)
