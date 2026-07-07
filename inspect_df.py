import pandas as pd

df = pd.read_excel('HR Data.xlsx', engine='openpyxl')

cols = ['Business Travel','Department','Education Field','Gender','Job Role','Marital Status','Over Time','Education','Environment Satisfaction','Job Involvement','Job Level','Job Satisfaction','Performance Rating','Relationship Satisfaction','Work Life Balance','CF_age band','CF_current Employee']

for c in cols:
    if c in df.columns:
        vals = pd.unique(df[c].dropna())
        print(f"{c} ({len(vals)} unique): {list(vals)[:30]}")
    else:
        print(f"{c}: NOT FOUND in dataframe")
