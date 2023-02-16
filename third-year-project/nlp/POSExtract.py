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


class POSExtract:
    def __init__(self, path, ids):
        self.full_sentence = pd.read_hdf(path, key="sentence")
        self.full_sentence.loc[:, "Text"] = self.full_sentence.loc[:, "Text"].apply(ast.literal_eval)
        self.full_form = pd.read_hdf(path, key="form")
        self.ids = set(ids.tolist())

    @staticmethod
    def to_lower(self, df, col):
        df.loc[:, col] = df.loc[:, col].astype(str).apply(lambda x: x.lower())
        return df

    @staticmethod
    def to_lower_list(self, df, col):
        df.loc[:, col] = df.loc[:, col].apply(lambda x: [word.lower() for word in x])
        return df

    def get_desired_reviews(self, df):
        return df.loc[df.loc[:, "Review id"].apply(lambda x: x in self.ids)]

    def get_candidates(self):
        # Filter by desired words
        text = self.full_sentence.copy()
        text = self.get_desired_reviews(text)

        # Getting sentence ids
        text = text.explode("Text")
        text["Sentence id"] = text.groupby(["Review id"]).cumcount()

        # Explode to the word level
        text = text.explode("Text")
        text = self.get_candidate_labels(text)

        return text

    def get_candidate_labels(self, text):

        # Join the sentences together with whitespace
        text = text.groupby(["Review id", "Sentence id"]).agg({"Text": " ".join})
        # Initiate stanza objects
        nlp_c = stanza.Pipeline(lang='en', processors='pos,constituency,tokenize,mwt', tokenize_pretokenized=True)
        nlp_d = stanza.Pipeline(lang='en', processors='pos,depparse,lemma,tokenize,mwt', tokenize_pretokenized=True)
        text = text.apply(self.analyse_dependencies, nlp_c, nlp_d, axis=1)

        return text

    def analyse_dependencies(self, sentence, constituency_parse, dependency_parse):

        # Pass into constituency object
        constituency = constituency_parse(sentence.loc["Text"])
        # Get past tense labels for each sentence
        labels = self.get_phrases(constituency.sentences[0].constituency)
        # Get modified verbs
        modified_verbs = self.get_modified_verbs(dependency_parse.sentences[0].dependencies)

    def get_phrases(self, tree, tensed_trees=None):

        if tensed_trees is None:
            tensed_trees = []
        if tree.is_preterminal():
            tensed_trees.append(1)
        elif tree.label == "VP" and tree.children[0].label == "VBD":
            tensed_trees = tensed_trees + [0 for x in range(len(tree.leaf_labels()))]
        else:
            for child in tree.children:
                tensed_trees = self.get_phrases(child, tensed_trees)

        return tensed_trees

    def get_modified_verbs(self, dependencies):

        for dep in dependencies:
            if dep[0]["xpos"] in ["NNS", "NN", "VB"]


