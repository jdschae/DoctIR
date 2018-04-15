import sys
import os
from vectorspace import *
from preprocess import *
from ast import literal_eval
from nltk.corpus import wordnet as wn
import dill
from collections import defaultdict

def read_illness_data(filenames):
    sources = []
    for filename in filenames:
        with open(filename) as file:
            sources.append(literal_eval(file.read()))
    return sources

def get_tokens(files):
    sources = read_illness_data(files)
    text_tokens = defaultdict(list)
    symptoms_tokens = defaultdict(list)
    for data in sources:
        for illness in data:
            if len(data[illness]['symptoms_list']):
                for symptom in data[illness]['symptoms_list']:
                    symptoms_tokens[illness].extend(preprocess(symptom))
                    symptoms_tokens[illness].extend(preprocess(symptom, 2))
            else:
                text_tokens[illness].extend(preprocess(data[illness]['text']))
                text_tokens[illness].extend(preprocess(data[illness]['text'], 2))

    return text_tokens, symptoms_tokens

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
    combined_model = 'model.pkl'
    if os.path.isfile(combined_model):
        print('Loading combined vector space model...')
        with open(combined_model, 'rb') as infile:
            return dill.load(infile)
        print('Done!')

    wiki_model = 'wiki_model.pkl'
    text_tokens, merged_symptoms = get_tokens(['wikipedia.txt'])
    if os.path.isfile(wiki_model):
        print('Loading Wikipedia vector space model...')
        with open(wiki_model, 'rb') as infile:
            vsm = dill.load(infile)
    else:
        print('Creating Wikipedia text vector space model...')
        vsm = VectorSpaceModel(doc_wt_scheme='tfc', query_wt_scheme='nfx')
        vsm.prepare(text_tokens, 1.)
        print('Dumping...')
        with open(wiki_model, 'wb') as outfile:
            dill.dump(vsm, outfile)
    print('Done!')
    print('Creating combined vector space model...')

    #Merging illnesses
    illness_files = ['cdc.txt', 'mayoclinic.txt']
    sources = read_illness_data(illness_files)

    merged_text = defaultdict(list)
    for data in sources:
        for illness in data:
            query = preprocess(illness) + preprocess(illness, 2)
            results = vsm.retrieve_ranked_docs(query)
            if len(results):
                normed_illness = results[0][0]
            else:
                normed_illness = illness
            print('Actual illness: {}'.format(illness))
            print('Normed illness: {}'.format(normed_illness))
            if len(data[illness]['symptoms_list']):
                for symptom in data[illness]['symptoms_list']:
                    merged_symptoms[normed_illness].extend(preprocess(symptom))
                    merged_symptoms[normed_illness].extend(preprocess(symptom, 2))
            else:
                merged_text[normed_illness].extend(preprocess(data[illness]['text']))
                merged_text[normed_illness].extend(preprocess(data[illness]['text'], 2))

    vsm.prepare(merged_text, 1., True)
    vsm.prepare(merged_symptoms, 4.)
    print('Dumping...')
    with open(combined_model, 'wb') as outfile:
        dill.dump(vsm, outfile)
    print('Done!')

    return vsm


def main():
    vsm = prepare_vector_space_model()
    while True:
        query = input('Enter your query: ')
        print('Retrieving possible illnesses...')
        print(vsm.retrieve_ranked_docs(preprocess(query) + preprocess(query, 2))[:10])

if __name__ == '__main__':
    main()
