import re

import pandas as pd
import numpy as np
import nltk
from nltk.corpus import stopwords
import ast
from nltk.stem import WordNetLemmatizer
from nltk.corpus import opinion_lexicon
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import stanza
from sklearn.preprocessing import OneHotEncoder
import keywords


class UnigramPreprocess:
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
        text["pptag"] = self.get_offset(text, "tag", 2)
        text["nntag"] = self.get_offset(text, "tag", -2)

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

        # Classify whether each sentence is past tense or not
        print("Getting tenses...")
        text = self.get_sentence_tense(text)
        print("Tenses retrieved")
        print("Getting instrument subjects...")
        # Get whether the adjective describes an instrument word
        text = self.get_instrument_subject(text)
        print("Instrument subjects retrieved")
        # Reset index for remaining operations
        # The above two require the indices to align with stopwords also
        text = text.reset_index(drop=True)

        # Get opinion word proportions by sentence
        text = self.get_opinion_frequency(text)
        # Get metric for how far through the sentence each word is
        text = self.get_sentence_location(text)

        return text

    def preprocess_sentence(self, text):
        # Get sentence id for each sentence
        text = text.explode("Text")
        text["Sentence id"] = text.groupby(["Review id"]).cumcount()

        # Get word id and word within sentence id
        text = text.explode("Text")
        text["Word_Sentence id"] = text.groupby(["Review id", "Sentence id"]).cumcount()
        text["Word id"] = text.groupby(["Review id"]).cumcount()
        text = text.reset_index(drop=True)

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
        text = text.reset_index(drop=True)
        text["Sentence id"] = text.groupby("Review id").cumcount()
        text.loc[:, "Text"] = text.loc[:, "Text"].apply(lambda x: " ".join(x))
        # Set up stanza object
        nlp = stanza.Pipeline(lang='en', processors='tokenize,pos,constituency', tokenize_pretokenized=True)

        # Get whether each sentence has a root past tense verb phrase or not
        tense_labels = text.loc[:, "Text"].apply(lambda x: self.get_tense_labels(x, nlp))
        # Set the column accordingly
        df["Past Tense"] = tense_labels.explode().reset_index(drop=True)

        return df

    def get_tense_labels(self, sentence, nlp):
        doc = nlp(sentence)
        queue = [doc.sentences[0].constituency.children[0]]
        labels = []

        while queue:
            node = queue.pop(0)
            if node.is_preterminal():
                labels.append(0)
            elif node.label == "VP":
                if node.children[0].label == "VBD":
                    labels = labels + [1 for _ in range(len(node.leaf_labels()))]
                    continue
            for child in node.children:
                queue.insert(0, child)

        return labels

    def get_instrument_subject(self, df):
        # Aggregate the text into sentences
        text = self.full_sentence.copy()
        text = self.get_desired_reviews(text)
        text = text.explode("Text")
        text = text.reset_index(drop=True)
        text["Sentence id"] = text.groupby("Review id").cumcount()
        text.loc[:, "Text"] = text.loc[:, "Text"].apply(lambda x: " ".join(x))
        # Set up stanza object
        nlp = stanza.Pipeline(lang='en', processors='pos,depparse,lemma,tokenize,mwt', tokenize_pretokenized=True)

        # Get whether the object of the word is an instrument or not
        instrument_labels = text.loc[:, "Text"].apply(lambda x: self.get_instrument_labels(x, nlp))
        # Set the column accordingly
        df["Instrument Subject"] = instrument_labels.explode().reset_index(drop=True)

        return df

    def get_instrument_labels(self, sentence, nlp):

        instrument_words = keywords.get_instrument_words()
        sentence = nlp(sentence)
        deps = sentence.sentences[0].dependencies
        labels = [0 for _ in range(len(sentence.sentences[0].words))]

        for dep in deps:
            if dep[1] == "amod":
                adj_id = dep[2].id
                subj_id = dep[0].id
                subject_text = [dep[0].text]

                for dep in deps:
                    if dep[1] == "compound" and dep[0].id == subj_id:
                        subject_text.append(dep[2].text)

                if any([x in subject_text for x in instrument_words]):
                    labels[adj_id - 1] = 1

        return labels


    def format_text(self):
        word_sentence = pd.merge(self.format_words(), self.format_sentences(),
                                 on=["Artist", "Album", "Platform", "Text", "Word id", "Review id"],
                                 how="inner")
        # Get the proportion of certain part of speech tags within sentences
        word_sentence = self.get_descriptive_frequency(word_sentence)
        # Get whether each sentence references the artist
        word_sentence = self.get_contains_artist(word_sentence)
        # Get whether each sentence references the album title
        word_sentence = self.get_contains_title(word_sentence)

        return word_sentence

    def get_descriptive_frequency(self, df):
        descriptive_frequency = df.copy()
        df["Descriptive Proportion"] = \
            descriptive_frequency.loc[:, ["Review id", "Sentence id", "tag"]].groupby(
                ["Review id", "Sentence id"]).transform(
                lambda x: x.isin(["JJ", "JJR", "RB", "RBR", "RBS", "VBG", "VBZ"]).sum() / x.count()
            )

        return df

    def get_contains_artist(self, df):
        contains_artist = df.groupby(["Review id", "Sentence id"]).agg(
            {"Artist": "first", "Text": list, "tag": list}
        ).reset_index()
        artists = pd.DataFrame(df.loc[:, "Artist"].unique(), columns=["Artist"])
        artists["Variations"] = artists.loc[:, "Artist"].apply(
            lambda x: {variation for variation in x.split(" ") }
            .union({variation + "'s" if variation[-1] != "s" else variation + "'" for variation in x.split(" ")})
            .union({x})
        )
        contains_artist["Contains Artist"] = contains_artist.apply(
            lambda x: any([word in artists.loc[artists["Artist"] == x.loc["Artist"], "Variations"].item()
                           and tag == "NNP"
                           for word, tag in zip(x["Text"], x["tag"])]),
            axis=1
        ).astype(int)

        df = pd.merge(df, contains_artist.drop(columns=["Text", "tag", "Artist"]), on=["Review id", "Sentence id"],
                      how="inner")

        return df

    def get_contains_title(self, df):
        contains_title = df.groupby(["Review id", "Sentence id"]).agg(
            {"Text": " ".join, "Album": "first"}
        ).reset_index()
        contains_title["Contains Title"] = contains_title.apply(
            lambda x: x.loc["Album"] in x.loc["Text"],
            axis=1
        ).astype(int)

        df = pd.merge(df, contains_title.drop(columns=["Album", "Text"]), on=["Review id", "Sentence id"],
                      how="inner")

        return df

