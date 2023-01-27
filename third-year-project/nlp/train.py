import pandas as pd
import numpy as np
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from nltk.tokenize.nist import NISTTokenizer
import ast
from sklearn.svm import SVC
from sklearn.naive_bayes import ComplementNB, GaussianNB
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from nltk.stem import WordNetLemmatizer
from nltk.corpus import opinion_lexicon


class Preprocess:

    def __init__(self, path, ids):

        self.full_text = pd.read_hdf(path, key="text")
        self.full_sentence = pd.read_hdf(path, key="sentence")
        self.full_sentence.loc[:, "Text"] = self.full_sentence.loc[:, "Text"].apply(ast.literal_eval)
        self.full_form = pd.read_hdf(path, key="form")
        self.ids = set(ids.tolist())

    def to_lower(self, df, col):

        df.loc[:, col] = df.loc[:, col].astype(str).apply(lambda x: x.lower())
        return df

    def to_lower_list(self, df, col):

        df.loc[:, col] = df.loc[:, col].apply(lambda x: [word.lower() for word in x])
        return df

    def remove_stop(self, df, col):

        english_stopwords = set(stopwords.words("english"))
        is_stop = df.loc[:, col].apply(lambda x: x not in english_stopwords)
        return df.loc[is_stop]

    def remove_stop_list(self, df, col):

        english_stopwords = set(stopwords.words("english"))
        df.loc[:, col] = df.loc[:, col].apply(lambda x: [word for word in x if word not in english_stopwords])
        return df

    def get_pos_tags(self, df, col):

        tags = df.loc[:, col].apply(lambda x: nltk.pos_tag(x))
        tags = tags.explode(col)
        tags = tags.apply(lambda x: x[1])
        return tags

    def get_offset(self, df, col, offset):

        return df.loc[:, col].shift(offset)

    def get_desired_reviews(self, df):

        return df.loc[df.loc[:, "Review id"].apply(lambda x: x in self.ids)]

    def format_words(self):

        # Filter by desired words
        text = self.full_text.copy()
        text = self.get_desired_reviews(text)

        # POS tagging
        tags = self.get_pos_tags(text, "Text")
        text = text.explode("Text").reset_index(drop=True)
        text["tag"] = tags
        text["ptag"] = self.get_offset(text, "tag", 1)
        text["ntag"] = self.get_offset(text, "tag", -1)

        # Lower case and remove stopwords
        text = self.to_lower(text, "Text")
        text = self.remove_stop(text, "Text").reset_index(drop=True)

        # Get word ids
        word_ids = self.full_form.copy()
        word_ids = self.get_desired_reviews(word_ids)
        word_ids = self.to_lower(word_ids, "Word")
        word_ids = self.remove_stop(word_ids, "Word").reset_index(drop=True)
        text["Word id"] = word_ids.loc[:, "Word id"]

        # Get word proportions across all platforms for each review
        text = self.get_album_frequency(text)

        return text

    def format_sentences(self):

        text = self.preprocess_sentence(self.full_sentence.copy())

        # Get opinion word proportions by sentence
        text = self.get_opinion_frequency(text)

        return text

    def preprocess_sentence(self, text):

        # Get sentence id for each sentence
        text = text.explode("Text")
        text["Sentence id"] = text.groupby(["Review id"]).cumcount()

        # Get word id and word within sentence id
        text = text.explode("Text")
        text["Word_Sentence id"] = text.groupby(["Review id", "Sentence id"]).cumcount()
        text["Word id"] = text.groupby(["Review id"]).cumcount()

        # Remove stopwords
        text = self.to_lower(text, "Text")
        text = self.remove_stop(text, "Text")

        return text

    def get_album_frequency(self, df):

        # Filter by desired words
        text = self.full_text.copy()
        text = self.get_desired_reviews(text)

        # Lower case and remove stopwords
        text = self.to_lower_list(text, "Text")
        text = self.remove_stop_list(text, "Text")

        # Get all text for every album
        text = text.loc[:, ["Album", "Text"]].groupby(["Album"]).agg({"Text": self.join_list})

        lemmatiser = WordNetLemmatizer()

        # Lemmatise every word for each album
        text.loc[:, "Text"] = text.loc[:, "Text"].apply(lambda x: [lemmatiser.lemmatize(word) for word in x])

        counts = {}

        # For each album get all the relevant text Count the occurrences of each word and divide by the total number
        # of word to get the relative frequency of each lemmatised word
        for album in text.index:
            album_text = text.loc[album, "Text"]
            counts[album] = pd.value_counts(np.array(album_text)) / len(album_text)

        df["Platform TF"] = df.apply(lambda x: counts[x.loc["Album"]][lemmatiser.lemmatize(x.loc["Text"])], axis=1)

        return df

    def join_list(self, text):

        output = []

        for platform_text in text.tolist():
            output = output + platform_text

        return output

    def get_opinion_frequency(self, df):

        # Get a copy of the sentence data frame including:
        # Ids for word, sentence_word and sentence
        # Rows for each word
        # All usual album data name, artist, platform
        opinion_sentence = df.copy()
        # Make this a set or it takes forever
        opinion_words = set(opinion_lexicon.words())

        # Get a boolean mask for whether each word is an opinion word
        opinion_sentence["Opinion Word"] = opinion_sentence.loc[:, "Text"].apply(lambda x: x in opinion_words)
        # Use the integer form of this as a feature in the sent_word dataset
        df = pd.merge(df,
                      opinion_sentence.loc[:, ["Sentence id", "Word id", "Review id", "Opinion Word"]],
                      on=["Sentence id", "Word id", "Review id"], how="inner")
        df.loc[:, "Opinion Word"] = df.loc[:, "Opinion Word"].astype(int)
        # Group by sentence and review id
        opinion_sentence_group = opinion_sentence.groupby(["Sentence id", "Review id"])
        # Get the sum of opinion words for each sentence
        opinion_sentence_agg = opinion_sentence_group.agg({"Opinion Word": "sum"}).reset_index()
        # Get the number of words in each sentence
        opinion_sentence_count = opinion_sentence_group.size().reset_index(name="Count")

        # Get number of opinion and total words
        opinion_sentence_agg = pd.merge(opinion_sentence_agg, opinion_sentence_count, on=["Review id", "Sentence id"],
                                        how="inner")
        # Merge opinion sentence with these aggregations on review and sentence id
        opinion_sentence = pd.merge(opinion_sentence.drop(columns=["Opinion Word"]), opinion_sentence_agg,
                                    on=["Sentence id", "Review id"], how="inner")

        # Create opinion proportion column
        opinion_sentence["Opinion Proportion"] = opinion_sentence.loc[:, "Opinion Word"].div(
            opinion_sentence.loc[:, "Count"])
        # Merge back into main dataframe
        df = pd.merge(df,
                      opinion_sentence.loc[:, ["Review id", "Sentence id", "Word id", "Opinion Proportion"]],
                      on=["Review id", "Sentence id", "Word id"], how="inner")

        return df


