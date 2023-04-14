import pandas as pd
from sklearn.naive_bayes import ComplementNB, GaussianNB, BernoulliNB
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from UnigramPreprocess import UnigramPreprocess
from sklearn.inspection import permutation_importance
import numpy as np
from sklearn.model_selection import KFold


def get_splits(ids, n_splits):
    kf = KFold(n_splits=5, shuffle=True)
    return kf.split(ids)


form = pd.read_hdf("C:\\Users\\tommy\\OneDrive\\University\\Year 3\\Third Year Project\\Platform Album "
                   "Data\\new_unigram_data.h5", key="reduced_music_form")

ids = pd.Series(form.loc[form["Desired"] == 1, "Review id"].unique())

np.random.seed(1)

preprocess = UnigramPreprocess("C:\\Users\\tommy\\OneDrive\\University\\Year 3\\Third Year Project\\Platform Album "
                               "Data\\new_unigram_data.h5", ids)
sent_word = preprocess.format_text()
sent_word = pd.merge(sent_word, form.loc[:, ["Word id", "Review id", "Desired"]], on=["Word id", "Review id"],
                     how="inner")

lift_dict = {i: [] for i in range(1, 11)}
lift_df = pd.DataFrame(lift_dict)

for train_split, test_split in get_splits(ids, 5):
    train_ids = ids.loc[train_split]
    test_ids = ids.loc[test_split]
    X_train = sent_word.loc[sent_word["Review id"].isin(train_ids)].drop(columns=["Desired", "Review id"]).reset_index(drop=True)
    X_test = sent_word.loc[sent_word["Review id"].isin(test_ids)].drop(columns=["Desired", "Review id"]).reset_index(drop=True)
    y_train = sent_word.loc[sent_word["Review id"].isin(train_ids), "Desired"].reset_index(drop=True)
    y_test = sent_word.loc[sent_word["Review id"].isin(test_ids), "Desired"].reset_index(drop=True)

    train_preprocess = UnigramPreprocess(
        "C:\\Users\\tommy\\OneDrive\\University\\Year 3\\Third Year Project\\Platform Album "
        "Data\\new_unigram_data.h5", ids)
    test_preprocess = UnigramPreprocess(
        "C:\\Users\\tommy\\OneDrive\\University\\Year 3\\Third Year Project\\Platform Album "
        "Data\\new_unigram_data.h5", ids, train_ids=train_ids)

    X_train = train_preprocess.get_album_frequency(X_train).drop(columns=["Review id"])
    X_test = test_preprocess.get_album_frequency(X_test).drop(columns=["Review id"])

    # Classifier
    clf = ComplementNB()
    # Encoder
    enc = OneHotEncoder()

    enc.fit(X_train.loc[:, ["ptag", "ntag", "tag", "Platform"]])
    # Encode any categorical variables
    one_hot = enc.transform(X_train.loc[:, ["ptag", "ntag", "tag", "Platform"]]).toarray()
    # Transform the data
    one_hot = pd.DataFrame(one_hot, columns=enc.get_feature_names_out())
    # Replace the columns with their one-hot variants
    X_train = pd.concat([X_train, one_hot], axis=1).drop(
        columns=["ptag", "ntag", "tag", "Text", "Platform", "Artist", "Album",
                 "Word id", "Word_Sentence id", "Sentence id"])
    features = X_train.columns

    # Fit the encoder
    enc.fit(X_test.loc[:, ["ptag", "ntag", "tag", "Platform"]])
    # Encode any categorical variables
    one_hot = enc.transform(X_test.loc[:, ["ptag", "ntag", "tag", "Platform"]]).toarray()
    # Transform the data
    one_hot = pd.DataFrame(one_hot, columns=enc.get_feature_names_out())
    # Replace the columns with their one-hot variants
    X_test = pd.concat([X_test, one_hot], axis=1).drop(
        columns=["ptag", "ntag", "tag", "Text", "Platform", "Artist", "Album", "Word id",
                 "Word_Sentence id",
                 "Sentence id"])
    # Missing columns from feature list
    missing_cols = [col for col in features if col not in X_test.columns]
    extra_cols = [col for col in X_test.columns if col not in features]

    # Make sure that the columns align between X and X_test
    X_train = pd.DataFrame(X_train)
    X_train = X_train.drop(columns=missing_cols)
    X_test = X_test.drop(columns=extra_cols)

    clf.fit(X_train, y_train)
    test_results = clf.predict_proba(X_test)

    sent_word_test = pd.merge(sent_word.loc[sent_word["Review id"].isin(test_ids)].drop(columns=["Desired"]),
                              form.loc[:, ["Word id", "Review id", "Desired"]], on=["Review id", "Word id"],
                              how="inner")
    test_results = sent_word_test.join(pd.DataFrame(test_results, columns=["neg_prob", "pos_prob"])).sort_values(
        by=["pos_prob"], ascending=False)

    cv_dict = {i: [] for i in range(1, 11)}
    cv_data = pd.DataFrame(cv_dict)

    for review_id in test_results.loc[:, "Review id"].unique():
        album_results = test_results.loc[test_results["Review id"] == review_id].sort_values(
            by=["pos_prob"], ascending=False)
        deciles = [x * round(album_results.shape[0] / 10) for x in range(1, 11)]
        album_data = {}

        desired_ratio = album_results.loc[album_results["Desired"] == 1].shape[0] / album_results.shape[0]

        for i in range(len(deciles)):
            decile = deciles[i]
            decile_results = album_results.iloc[:decile, :]
            album_data[i + 1] = (decile_results[decile_results["Desired"] == 1].shape[0] /
                                  (decile_results.shape[0] * desired_ratio))

        cv_data = cv_data.append(pd.Series(album_data), ignore_index=True)

    lift_df = lift_df.append(cv_data.mean(axis=0), ignore_index=True)


lift_df.to_csv("C:\\Users\\tommy\\OneDrive\\University\\Year 3\\Third Year Project\\Platform Album Data\\Model "
               "Evaluation\\lift.csv")