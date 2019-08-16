"""
    This is cofig file all constants are defined in this file.

    STOPWORDS = stopwords to remove from data
    CONTRACTION_CHANGES = it will resolve all these contractions.
    JUNK_WORDS = it will remove all JUNK words from user query.
"""
from nltk.corpus import stopwords

STOPWORDS = stopwords.words('english')

CONTRACTION_CHANGES = [(r"won\'t", "will not"), (r"can\'t", "can not"), (r"n\'t", " not"),
                       (r"\'re", " are"), (r"\'s", " is"), (r"\'d", " would"),
                       (r"\'ll", " will"), (r"\'t", " not"), (r"\'ve", " have"), (r"\'m", " am")]

JUNK_WORDS = ["cousin", "grand", "mother", "father", "grandfather", "grandmother", "friend", \
                "uncle", "aunt", "consult", "help", "helps", "need", "needs", "issue", "issues", \
                "problems", "suggestions", "patient", "patients", "case", "other", "are", "i", \
                "service", "difference", "research"]
