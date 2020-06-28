import pandas as pd
import matplotlib.pyplot as plt
import nltk
from nltk.tokenize import word_tokenize
from nltk.probability import ConditionalFreqDist
import random

df = pd.read_csv("bookdata_sample1.csv", index_col=0)
#df.head(10)
#pd.DataFrame.info(df)

df1 = df[["Author","Genre","Summary"]]
#df.head()
input_genre = input("Enter the genre you like: ")
print(input_genre)

genreDf = df1.loc[df1['Genre'].str.contains(input_genre)]

genreDf.head()
count_row = genreDf.shape[0]

summaryDf = genreDf['Summary'] 
#summaryDf.head()

summaryList = summaryDf.values
#print(summaryList[1])

cfdist = ConditionalFreqDist()
for s in summaryList:
    tokens = nltk.word_tokenize(s)
    token_length = len(tokens)
    for i in range(0,token_length-1):
        condition = tokens[i+1]
        cfdist[tokens[i]][condition] += 1

def generate_sentence(cfdist, word, num = 30):
    length = 0
    for i in range(num):
        if (word != '.'):
            print(word,end=" ")
            list_of_cdf = list(cfdist[word])[:5]
            word = random.choice(list_of_cdf)

for i in range(0,3):
    randIndex = random.randint(0, count_row)
    tokens = nltk.word_tokenize(summaryList[randIndex])
    randomWord = tokens[0]
    generate_sentence(cfdist, randomWord)