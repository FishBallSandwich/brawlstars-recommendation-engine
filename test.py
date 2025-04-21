import pandas as pd

# Sample Pandas DataFrame
data = [{'name':'john', 'index':2},{'name':'Doe', 'index':2}]
df = pd.DataFrame(data)

print("Original DataFrame:")
print(df)

# Convert DataFrame to a list of dictionaries using to_dict("records")
records = df.to_dict("records")

res = df['name'].tolist()
print(res)

