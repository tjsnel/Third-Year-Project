import pandas as pd
from sklearn.naive_bayes import ComplementNB, GaussianNB, BernoulliNB
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from UnigramPreprocess import UnigramPreprocess
from sklearn.inspection import permutation_importance
import numpy as np

form = pd.read_hdf("C:\\Users\\tommy\\OneDrive\\University\\Year 3\\Third Year Project\\Platform Album "
                   "Data\\new_unigram_data.h5", key="reduced_music_form")

ids = form.loc[form["Desired"] == 1, "Review id"].unique()

train_ids = pd.Series(np.random.choice(ids, size=int(len(ids) * 0.75), replace=False))
test_ids = pd.Series([labelled_id for labelled_id in ids if labelled_id not in train_ids])

preprocess = UnigramPreprocess("C:\\Users\\tommy\\OneDrive\\University\\Year 3\\Third Year Project\\Platform Album "
                        "Data\\new_unigram_data.h5", train_ids)
form = pd.read_hdf("C:\\Users\\tommy\\OneDrive\\University\\Year 3\\Third Year Project\\Platform Album "
                   "Data\\new_unigram_data.h5", key="reduced_music_form")

sent_word = preprocess.format_text()
sent_word = pd.merge(sent_word, form.loc[:, ["Word id", "Review id", "Desired"]], on=["Word id", "Review id"],
                     how="inner")

# Set predictors and target
X = sent_word.drop(columns=["Desired", "Review id"])
y = sent_word.loc[:, "Desired"]

# Classifier
clf = ComplementNB()
# Encoder
enc = OneHotEncoder()

# Fit the encoder
enc.fit(X.loc[:, ["ptag", "pptag", "ntag", "nntag", "Platform", "tag"]])
# Encode any categorical variables
one_hot = enc.transform(X.loc[:, ["ptag", "pptag", "ntag", "nntag", "Platform", "tag"]]).toarray()
# Transform the data
one_hot = pd.DataFrame(one_hot, columns=enc.get_feature_names_out())
# Replace the columns with their one-hot variants
X = pd.concat([X, one_hot], axis=1).drop(columns=["ptag", "pptag", "ntag", "nntag", "Text", "tag", "Platform", "Artist", "Album",
                                                  "Word id", "Word_Sentence id", "Sentence id"])
features = X.columns

# albums = form.loc[form["Review id"].isin([99, 100, 101]), "Album"].unique()
# ids_test = form.loc[form["Album"].isin(["sometimes i might be introvert"]), "Review id"].unique()

preprocess_test = UnigramPreprocess("C:\\Users\\tommy\\OneDrive\\University\\Year 3\\Third Year Project\\Platform Album "
                             "Data\\new_unigram_data.h5", ids=test_ids, train_ids=train_ids)

sent_word_test = preprocess_test.format_text()

# Set predictors and target
X_test = sent_word_test.drop(columns=["Review id"])
# Fit the encoder
enc.fit(X_test.loc[:, ["ptag", "pptag", "ntag", "nntag", "Platform", "tag"]])
# Encode any categorical variables
one_hot = enc.transform(X_test.loc[:, ["ptag", "pptag", "ntag", "nntag", "Platform", "tag"]]).toarray()
# Transform the data
one_hot = pd.DataFrame(one_hot, columns=enc.get_feature_names_out())
# Replace the columns with their one-hot variants
X_test = pd.concat([X_test, one_hot], axis=1).drop(
    columns=["ptag", "pptag", "ntag", "nntag", "Text", "tag", "Platform", "Artist", "Album", "Word id", "Word_Sentence id",
             "Sentence id"])
# Missing columns from feature list
missing_cols = [col for col in features if col not in X_test.columns]
extra_cols = [col for col in X_test.columns if col not in features]

# Make sure that the columns align between X and X_test
X = pd.DataFrame(X)
X = X.drop(columns=missing_cols)
X_test = X_test.drop(columns=extra_cols)

# sc.fit(X_test)
# X_test = sc.transform(X_test)

X.to_csv("C:\\Users\\tommy\\OneDrive\\University\\Year 3\\Third Year Project\\Platform Album "
         "Data\\X_data.csv")

clf.fit(X, y)
test_results = clf.predict_proba(X_test)

sent_word_test = pd.merge(sent_word_test, form.loc[:, ["Word id", "Review id", "Desired"]], on=["Review id", "Word id"],
                          how="inner")
test_results = sent_word_test.join(pd.DataFrame(test_results, columns=["neg_prob", "pos_prob"])).sort_values(
    by=["pos_prob"], ascending=False)

first_dict = {}

for k, v in zip(test_results.loc[:, "Text"], test_results.loc[:, "pos_prob"]):
    first_dict[k] = v

# cloud = WordCloud().generate_from_frequencies(first_dict)
# plt.imshow(cloud)
# plt.show()

test_results.to_csv("C:\\Users\\tommy\\OneDrive\\University\\Year 3\\Third Year Project\\Platform Album "
                    "Data\\test_results.csv")

imps = permutation_importance(clf, X_test, sent_word_test.loc[:, "Desired"])
imps_df = pd.DataFrame({"Feature": X.columns, "Importance": imps.importances_mean}).sort_values(by="Importance")
