import pandas as pd
import sys
import ast

text = pd.read_hdf("C:\\Users\\tommy\\OneDrive\\University\\Year 3\\Third Year Project\\Platform Album "
                   "Data\\new_unigram_data.h5", key="text")
form = pd.read_hdf("C:\\Users\\tommy\\OneDrive\\University\\Year 3\\Third Year Project\\Platform Album "
                   "Data\\new_unigram_data.h5", key="form")

progress = pd.read_csv("C:\\Users\\tommy\\OneDrive\\University\\Year 3\\Third Year Project\\Platform Album "
                       "Data\\progress.csv").iloc[0, 0]

text = text.iloc[progress:, :]

for i in range(len(text)):
    row = text.iloc[i]

    print(row.loc["Artist"], row.loc["Album"], row.loc["Platform"])
    print([f"{j}: {row.loc['Text'][j]}" for j in range(len(row.loc["Text"]))])

    desireds = input("Select desireds:")

    if desireds == "n":
        continue

    if desireds == "end":
        sys.exit()

    for desired in ast.literal_eval(desireds):
        form.loc[(form["Review id"] == row.loc["Review id"]) & (form["Word id"] == desired), "Desired"] = 1

    form.to_hdf("C:\\Users\\tommy\\OneDrive\\University\\Year 3\\Third Year Project\\Platform Album "
                "Data\\new_unigram_data.h5", key="form", mode="a")
    pd.DataFrame({"Progress": [progress + i]}, index=[0], columns=["Progress"]).to_csv(
        "C:\\Users\\tommy\\OneDrive\\University\\Year 3\\Third Year Project\\Platform Album Data\\progress.csv",
        mode="w", index=False)
