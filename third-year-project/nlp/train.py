import pandas as pd
from sklearn.naive_bayes import ComplementNB, GaussianNB, BernoulliNB
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from UnigramPreprocess import UnigramPreprocess
from sklearn.inspection import permutation_importance
from sklearn.model_selection import KFold
import numpy as np

def cross_validate(ids, folds):

    kf = KFold(n_splits=folds, shuffle=True)
    return kf.split(ids)

form = pd.read_hdf("C:\\Users\\tommy\\OneDrive\\University\\Year 3\\Third Year Project\\Platform Album "
                   "Data\\new_unigram_data.h5", key="reduced_music_form")
ids = form.loc[form["Desired"] == 1, "Review id"].unique()
np.random.seed(1)

preprocess = UnigramPreprocess("C:\\Users\\tommy\\OneDrive\\University\\Year 3\\Third Year Project\\Platform Album "
                               "Data\\new_unigram_data.h5", ids)
preprocessed_reviews = preprocess.format_text()
preprocessed_reviews = pd.merge(preprocessed_reviews, form.loc[:, ["Word id", "Review id", "Desired"]],
                                on=["Word id", "Review id"], how="inner")

# For each split in cross validation
for train_split, test_split in cross_validate(ids, 5):

    # Get train and test splits
    train_ids = ids[train_split]
    test_ids = ids[test_split]

    enc = OneHotEncoder()
    enc.fit(preprocessed_reviews.loc[:, ["ptag", "pptag", "ntag", "Platform", "tag"]])
    one_hot = enc.transform(
        preprocessed_reviews.loc[:, ["ptag", "pptag", "ntag", "nntag", "Platform", "tag"]]).toarray()
    one_hot = pd.DataFrame(one_hot, columns=enc.get_feature_names_out())
    preprocessed_reviews = pd.concat([preprocessed_reviews, one_hot], axis=1).drop(
        columns=["ptag", "pptag", "ntag", "nntag", "Text", "tag", "Platform", "Artist", "Album", "Word id",
                 "Word_Sentence id", "Sentence id"])

    X_train = preprocessed_reviews.loc[preprocessed_reviews["Review id"].isin(train_split)]
    X_test = preprocessed_reviews.loc[preprocessed_reviews["Review id"].isin(test_split)]
    y_train = X_train.loc[:, "Desired"]
    y_test = X_train.loc[:, "Desired"]

    X_train = X_train.drop(columns=["Review id", "Desired"])
    X_test = X_test.drop(columns=["Review id", "Desired"])

    # Classifier
    clf = ComplementNB()

    # features = X.columns

    # albums = form.loc[form["Review id"].isin([99, 100, 101]), "Album"].unique()
    # ids_test = form.loc[form["Album"].isin(["sometimes i might be introvert"]), "Review id"].unique()

    # preprocess_test = UnigramPreprocess("C:\\Users\\tommy\\OneDrive\\University\\Year 3\\Third Year Project\\Platform Album "
    #                              "Data\\new_unigram_data.h5", test_ids)
    #
    # sent_word_test = preprocess_test.format_text()
    #
    # # Set predictors and target
    # X_test = sent_word_test.drop(columns=["Review id"])
    # # Fit the encoder
    # enc.fit(X_test.loc[:, ["ptag", "pptag", "ntag", "nntag", "Platform", "tag"]])
    # # Encode any categorical variables
    # one_hot = enc.transform(X_test.loc[:, ["ptag", "pptag", "ntag", "nntag", "Platform", "tag"]]).toarray()
    # # Transform the data
    # one_hot = pd.DataFrame(one_hot, columns=enc.get_feature_names_out())
    # # Replace the columns with their one-hot variants
    # X_test = pd.concat([X_test, one_hot], axis=1).drop(
    #     columns=["ptag", "pptag", "ntag", "nntag", "Text", "tag", "Platform", "Artist", "Album", "Word id", "Word_Sentence id",
    #              "Sentence id"])
    # # Missing columns from feature list
    # missing_cols = [col for col in features if col not in X_test.columns]
    # extra_cols = [col for col in X_test.columns if col not in features]
    #
    # # Make sure that the columns align between X and X_test
    # X = pd.DataFrame(X)
    # X = X.drop(columns=missing_cols)
    # X_test = X_test.drop(columns=extra_cols)

    # sc.fit(X_test)
    # X_test = sc.transform(X_test)

    # X.to_csv("C:\\Users\\tommy\\OneDrive\\University\\Year 3\\Third Year Project\\Platform Album "
    #          "Data\\X_data.csv")

    clf.fit(X_train, y_train)
    test_results = clf.predict_proba(X_test)

    sent_word_test = pd.merge(X_test, form.loc[:, ["Word id", "Review id", "Desired"]], on=["Review id", "Word id"],
                              how="inner")
    test_results = sent_word_test.join(pd.DataFrame(test_results, columns=["neg_prob", "pos_prob"])).sort_values(
        by=["pos_prob"], ascending=False)

    # first_dict = {}
    #
    # for k, v in zip(test_results.loc[:, "Text"], test_results.loc[:, "pos_prob"]):
    #     first_dict[k] = v

    # cloud = WordCloud().generate_from_frequencies(first_dict)
    # plt.imshow(cloud)
    # plt.show()

    # test_results.to_csv("C:\\Users\\tommy\\OneDrive\\University\\Year 3\\Third Year Project\\Platform Album "
    #                     "Data\\test_results.csv")
    #
    # imps = permutation_importance(clf, X_test, sent_word_test.loc[:, "Desired"])
    # imps_df = pd.DataFrame({"Feature": X.columns, "Importance": imps.importances_mean}).sort_values(by="Importance")
