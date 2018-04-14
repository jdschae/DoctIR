import sys
import os
from vectorspace import *
from preprocess import *
from ast import literal_eval


def prepare_illnesses(filenames):
    for filename in filenames:
        with open(filename) as file:
            return literal_eval(file.read())


def main():
    illness_files = ['mayoclinic.txt']
    illnesses = prepare_illnesses(illness_files)
    vsm = VectorSpaceModel(doc_wt_scheme='tfc', query_wt_scheme='nfx')
    tokens = {}
    for illness in illnesses:
        tokens[illness] = preprocess(illnesses[illness]['text'], 2)
        tokens[illness].extend(preprocess(illnesses[illness]['text']))
        for symptom in illnesses[illness]['symptoms_list']:
            tokens[illness].extend(preprocess(symptom, 2))
            tokens[illness].extend(preprocess(symptom))

    vsm.prepare(tokens)


    while True:
        query = input('Enter your query: ')
        print('Retrieving possible illnesses...')
        print(query)
        print(preprocess(query))
        print(vsm.retrieve_ranked_docs(preprocess(query, 2) + preprocess(query)))

if __name__ == '__main__':
    main()
