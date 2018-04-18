import os
from vectorspace import *
from preprocess import *
from ast import literal_eval
from nltk.corpus import wordnet as wn
import dill
from collections import defaultdict


def read_illness_data(filenames):
    # Read in the illness dictionaries from the given files.
    sources = []
    for filename in filenames:
        with open(filename) as file:
            sources.append(literal_eval(file.read()))
    return sources


def get_tokens(files):
    # Get the text and symptoms tokens for the given files
    sources = read_illness_data(files)
    text_tokens = defaultdict(list)
    symptoms_tokens = defaultdict(list)
    for data in sources:
        for illness in data:
            add_data(text_tokens[illness],
                     symptoms_tokens[illness],
                     data[illness])

    return text_tokens, symptoms_tokens


def add_data(text, symptoms, illness_data):
    # If there's a symptoms list for this illness, then add it to the symptoms list.
    # Otherwise, add the text to the text list.
    if len(illness_data['symptoms_list']):
        for symptom in illness_data['symptoms_list']:
            symptoms.extend(preprocess(symptom))
            symptoms.extend(preprocess(symptom, 2))
    else:
        text.extend(preprocess(illness_data['text']))
        text.extend(preprocess(illness_data['text'], 2))
    return text, symptoms


def prepare_vector_space_model():
    '''
    Prepares the Wikipedia vector space model for internal querying (for
    illness name normalization) and the combined data vector space model.
    '''

    # If the combined vector space model already exists, then load it and return
    combined_model = 'model.pkl'
    if os.path.isfile(combined_model):
        print('Loading combined vector space model...')
        with open(combined_model, 'rb') as infile:
            return dill.load(infile)
        print('Done!')

    # If the Wikipedia vector space model exists, then load it.
    # Otherwise, create it and then save it.
    wiki_model = 'wiki_model.pkl'
    print('Reading Wikipedia text and symptoms tokens...')
    wiki_text, wiki_symptoms = get_tokens(['wikipedia.txt'])
    print('Done!')
    if os.path.isfile(wiki_model):
        print('Loading Wikipedia vector space model...')
        with open(wiki_model, 'rb') as infile:
            vsm = dill.load(infile)
    else:
        # Don't use the symptoms to build the Wikipedia vector space model.
        # Only use the text so that illness name normalization works better.
        print('Creating Wikipedia vector space model...')
        vsm = VectorSpaceModel(doc_wt_scheme='tfc', query_wt_scheme='nfx')
        vsm.prepare(wiki_text, 1.)
        print('Dumping...')
        with open(wiki_model, 'wb') as outfile:
            dill.dump(vsm, outfile)
    print('Done!')
    print('Creating combined vector space model...')

    # Merging illnesses
    illness_files = ['cdc.txt', 'mayoclinic.txt']
    sources = read_illness_data(illness_files)
    merged_symptoms = defaultdict(list)
    merged_text = defaultdict(list)
    for data in sources:
        for illness in data:
            # Internally query vector space model to normalize illness names.
            query = preprocess(illness) + preprocess(illness, 2)
            results = vsm.retrieve_ranked_docs(query)
            if len(results):
                normed_illness = results[0][0]
            else:
                normed_illness = illness
            add_data(merged_text[normed_illness],
                     merged_symptoms[normed_illness],
                     data[illness])

    vsm.prepare(wiki_symptoms, 2., only_index=True)
    vsm.prepare(merged_text, 1., only_index=True)
    vsm.prepare(merged_symptoms, 2.)
    print('Dumping...')
    with open(combined_model, 'wb') as outfile:
        dill.dump(vsm, outfile)
    print('Done!')

    return vsm


def is_yes(response):
    return ''.join(response.split()).lower() == 'y'


def disclaimer_understood():
    print('DISCLAIMER: This program is not a substitute for the advice of a ' +
          'real medical professional.')
    response = input('Please state whether you understand this disclaimer [y/n]: ')
    return is_yes(response)


def main():
    if not disclaimer_understood():
        print('Terminating program')
        return

    vsm = prepare_vector_space_model()
    print('Copyright\u00a9 doctIR')
    while True:
        query = input('Enter your query: ')
        print('Retrieving possible illnesses...')
        illnesses = vsm.retrieve_ranked_docs(preprocess(query) + preprocess(query, 2))
        print('Displaying {} out of {} results.'.format(min(10, len(illnesses)), len(illnesses)))
        for i in range(0, len(illnesses), 10):
            display_more = True
            for j in range(i, min(i + 10, len(illnesses))):
                print("\t{}. {}".format(j + 1, illnesses[j][0]))
                if j == len(illnesses) - 1:
                    display_more = False

            if display_more:
                response = input('\nDisplay 10 more results? [y/n]: ')
                if not is_yes(response):
                    break
            else:
                print('No more results.\n')

if __name__ == '__main__':
    main()