form = pd.read_hdf("C:\\Users\\tommy\\OneDrive\\University\\Year 3\\Third Year Project\\Platform Album "
                   "Data\\new_unigram_data.h5", key="form")

ids = form.loc[form["Desired"] == 1, "Review id"].unique()

preprocess = Preprocess("C:\\Users\\tommy\\OneDrive\\University\\Year 3\\Third Year Project\\Platform Album "
                        "Data\\new_unigram_data.h5", ids)
form = pd.read_hdf("C:\\Users\\tommy\\OneDrive\\University\\Year 3\\Third Year Project\\Platform Album "
                   "Data\\new_unigram_data.h5", key="form")

sent_word = pd.merge(preprocess.format_words(), preprocess.format_sentences(),
                     on=["Artist", "Album", "Platform", "Text", "Word id", "Review id"], how="inner")
sent_word = pd.merge(sent_word, form.loc[:, ["Word id", "Review id", "Desired"]], on=["Word id", "Review id"],
                     how="inner")

# Set predictors and target
X = sent_word.drop(columns=["Desired", "Review id"])
y = sent_word.loc[:, "Desired"]

# Scaler
sc = StandardScaler()
# Classifier
clf = SVC(gamma="auto")
# Encoder
enc = OneHotEncoder()

# Fit the encoder
enc.fit(X.loc[:, ["ptag", "ntag", "Platform", "tag"]])
# Encode any categorical variables
one_hot = enc.transform(X.loc[:, ["ptag", "ntag", "Platform", "tag"]]).toarray()
# Transform the data
one_hot = pd.DataFrame(one_hot, columns=enc.get_feature_names_out())
# Replace the columns with their one-hot variants
X = pd.concat([X, one_hot], axis=1).drop(columns=["ptag", "ntag", "Text", "tag", "Platform", "Artist", "Album"])
features = X.columns
sc.fit(X)
X = sc.transform(X)

X = pd.DataFrame(X)
y_balanced = pd.concat([y.loc[y == 1], y.loc[y != 1].sample(300, random_state=0)], axis=0)
X_balanced = pd.concat([X.loc[y == 1], X.loc[y != 1].sample(300, random_state=0)], axis=0)

pd.set_option("display.max_rows", 313)
clf.fit(X_balanced, y_balanced)
print(pd.concat([sent_word.loc[y == 1], sent_word.loc[y != 1].sample(300, random_state=0)], axis=0).reset_index(
    drop=True).loc[pd.Series(clf.predict(X_balanced)).reset_index(drop=True) == 1].loc[:, "Text"])

ids_test = pd.Series([x for x in range(40, 90)])

preprocess_test = Preprocess("C:\\Users\\tommy\\OneDrive\\University\\Year 3\\Third Year Project\\Platform Album "
                             "Data\\new_unigram_data.h5", ids_test)

sent_word_test = pd.merge(preprocess_test.format_words(), preprocess_test.format_sentences(),
                     on=["Artist", "Album", "Platform", "Text", "Word id", "Review id"], how="inner")

# Set predictors and target
X_test = sent_word_test.drop(columns=["Review id"])
# Fit the encoder
enc.fit(X_test.loc[:, ["ptag", "ntag", "Platform", "tag"]])
# Encode any categorical variables
one_hot = enc.transform(X_test.loc[:, ["ptag", "ntag", "Platform", "tag"]]).toarray()
# Transform the data
one_hot = pd.DataFrame(one_hot, columns=enc.get_feature_names_out())
# Replace the columns with their one-hot variants
X_test = pd.concat([X_test, one_hot], axis=1).drop(columns=["ptag", "ntag", "Text", "tag", "Platform", "Artist", "Album"])
# Missing columns from feature list
missing_cols = [col for col in features if col not in X_test.columns]
extra_cols = [col for col in X_test.columns if col not in features]

print(missing_cols, extra_cols)

for col in missing_cols:
    X_test[col] = [0 for x in range(X_test.shape[0])]

X_test = X_test.drop(columns=extra_cols)

sc.fit(X_test)
X_test = sc.transform(X_test)

X_cols = pd.DataFrame(X).columns
X_test_cols = pd.DataFrame(X_test).columns

test_results = clf.predict(X_test)

test_results = sent_word_test.loc[test_results == 1]
print(test_results)