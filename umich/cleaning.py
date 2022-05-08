import pandas as pd

classes_df = pd.read_csv("umich/umich.csv")

# if row course_code, course_time, and course_instructors are the same, 
# combine rows into one row

#dupes = classes_df.duplicated(subset=["course_code", "course_time", "course_instructors"])

# ex class eecs 445

grouped = classes_df.groupby(["course_code", "course_time", "course_instructors"])

result = grouped.agg({"course_enrollment": "sum", "course_capacity": "sum"})

result.to_csv("umich_combined.csv")

print(result)