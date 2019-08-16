"""
    This code will predict the Speciality from the description given to us.
"""
import re

import pandas as pd
import numpy as np

from nltk import word_tokenize, pos_tag
from gensim.utils import lemmatize

from flask import Flask, request, jsonify

from config import STOPWORDS, CONTRACTION_CHANGES, JUNK_WORDS

APP = Flask(__name__)

# Read the data from excel or csv whatever format we stored.
CURO_DATA = pd.DataFrame()
try:
    CURO_DATA = pd.read_excel("health_patent_work.xlsx", sheet_name=0)
except BaseException:
    CURO_DATA = pd.read_csv("health_patent_work.csv")

class CURO():
    """
        This class contains several methods which is useful to process the query.
    """
    @classmethod
    def contraction(cls, phrase):
        """
            Contraction will change words in according
        """
        for old, new in CONTRACTION_CHANGES:
            phrase = phrase.replace(old, new)
        return phrase

    @classmethod
    def preprocess_data(cls):
        """
            It will process te ground data on which we are going to test and return te result.
        """
        preprocessed_description, preprocessed_speciality = [], []

        for _, sentence in enumerate(CURO_DATA["Description"].values):
            # We want those words here which is free from contraction so that not loose meaning
            sentence = CURO().contraction(str(sentence))
            # Eliminate those words which are with numbers
            sentence = re.sub(r"\S*\d\S*", "", sentence).strip()
            # Eliminate all numerics and special characters
            sentence = re.sub('[^A-Za-z]+', " ", sentence)
            # Remove all stopwords from each sentence, convert to lowercase
            sentence = " ".join(e.lower() for e in str(sentence).split() if e.lower() \
                                not in STOPWORDS)
            # Lemmatize all words
            sentence = " ".join([word.decode('utf-8').split('/')[0] for word in \
                                lemmatize(sentence)])
            preprocessed_description.append(sentence.strip())

        for _, sentence in enumerate(CURO_DATA["Speciality"].values):
            # Eliminate all numerics and special characters
            sentence = sentence.replace("@#$", "") if not sentence.split("@#$")[1] \
                                                    else sentence.replace("@#$", " => ")
            # Remove all stopwords from each sentence, convert to lowercase
            sentence = " ".join(e.lower() for e in str(sentence).split())
            preprocessed_speciality.append(sentence.strip())

        CURO_DATA["Preprocessed_Description"] = preprocessed_description
        CURO_DATA["Preprocessed_Speciality"] = preprocessed_speciality

    @staticmethod
    @APP.route("/curo/chat", methods=["POST"])
    def query_data():
        """
            After you call to this API i.e. http://<IP ADDRESS>/curo/chat
            you will get answer. Input to this is user query.
        """
        query = request.json["query"].lower().replace("/", " ").replace("-", " ")

        # Collect all POS tags using nltk
        pos_list = pos_tag(word_tokenize(query))
        kw_list = []

        try:
            # Collect all Adjective and Noun phrases
            kw_list = [str(lemmatize(str(item[0]))[0].decode("utf-8")).split("/")[0] \
                        for item in pos_list \
                        if item[1] in ['NN', 'NNS', 'JJ'] and item[0] not in JUNK_WORDS]
            # Check lenth of list if its empty then possibility is that there are
            # several verb and gerunds are present.
            if not kw_list:
                kw_list = [str(lemmatize(str(item[0]))[0].decode("utf-8")).split("/")[0] \
                            for item in pos_list \
                            if item[1] in ['VBN', 'VBG'] and item[0] not in JUNK_WORDS]
            else:
                kw_list = [str(lemmatize(str(item[0]))[0].decode("utf-8")).split("/")[0] \
                            for item in pos_list \
                            if item[1] in ['NN', 'NNS', 'JJ', 'VBG'] and item[0] not in JUNK_WORDS]
        except BaseException:
            pass

        # Check intersection of each document with query and collect score of query
        array = np.array([len(set(check.split()) & set(kw_list)) \
                            for _, check in enumerate(CURO_DATA["Preprocessed_Description"])])

        # This dictionary contains rank wise indexes in a list later we are maping to values.
        curo_dict = {}
        for index in range(len(set(kw_list)), 0, -1):
            if list(np.where(array == index)[0]):
                curo_dict["rank {}".format(len(set(kw_list))-index+1)] = \
                                    list(np.where(array == index)[0])

        # Using these variables we are extracting maximum 5 results
        counter = 0
        flag = False
        display_data_index = []

        # Below snippet will store those index strings in one list
        for value in list(curo_dict.values()):
            for val in value:
                try:
                    if counter == 5:
                        flag = True
                        break
                    display_data_index.append(val)
                    counter = counter + 1
                except BaseException:
                    flag = True
                    break
            if flag:
                break

        # Output contains comma separated results
        output = ", ".join(CURO_DATA["Preprocessed_Speciality"][display_data_index])

        # Returning json
        if output == "":
            return jsonify({"message":"Please re-phrase your question " \
                            "with more specific keywords..."})

        return jsonify({"{0}".format(idx+1) : check.strip().title() \
                        for idx, check in enumerate(output.split(","))})

if __name__ == "__main__":
    CURO().preprocess_data()
    APP.run(debug=True, port=12000)
