import pandas as pd
import numpy as np
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from nltk.tokenize.nist import NISTTokenizer
import ast
from sklearn.svm import SVC
from sklearn.naive_bayes import ComplementNB, GaussianNB, BernoulliNB
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from nltk.stem import WordNetLemmatizer
from nltk.corpus import opinion_lexicon
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import stanza


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
        # Get relative word positions within review
        text = self.get_review_location(text)

        return text

    def get_review_location(self, df):
        # Get the number of words in each review
        max_id = df.groupby(["Review id"])["Word id"].transform(np.max)
        # Divide the word id by the number of words to get a proportional position
        df["Review Location"] = df.loc[:, "Word id"].add(1).div(max_id.add(1))

        return df

    def format_sentences(self):

        # Get the desired sentence text
        text = self.get_desired_reviews(self.full_sentence)
        # Preprocess the sentence data
        text = self.preprocess_sentence(text)

        # Get opinion word proportions by sentence
        text = self.get_opinion_frequency(text)
        # Get metric for how far through the sentence each word is
        text = self.get_sentence_location(text)

        # Classify whether each sentence is past tense or not
        # text = self.get_sentence_tense(text)

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
        text = self.full_text.copy()

        # Lower case and remove stopwords
        text = self.to_lower_list(text, "Text")
        text = self.remove_stop_list(text, "Text")

        # Save a copy and get only desired reviews
        full_text = text.copy()
        text = self.get_desired_reviews(text)
        # Get all text for every album
        text = text.loc[:, ["Album", "Text"]].groupby(["Album"]).agg({"Text": self.join_list})

        lemmatiser = WordNetLemmatizer()
        # Lemmatise every word for each album
        text.loc[:, "Text"] = text.loc[:, "Text"].apply(lambda x: [lemmatiser.lemmatize(word) for word in x])

        # Get text for all albums
        full_text = full_text.loc[:, ["Album", "Text"]].groupby(["Album"]).agg({"Text": self.join_list})
        full_text.loc[:, "Text"] = full_text.loc[:, "Text"].apply(
            lambda x: set([lemmatiser.lemmatize(word) for word in set(x)]))

        counts = {}
        document_counts = {}
        documents = full_text.shape[0]

        # For each album get all the relevant text Count the occurrences of each word and divide by the total number
        # of word to get the relative frequency of each lemmatised word
        for album in text.index:
            album_text = text.loc[album, "Text"]
            counts[album] = pd.value_counts(np.array(album_text)) / len(album_text)

            document_counts[album] = {}
            for word in full_text.loc[album, "Text"]:
                document_counts[album][word] = documents / full_text.loc[:, "Text"].apply(lambda x: word in x).sum()

        df["Platform TFIDF"] = df.apply(
            lambda x: counts[x.loc["Album"]][lemmatiser.lemmatize(x.loc["Text"])] *
                      document_counts[x.loc["Album"]][lemmatiser.lemmatize(x.loc["Text"])], axis=1)

        return df

    def join_list(self, text):
        output = []

        for platform_text in text.tolist():
            output = output + platform_text

        return output

    def get_opinion_frequency(self, df):
        # Make this a set or it takes forever
        opinion_words = set(opinion_lexicon.words())

        df["Opinion Word"] = df.loc[:, "Text"].isin(opinion_words).astype(int)

        df["Opinion Proportion"] = df.groupby(["Review id", "Sentence id"])["Opinion Word"].transform(
            lambda x: x.sum() / x.count()
        )

        return df

    def get_sentence_location(self, df):
        # Get number of words in each sentence
        num_words = df.groupby(["Review id", "Sentence id"])["Word_Sentence id"].transform(np.max)
        # Divide sentence word id by max sentence word id
        df["Sentence Location"] = df.loc[:, "Word_Sentence id"].add(1).div(num_words.add(1))

        return df

    def get_sentence_tense(self, df):
        # Aggregate the text into sentences
        text = self.full_sentence.copy()
        text = self.get_desired_reviews(text)
        text = text.explode("Text")
        text["Sentence id"] = text.groupby("Review id").cumcount()
        text.loc[:, "Text"] = text.loc[:, "Text"].apply(lambda x: " ".join(x))
        # Set up stanza object
        nlp = stanza.Pipeline(lang='en', processors='tokenize,pos,constituency', tokenize_pretokenized=True)

        # Get whether each sentence has a root past tense verb phrase or not
        text["Past Tense"] = text.loc[:, "Text"].apply(lambda x: self.get_root_tense(x, nlp))
        # Set the column accordingly
        df = pd.merge(text.loc[:, ["Sentence id", "Review id", "Past Tense"]],
                      df, on=["Sentence id", "Review id"], how="inner")

        return df

    def get_root_tense(self, sentence, nlp):
        doc = nlp(sentence)
        queue = [doc.sentences[0].constituency.children[0]]

        while queue:
            node = queue.pop(0)
            if node.label == "VP":
                if node.children[0].label == "VBD" or node.children[0].label == "VBN":
                    return 1
                else:
                    return 0
            else:
                for child in node.children:
                    queue.append(child)

        return 0

    def format_text(self):
        word_sentence = pd.merge(self.format_words(), self.format_sentences(),
                                 on=["Artist", "Album", "Platform", "Text", "Word id", "Review id"],
                                 how="inner")
        # Get the proportion of certain part of speech tags within sentences
        word_sentence = self.get_descriptive_frequency(word_sentence)

        return word_sentence

    def get_descriptive_frequency(self, df):
        descriptive_frequency = df.copy()
        df["Descriptive Proportion"] = \
            descriptive_frequency.loc[:, ["Review id", "Sentence id", "tag"]].groupby(
                ["Review id", "Sentence id"]).transform(
                lambda x: x.isin(["JJ", "JJR", "RB", "RBR", "RBS", "VBG", "VBZ"]).sum() / x.count()
            )

        return df


