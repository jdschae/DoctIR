import sys
import os
from vectorspace import *
from preprocess import *
from ast import literal_eval
from nltk.corpus import wordnet
import _pickle as pickle


def read_illness_data(filenames):
    sources = []
    for filename in filenames:
        with open(filename) as file:
            sources.append(literal_eval(file.read()))
    return sources


def prepare_vector_space_model():
    illness_files = ['wikipedia.txt']
    sources = read_illness_data(illness_files)
    vsm = VectorSpaceModel(doc_wt_scheme='tfc', query_wt_scheme='nfx')
    tokens = {}
    for data in sources:
        for illness in data:
            if len(data[illness]['symptoms_list']):
                for symptom in data[illness]['symptoms_list']:
                    tokens[illness] = preprocess(symptom, 2)
                    tokens[illness].extend(preprocess(symptom))
            else:
                tokens[illness] = preprocess(data[illness]['text'], 2)
                tokens[illness].extend(preprocess(data[illness]['text']))


    vsm.prepare(tokens)
    return vsm


def main():
    model_filename = 'wiki_model.pkl'
    print(os.path.isfile(model_filename))
    if os.path.isfile(model_filename):
        with open(model_filename, 'rb') as infile:
            vsm = pickle.load(infile)
    else:
        vsm = prepare_vector_space_model()
        with open(model_filename, 'wb') as outfile:
            pickle.dump(vsm, outfile, -1)

    while True:
        query = input('Enter your query: ')
        print('Retrieving possible illnesses...')
        print(vsm.retrieve_ranked_docs(preprocess(query) + preprocess(query, 2)))

if __name__ == '__main__':
    main()
