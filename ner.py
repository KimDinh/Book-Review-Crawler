from langdetect import detect
from vncorenlp import VnCoreNLP
import json

names = set()

# get a review/comment and add words that are names of people and places to the set names
def get_name_and_place(text):
    try:
        # the text's language is not Vietnamese
        if detect(text[:min(len(text), 100)]) != 'vi':
            return
    except:
        return
    text_ner = annotator.ner(text.replace(".", ". "))
    for sentence in text_ner:
        for word in sentence:
            # check NER tag for person or location
            if word[1] == "B-PER" or word[1] == "B-LOC":
                names.add(word[0])

vncorenlp_path = "/usr/local/lib/python3.7/site-packages/vncorenlp/bin/VnCoreNLPServer.jar"
annotator = VnCoreNLP(port=9000)

# Read reviews from file
f = open('bookreviews.json', 'r')
books = json.loads(f.read())
f.close()

# iterate the books and get names from reviews/comments
for book in books:
    reviews = book['Review']
    if reviews is None:
        continue
    for review in reviews:
        content = review['Content']
        if content is None:
            continue
        get_name_and_place(content)
        comments = review['Comment']
        if comments is None:
            continue
        for comment in comments:
            get_name_and_place(comment)

annotator.close()

# write names to file
res = open('name.txt', 'w')
for name in names:
    res.write(name + "\n")
res.close()