form = pd.read_hdf("C:\\Users\\tommy\\OneDrive\\University\\Year 3\\Third Year Project\\Platform Album "
                   "Data\\new_unigram_data.h5", key="reduced_music_form")

ids = form.loc[form["Desired"] == 1, "Review id"].unique()

preprocess = Preprocess("C:\\Users\\tommy\\OneDrive\\University\\Year 3\\Third Year Project\\Platform Album "
                        "Data\\new_unigram_data.h5", ids)
form = pd.read_hdf("C:\\Users\\tommy\\OneDrive\\University\\Year 3\\Third Year Project\\Platform Album "
                   "Data\\new_unigram_data.h5", key="reduced_music_form")

sent_word = preprocess.format_text()
sent_word = pd.merge(sent_word, form.loc[:, ["Word id", "Review id", "Desired"]], on=["Word id", "Review id"],
                     how="inner")

# Set predictors and target
X = sent_word.drop(columns=["Desired", "Review id"])
y = sent_word.loc[:, "Desired"]

# Scaler
sc = StandardScaler()
# Classifier
clf = ComplementNB()
# Encoder
enc = OneHotEncoder()

# Fit the encoder
enc.fit(X.loc[:, ["ptag", "ntag", "Platform", "tag"]])
# Encode any categorical variables
one_hot = enc.transform(X.loc[:, ["ptag", "ntag", "Platform", "tag"]]).toarray()
# Transform the data
one_hot = pd.DataFrame(one_hot, columns=enc.get_feature_names_out())
# Replace the columns with their one-hot variants
X = pd.concat([X, one_hot], axis=1).drop(columns=["ptag", "ntag", "Text", "tag", "Platform", "Artist", "Album",
                                                  "Word id", "Word_Sentence id", "Sentence id"])
features = X.columns
# sc.fit(X)
# X = sc.transform(X)

# X = pd.DataFrame(X)
# y_balanced = pd.concat([y.loc[y == 1], y.loc[y != 1].sample(300, random_state=0)], axis=0)
# X_balanced = pd.concat([X.loc[y == 1], X.loc[y != 1].sample(300, random_state=0)], axis=0)

# clf.fit(X_balanced, y_balanced)

albums = form.loc[form["Review id"].isin([99, 100, 101]), "Album"].unique()
ids_test = form.loc[form["Album"].isin(["sour"]), "Review id"].unique()

preprocess_test = Preprocess("C:\\Users\\tommy\\OneDrive\\University\\Year 3\\Third Year Project\\Platform Album "
                             "Data\\new_unigram_data.h5", ids_test)

sent_word_test = preprocess_test.format_text()

# Set predictors and target
X_test = sent_word_test.drop(columns=["Review id"])
# Fit the encoder
enc.fit(X_test.loc[:, ["ptag", "ntag", "Platform", "tag"]])
# Encode any categorical variables
one_hot = enc.transform(X_test.loc[:, ["ptag", "ntag", "Platform", "tag"]]).toarray()
# Transform the data
one_hot = pd.DataFrame(one_hot, columns=enc.get_feature_names_out())
# Replace the columns with their one-hot variants
X_test = pd.concat([X_test, one_hot], axis=1).drop(
    columns=["ptag", "ntag", "Text", "tag", "Platform", "Artist", "Album", "Word id", "Word_Sentence id",
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

test_results = sent_word_test.join(pd.DataFrame(test_results, columns=["neg_prob", "pos_prob"])).sort_values(
    by=["pos_prob"], ascending=False)

first_dict = {}

for k, v in zip(test_results.loc[:, "Text"], test_results.loc[:, "pos_prob"]):
    first_dict[k] = v

cloud = WordCloud().generate_from_frequencies(first_dict)
plt.imshow(cloud)
plt.show()

test_results.to_csv("C:\\Users\\tommy\\OneDrive\\University\\Year 3\\Third Year Project\\Platform Album "
                    "Data\\test_results.csv")
