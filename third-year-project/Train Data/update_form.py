import pandas as pd
import sys
import ast
from colorama import Fore, Style
import colorama

colorama.init()

write_form = pd.read_hdf("C:\\Users\\tommy\\OneDrive\\University\\Year 3\\Third Year Project\\Platform Album "
                         "Data\\new_unigram_data.h5", key="reduced_music_form")
read_form = pd.read_hdf("C:\\Users\\tommy\\OneDrive\\University\\Year 3\\Third Year Project\\Platform Album "
                        "Data\\new_unigram_data.h5", key="music_form")

progress = pd.read_csv("C:\\Users\\tommy\\OneDrive\\University\\Year 3\\Third Year Project\\Platform Album "
                       "Data\\reduced_music_progress.csv").iloc[0, 0]

labelled_reviews = read_form.loc[read_form["Desired"] == 1, "Review id"].unique()

for j in range(len(labelled_reviews)):

    id = labelled_reviews[j]
    review_text = read_form.loc[read_form["Review id"] == id]

    print(review_text.iloc[0].loc["Album"], review_text.iloc[0].loc["Artist"], review_text.iloc[0].loc["Platform"])

    for i in range(review_text.shape[0]):
        row = review_text.iloc[i]

        if row.loc["Desired"] == 1:
            print(Fore.RED + f"{i} {row.loc['Word']}" + Style.RESET_ALL, end=", ")
        else:
            print(f"{i} {row.loc['Word']}", end=", ")

    updates = input("Select updates:")

    if updates == "n":
        continue

    if updates == "end":
        sys.exit()

    for update in ast.literal_eval(updates):
        write_form.loc[(write_form["Review id"] == id) & (write_form["Word id"] == update), "Desired"] = 1

    write_form.to_hdf("C:\\Users\\tommy\\OneDrive\\University\\Year 3\\Third Year Project\\Platform Album "
                      "Data\\new_unigram_data.h5", key="reduced_music_form", mode="a")

    pd.DataFrame({"Progress": [progress + j]}, index=[0], columns=["Progress"]).to_csv(
        "C:\\Users\\tommy\\OneDrive\\University\\Year 3\\Third Year Project\\Platform Album "
        "Data\\reduced_music_progress.csv", mode="w", index=False)
