#-*- coding: utf-8 -*-
def get_texts_scores(fname):
    with open(fname, encoding='utf-8') as f:
        docs = [doc.lower().replace('\n', '').split('\t') for doc in f]
        docs = [doc for doc in docs if len(doc) == 2]

        if not docs:
            return [], []

        texts, scores = zip(*docs)
        return list(texts), list(scores)


# La La Land
fname = './data/134963.txt'
texts, scores = get_texts_scores(fname)

from krwordrank.word import KRWordRank
from krwordrank.hangle import normalize

with open('./data/134963_norm.txt', 'w', encoding='utf-8') as f:
    for text, score in zip(texts, scores):
        text = normalize(text, english=True, number=True)
        f.write('%s\t%s\n' % (text, str(score)))

# La La Land
fname = './data/134963_norm.txt'
texts, scores = get_texts_scores(fname)

min_count = 5   # 단어의 최소 출현 빈도수 (그래프 생성 시)
max_length = 10 # 단어의 최대 길이
wordrank_extractor = KRWordRank(min_count, max_length)

beta = 0.85    # PageRank의 decaying factor beta
max_iter = 10
verbose = True
keywords, rank, graph = wordrank_extractor.extract(texts, beta, max_iter, verbose)

for word, r in sorted(keywords.items(), key=lambda x:x[1], reverse=True)[:30]:
    print('%8s:\t%.4f' % (word, r))

fnames = ['./data/91031.txt', './data/99714.txt']
for fname in fnames:
    texts, scores = get_texts_scores(fname)
    with open(fname.replace('.txt', '_norm.txt'), 'w', encoding='utf-8') as f:
        for text, score in zip(texts, scores):
            text = normalize(text, english=True, number=True)
            f.write('%s\t%s\n' % (text, str(score)))

#fnames = ['./data/91031.txt', './data/99714.txt']
#for fname in fnames:
#    texts, scores = get_texts_scores(fname)
#    with open(fname.replace('.txt', '_norm.txt'), 'w', encoding='utf-8') as f:
#        for text, score in zip(texts, scores):
#            text = normalize(text, english=True, number=True)
#            f.write('%s\t%s\n' % (text, str(score)))


top_keywords = []
fnames = ['./data/134963_norm.txt', './data/91031_norm.txt', './data/99714_norm.txt']
for fname in fnames:
    texts, scores = get_texts_scores(fname)
    wordrank_extractor = KRWordRank(min_count, max_length)
    keywords, rank, graph = wordrank_extractor.extract(texts, beta, max_iter, verbose=False)
    top_keywords.append(sorted(keywords.items(), key=lambda x:x[1], reverse=True)[:100])


movie_names = ['라라랜드', '신세계', '엑스맨']
for k in range(100):
    message = '  --  '.join(['%8s (%.3f)' % (top_keywords[i][k][0], top_keywords[i][k][1]) for i in range(3)])
    print(message)


keyword_counter = {}
for keywords in top_keywords:
    words, ranks = zip(*keywords)
    for word in words:
        keyword_counter[word] = keyword_counter.get(word, 0) + 1

common_keywords = {word for word, count in keyword_counter.items() if count == 3}
len(common_keywords)


