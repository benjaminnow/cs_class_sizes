import pandas as pd

classes_df = pd.read_csv("umd/umd.csv")

# if row course_name and professor are the same, combine rows into one row

grouped = classes_df.groupby(["course_name", "professor"])

result = grouped.agg({"count": "sum"})

result.to_csv("umd_combined.csv")

print(result)