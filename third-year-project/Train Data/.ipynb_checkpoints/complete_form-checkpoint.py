import pandas as pd
import sys
import ast

text = pd.read_hdf("C:\\Users\\tommy\\OneDrive\\University\\Year 3\\Third Year Project\\Platform Album "
                   "Data\\unigram_data.h5", key="text")
form = pd.read_hdf("C:\\Users\\tommy\\OneDrive\\University\\Year 3\\Third Year Project\\Platform Album "
                   "Data\\unigram_data.h5", key="form")

platforms = ["Pitchfork", "Guardian", "Spectrum", "NME"]
progress = pd.read_csv("C:\\Users\\tommy\\OneDrive\\University\\Year 3\\Third Year Project\\Platform Album "
                       "Data\\progress.csv").iloc[0, 0]

text = text.iloc[progress:, :]

for i in range(len(text)):
    row = text.iloc[i]

    for platform in platforms:

        print(row.loc["Artist"], row.loc["Album"], platform)
        print([f"{j}: {row.loc[platform][j]}" for j in range(len(row.loc[platform]))])

        desireds = input("Select desireds:")

        if desireds == "n":
            continue

        if desireds == "end":
            sys.exit()

        for desired in ast.literal_eval(desireds):
            form.loc[(form["Artist"] == row.loc["Artist"]) & (form["Album"] == row.loc["Album"]) &
                     (form["Platform"] == platform) & (form["id"] == desired), "Desired"] = 1

        form.to_hdf("C:\\Users\\tommy\\OneDrive\\University\\Year 3\\Third Year Project\\Platform Album "
                    "Data\\unigram_data.h5", key="form", mode="a")
        pd.DataFrame({"Progress": [i]}, index=[0], columns=["Progress"]).to_csv(
            "C:\\Users\\tommy\\OneDrive\\University\\Year 3\\Third Year Project\\Platform Album Data\\progress.csv",
            mode="w", index=False)
