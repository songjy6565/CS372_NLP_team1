import nltk,re,pprint
from nltk import word_tokenize, FreqDist
from urllib import request
from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

url = "https://www.goodreads.com/book/show/2767052.The_Hunger_Games"
html = request.urlopen(url).read().decode('utf8')
sum_idx = html.find("descriptionContainer")
sum_start_1 = html[sum_idx:].find("display:none")
sum_start_2 = html[sum_idx+sum_start_1:].find(">")
sum_end = html[sum_idx+sum_start_1+sum_start_2:].find("</span>")
sum_text = html[sum_idx+sum_start_1+sum_start_2+1:sum_idx+sum_start_1+sum_start_2+sum_end]
#remove braces
rel_idx= html.find("relatedWorks")
rel_start = html[rel_idx:].find("<ul>")
rel_end = html[rel_idx+rel_start:].find("</ul>")
rel_text = html[rel_idx+rel_start+4:rel_idx+rel_start+4+rel_end]
rel_list = []
idx = 0
idx_add = rel_text[idx:].find("<li")
while idx_add > 0 :
	idx += idx_add
	id_start = rel_text[idx:].find("bookCover_")
	idx += id_start
	id_end = rel_text[idx:].find('>')
	rel_list.append(rel_text[idx+10:idx+id_end-1])
	idx += id_end
	idx_add = rel_text[idx:].find("<li")

print(re.sub(r'<[^>]*>',' ', sum_text))
print(rel_list)
temp_summary_from_corpus = re.sub(r'<[^>]*>',' ', sum_text)

temp_title_from_corpus = "The Hunger Game"
temp_rating_from_corpus = 4.34
invalid = ['','-','_',':',',','.','the']
word_count = {}
sum_of_rating = {}
#pre dictionary with some info (ex.)genre, summary content, rating,  and certain title form
for e in temp_title_from_corpus.split(' '):
  if e.lower() not in invalid:
    temp = e.lower()
    if temp not in word_count:
      word_count[temp] = 1
      sum_of_rating[temp] = temp_rating_from_corpus
    else:
      word_count[temp] += 1
      sum_of_rating[temp] += temp_rating_from_corpus

summary_tagged = []
n = WordNetLemmatizer()
for e in temp_summary_from_corpus.split(' '):
  if e not in invalid:
    token = word_tokenize(e.lower())
    tag = pos_tag(token)[0][1]
    if tag == 'NNS':
      summary_tagged.append((n.lemmatize(token[0],pos='n'), tag))
    else:
      summary_tagged.append((token[0], tag))

freq1 = []
freq2 = []
for i in range(len(summary_tagged)-1):
  cur = summary_tagged[i]
  nex = summary_tagged[i+1]
  if cur[1] == 'NN' and nex[1] == 'NNS':
    freq1.append(cur[0])
    freq2.append(nex[0])

freq1 = FreqDist(freq1).most_common()
freq2 = FreqDist(freq2).most_common()
#frequent word in summary has more probability to be put into the title

result_name = 'The '
# The + NN + NN form result (temp example)
for v, c in freq1:
  if v not in word_count:
    continue
  else:
    if sum_of_rating[v]/word_count[v] >= 3.0: # proper coefficient for rating. (experiment result value)
      result_name += v + ' '
      break

for v2, c2 in freq2:
  if v2 not in word_count:
    continue
  else:
    if sum_of_rating[v2]/word_count[v2] >= 3.0:
      result_name += v2
      break
print(result_name)