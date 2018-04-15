import sys
import os
from vectorspace import *
from preprocess import *
from ast import literal_eval
from nltk.corpus import wordnet as wn
import _pickle as pickle


def read_illness_data(filenames):
    sources = []
    for filename in filenames:
        with open(filename) as file:
            sources.append(literal_eval(file.read()))
    return sources

def get_tokens(files):
    sources = read_illness_data(files)
    tokens = {}
    for data in sources:
        for illness in data:
            if 'influenza' in illness:
                print(data[illness])
            tokens[illness] = preprocess(data[illness]['text'], 2)
            tokens[illness].extend(preprocess(data[illness]['text']))
            for symptom in data[illness]['symptoms_list']:
                tokens[illness].extend(preprocess(symptom, 2))
                tokens[illness].extend(preprocess(symptom))

    return tokens

def expand_query(tokens):
    query = ''
    for token in tokens:
        ss = wn.synsets(token)
        if len(ss):
            for syn in wn.synsets(token):
                for lemma in syn.lemma_names():
                    query += ' ' + ' '.join(lemma.split('_'))
        else:
            query += ' ' + token
    return query

def prepare_vector_space_model():
    model_filename = 'wiki_model.pkl'
    print(os.path.isfile(model_filename))
    if os.path.isfile(model_filename):
        with open(model_filename, 'rb') as infile:
            vsm = pickle.load(infile)
    else:
        vsm = VectorSpaceModel(doc_wt_scheme='tfc', query_wt_scheme='nfx')
        vsm.prepare(get_tokens(['wikipedia.txt']))
        with open(model_filename, 'wb') as outfile:
            pickle.dump(vsm, outfile, -1)

    #Merging illnesses
    get_tokens(['wikipedia.txt'])
    illness_files = ['cdc.txt', 'mayoclinic.txt']
    sources = read_illness_data(illness_files)

    merged_data = {}
    for data in sources:
        for illness in data:
            # illness_tokens = preprocess(illness, stem=False)
            # query = expand_query(illness_tokens)
            print(illness)
            query = preprocess(illness)
            results = vsm.retrieve_ranked_docs(query)
            if len(results):
                print('Query: {}; Returned: {}'.format(query, results[0]))



    return vsm


def main():
    vsm = prepare_vector_space_model()

    while True:
        query = input('Enter your query: ')
        print('Retrieving possible illnesses...')
        print(vsm.retrieve_ranked_docs(preprocess(query) + preprocess(query, 2)))

if __name__ == '__main__':
    main()
