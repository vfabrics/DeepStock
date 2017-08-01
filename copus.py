import codecs

def read_data(filename):
    with codecs.open(filename, encoding='utf-8', mode='r') as f:
        data = [line.split('\t') for line in f.read().splitlines()]
        data = data[1:]   # header 제외
    return data

train_data = read_data('./ratings_train.txt')


from konlpy.tag import Twitter
tagger = Twitter()

def tokenize(doc):
    return ['/'.join(t) for t in tagger.pos(doc, norm=True, stem=True)]

train_docs = [row[1] for row in train_data]
sentences = [tokenize(d) for d in train_docs]

from gensim.models import word2vec
model = word2vec.Word2Vec(sentences)
model.init_sims(replace=True)


model.similarity(*tokenize(u'악당 영웅'))
from konlpy.utils import pprint
pprint(model.most_similar(positive=tokenize(u'배우 남자'), negative=tokenize(u'여배우'), topn=1))
