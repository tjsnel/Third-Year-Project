import pandas as pd
import numpy as np
from nltk.tokenize.nist import NISTTokenizer
import sys
import re
from nltk.tokenize.nist import NISTTokenizer
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import string
import nltk


def tokenize_both(x):

    nist_tokenizer = NISTTokenizer()

    return [nist_tokenizer.tokenize(sentence) for sentence in sent_tokenize(x)]


def replace_quotes(x):
    for match in re.findall(" “.+?[”'\1{2}]", x):
        x = x.replace(match, "")

    return x


def preprocess(x):

    nist_tokenizer = NISTTokenizer()
    x = replace_quotes(x)
    x = nist_tokenizer.tokenize(x)
    x = [word for word in x if word not in string.punctuation and word not in stopwords.words("english")]

    return x


platforms = ["Pitchfork", "Guardian", "Spectrum", "NME"]
path = "C:\\Users\\tommy\\OneDrive\\University\\Year 3\\Third Year Project\\Platform Album Data\\text_edited_data.h5"

dfs = {platform: pd.read_hdf(path, key=platform) for platform in platforms}
text = pd.Series(dtype=object)

all_text = dfs["Pitchfork"].loc[:, ["Artist", "Album", "Text"]].rename({"Text": "Pitchfork"}, axis=1)

for platform, df in list(dfs.items())[1:]:
    all_text[platform] = df.loc[:, "Text"]

for platform in platforms:
    all_text.loc[:, platform] = all_text.loc[:, platform].apply(lambda x: preprocess(x))

all_text.to_hdf("C:\\Users\\tommy\\OneDrive\\University\\Year 3\\Third Year Project\\Platform Album "
                "Data\\unigram_data.h5", mode="a", key="text")

np.random.seed(0)
sample = np.random.choice(a=len(all_text), size=int(len(all_text) / 5), replace=False)

samples = all_text.iloc[sample, :]

sample_data = {"Artist": [],
               "Album": [],
               "Platform": [],
               "id": [],
               "Desired": []}

for i in range(len(samples)):
    for platform in platforms:
        row = samples.iloc[i]
        for j in range(len(row.loc[platform])):
            sample_data["Artist"].append(row.loc["Artist"])
            sample_data["Album"].append(row.loc["Album"])
            sample_data["Platform"].append(platform)
            sample_data["id"].append(j)
            sample_data["Desired"].append(-1)

sample_data = pd.DataFrame(sample_data)

sample_data.to_hdf("C:\\Users\\tommy\\OneDrive\\University\\Year 3\\Third Year Project\\Platform Album "
                   "Data\\unigram_data.h5", key="form", mode="a")
