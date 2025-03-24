import pandas as pd
import nltk
from nltk import word_tokenize
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer

# Download the dataset from Kaggle (source: https://www.kaggle.com/datasets/abhi8923shriv/sentiment-analysis-dataset/data)
test_path = "../../data/convertedcsv/Kagglehub_Reviews/test.csv"
train_path = "../../data/convertedcsv/Kagglehub_Reviews/train.csv"
test_df = pd.read_csv(test_path, encoding='Windows-1252')
train_df = pd.read_csv(train_path, encoding='Windows-1252')

# PRE-PROCESSING
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def nltk_pos_tagger(nltk_tag):
    if nltk_tag.startswith('J'):
        return wordnet.ADJ
    elif nltk_tag.startswith('V'):
        return wordnet.VERB
    elif nltk_tag.startswith('R'):
        return wordnet.ADV
    elif nltk_tag.startswith('N'):
        return wordnet.NOUN
    else:
        return wordnet.NOUN

def pre_process(data):
    tokens = word_tokenize(data["text"])
    tokens = [word for word in tokens if word not in stop_words]
    tokens = [lemmatizer.lemmatize(word, nltk_pos_tagger(tag)) for word, tag in nltk.pos_tag(tokens)]
    return {"tokens": tokens, "text": data["text"], "label": data["label"]}

print(train_df.columns)


