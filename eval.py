from vectorspace import *
from preprocess import *
from ast import literal_eval
import dill
from collections import defaultdict
import copy


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
    wiki_text, wiki_symptoms = get_tokens(['wikipedia.json'])
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
    illness_files = ['cdc.json', 'mayoclinic.json']

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

#stores queries and Isabel Healthcare/ WebMD illnesses corresponding to them
benchmarkDict = {}
#stores what our search engine outputs for queries from benchmarkDict
outputDict = {}

pleurisyString = "chest pain shortness breath shoulder pain cough"
benchmarkDict[pleurisyString] = {}
benchmarkDict[pleurisyString]["isabel"] = ["pulmonary embolism", "lung cancer", "heart attack", "pleurisy", "langerhans cell histiocytosis class 1", "atypical pneumonia", "lung abscess", "sarcoidosis", "aortic aneurysm", "asthma", "thymic cancer", "angina", "lung tuberculosis", "pleural effusion", "pulmonary edema", "pericardial effusion", "thoracic aortic aneurysm", "tularemia", "aspiration syndromes", "heart failure", "histoplasmosis", "sickle cell anemia", "pulmonary hypertension", "idiopathic pulmonary fibrosis", "myocarditis", "aspergillosis", "bacterial pneumonia", "pneumothorax", "pericarditis", "bronchiectasis", "hypersensitivity pneumonitis", "wegener's granulomatosis", "mitral stenosis", "non-hodgkin lymphoma", "cytomegalovirus", "drug induced lung disease"]
benchmarkDict[pleurisyString]["webmd"] = ["pulmonary embolism", "asthma", "influenza", "pericarditis", "tuberculosis", "collapsed lung", "pneumothorax", "emphysema", "heartburn", "gerd", "common cold", "whooping cough", "bronchitis", "acute sinusitis", "costochondritis" "bacterial pneumonia", "broken rib", "fractured rib", "poisoning", "acute respiratory distress syndrome", "lyme disease", "sarcoidosis", "histoplasmosis", "esophagitis", "esophagael spasm"]

lymeString = "fever chills headache fatigue muscle pain joint pain swollen lymph nodes rash heart palpitation numbness in feet numbness in hand tingling in feet tingling in hands"
benchmarkDict[lymeString] = {}
benchmarkDict[lymeString]["isabel"] = ["lyme disease", "food poisoning", "tularemia", "brucellosis", "relapsing fever", "infectious mononucleosis", "human granulocytic anaplasmosis", "hiv", "aids", "influenza", "leptospirosis", "leukemia", "q fever", "rat-bite fever", "rocky mountain spotted fever", "cat-scratch disease", "endocarditis", "kikuchi disease", "poems", "schnitzler syndrome", "lemierre's syndrome", "viral hepatitis", "myocarditis", "type 2 diabetes", "bacterial meningitis", "dengue fever", "meningicoccal meningitis", "sarcoidosis", "cytomegalovirus", "non-hodgkin lymphoma", "systemic lupus erythematosus", "thrombocytosis"]
benchmarkDict[lymeString]["webmd"] = ["lumbar herniated disk", "hyperventilation", "influenza", "mononucleosis", "carpal tunnel syndrome", "sarcoidosis", "west nile disease", "chronic fatigue syndrome", "cfids", "lyme disease", "hypothyroidism", "shingles", "herpes zoster", "cervical herniated disk", "chronic kidney disease", "aseptic meningitis", "multiple sclerosis", "iron deficiency anemia", "aids", "acquired immunodeficiency syndrome", "decompression sickness", "hypocalcemia", "Guillain-Barré syndrome"]

dengueString = "fever severe headache pain behind the eyes joint pain muscle pain fatigue nausea vomiting skin rash nose bleed bleeding gums"
benchmarkDict[dengueString] = {}
benchmarkDict[dengueString]["isabel"] = ["relapsing fever", "lyme disease", "tularemia", "leptospirosis", "viral hepatitis", "rocky mountain spotted fever", "dengue fever", "infectious mononucleosis", "steven-johnson syndrome", "human granulocytic anaplasmosis", "leukemia", "brucellosis", "erythma multiforme", "relapsing polychonditis", "meningicoccal meningitis", "nomid", "west nile encephalitis", "babesiosis", "murine typhus", "crohn's disease", "drug-induced hepatitis", "toxic hepatitis", "systemic lupus erythematosus", "bacterial meningitis", "sepsis and shock", "lemierre's syndrome", "pyelonephritis", "polyarteritis nodosa", "henoch-schonlein purpura", "kikuchi disease", "antiphospholipid syndrome", "wegener's granulomatosis", "zika virus", "chemotherapy side effects"]
benchmarkDict[dengueString]["webmd"] = ["influenza", "acute sinusitis", "bacterial pneumonia", "kidney infection", "pyelonephritis", "chronic sinusitis", "west nile virus", "aseptic meningitis", "strep throat", "viral gastroenteritis", "drug allergy", "migraine", "appendicitis", "heat stroke", "hyperthermia"]

monoString = "fatigue headache sore throat chills fever muscle aches swollen lymph nodes jaundice skin rash abdominal soreness"
benchmarkDict[monoString] = {}
benchmarkDict[monoString]["isabel"] = ["tularemia", "infectious mononucleosis", "lyme disease", "viral hepatitis", "relapsing fever", "rocky mountain spotted fever", "brucellosis", "lemierre's syndrome", "leptospirosis", "human granulocytic anaplasmosis", "strep throat", "babesiosis", "meningicoccal meningitis", "west nile encephalitis", "cat-scratch disease", "leukemia", "cytomegalovirus", "hiv", "aids", "influenza", "q fever", "measles", "non-hodgkin lymphoma", "kikuchi disease", "sarcoidosis", "marshalls syndrome", "quinsy", "murine typhus", "dengue fever"]
benchmarkDict[monoString]["webmd"] = ["mononucleosis", "influenza", "strep throat", "common cold", "hepatitis b", "hepatitis a", "viral pneumonia", "appendicitis", "gallstones", "diverticulitis", "tonsillitis", "west nile virus", "poisoning", "intestinal obstruction", "pancreatic cancer", "lyme disease", "scarlet fever", "acute sinusitis", "laryngitis"]

choleraString = "rapid heart rate dry mouth dry nose low blood pressure thirst muscle cramps dehydration"
benchmarkDict[choleraString] = {}
benchmarkDict[choleraString]["isabel"] = ["addison's disease", "diabetic hypoglycemia", "heat exhaustion", "diabetes insipidus", "hypovolemic shock", "adrenal cancer", "heavy metal intoxication", "pancreatitis", "thryoid storm", "diabetic neuropathy", "fecal impaction", "nonketotic hyperosmolar coma", "theophylline toxicity", "postural orthostatic tachycardia syndrome", "alcoholic liver disease", "peritonitis", "primary adrenal insufficiency", "eating disorders", "portal hypertension", "portal varices", "periodic paralysis", "shigella infections", "bartter syndrome", "pulmonary embolism", "sjogren's syndrome", "antidiabetic agents toxicity", "diuretics toxicity"]
benchmarkDict[choleraString]["webmd"] = ["drug allergy", "diabetic ketoacidosis", "generalized anxiety disorder", "low potassium", "hypokalemia", "marijiana use", "type 2 diabetes", "iron deficiency anemia", "hyperthyroidism", "cholera", "chronic kidney disease", "sleep apnea", "appendicitis", "drug overdose", "bacterial pneumonia"]

herpesString = "cold sore burning urinating swollen lymph nodes fever headaches itching genitals backaches fatigue"
benchmarkDict[herpesString] = {}
benchmarkDict[herpesString]["isabel"] = ["tularemia", "cat-scratch disease", "brucellosis", "lyme disease", "pyelonephritis", "leukemia", "urinary infection", "west nile encephalitis", "non-hodgkin lymphoma", "tuberculous meningitis", "influenza", "relapsing fever", "dengue fever", "listeriosis", "sarcoidosis", "cold sores", "prostatitis", "hiv", "aids", "malignant bone tumors", "bacterial meningitis", "cystititus", "endocarditis", "epidural abscess", "lymphogranuloma venereum", "tuberculosis", "common cold", "herpes simplex", "rat-bite fever", "cytomegalovirus", "marshalls syndrome"]
benchmarkDict[herpesString]["webmd"] = ["cold sores", "osteomyelitis", "migraine", "crabs", "cluster headache", "influenza", "gonorrhea", "strep throat", "chronic sinusitis", "viral pneumonia", "common cold", "erythema multiforme", "mononucleosis", "intracranial hematoma", "acute sinusitis", "genital herpes", "abscess"]

rabiesString = "cough sore throat restlessness hallucinations seizures coma"
benchmarkDict[rabiesString] = {}
benchmarkDict[rabiesString]["isabel"] = ["rabies", "acute porphyria", "meningicoccal meningitis", "serotonin syndrome", "carbon monoxide toxicity", "substance abuse", "viral meningoencephalitis", "steven-johnson syndrome", "delirium tremens", "epilepsy", "heavy metal intoxication", "nmda receptor antibody encephalitis", "radioactive isotopes", "renal failure", "aseptic meningitis", "carbon dioxide toxicity", "pancreatic cancer", "barbiturates toxicity", "limbic encephalitis", "benzodiazepines toxicity", "epiglottitis", "hydrogen sulphide toxicity", "thryoid storm", "pesticides toxicity", "primary amoebic meningoencephalitis", "brain tumors", "environment exposure", "work exposure", "rocky mountain spotted fever", "antidepressants toxicity", "co-phenotrope toxicity", "gasoline exposure", "plague", "creutzfeldt-jakob disease", "tularemia", "nsaid's toxicity"]
benchmarkDict[rabiesString]["webmd"] = ["common cold", "west nile virus", "drug overdose", "hypoglycemia", "whooping cough", "poisoning", "influenza", "intoxication", "acute sinusitis", "alcohol intoxication", "mononucleosis", "aspirin poisoning", "tonsillitis", "laryngitis", "hay fever", "asthma", "tuberculosis", "intracranial hematoma", "epilepsy", "phencyclidine use", "abscess"]

depressionString = "anxiety sadness suicidal thoughts restlessness low energy poor concentration headaches trouble sleeping appetite loss"
benchmarkDict[depressionString] = {}
benchmarkDict[depressionString]["isabel"] = ["depression", "chronic fatigue syndrome", "lyme disease", "delirium tremens", "alcohol withdrawal syndrome", "bipolar disorder", "eating disorders", "general anxiety disorder", "brucellosis", "hyperthyroidism", "iron deficiency anemia", "vitamin b12 deficiency", "celiac disease", "postural orthostatic tachycardia syndrome", "alcohol hangover", "sleep apnea", "substance abuse", "dysthymic disorder", "pituitary cancer", "acute stress disorder", "adrenal cancer", "migraine"]
benchmarkDict[depressionString]["webmd"] = ["seasonal depression", "bipolar disorder", "attention deficit hyperactivity disorder", "autism", "generalized anxiety disorder", "chronic fatigue syndrome", "post-traumatic stress disorder", "barbiturate abuse", "tension headache", "drug allergy", "asperger syndrome", "anorexia nervosa", "schizophrenia", "restless legs syndrome", "intoxication", "aspirin poisoning", "hyperthyroidism", "postconcussive syndrome", "drug dependence and abuse", "acetaminophen poisoning", "dementia", "hypoglycemia", "poisoning", "concussion", "brain injury", "hypertension", "vasovagal syncope", "supraventricular tachycardia"]

sarcoidosisString = "blurred vision red eyes tearing eyes swollen lymph nodes hoarse voice cyst in bone kidney stones liver enlargement pericarditis arrhythmia heart failure meningitis seizures dementia depression psychosis"
benchmarkDict[sarcoidosisString] = {}
benchmarkDict[sarcoidosisString]["isabel"] = ["sarcoidosis", "whipple disease", "systemic lupus erythematosus", "brucellosis", "tularemia", "lyme disease", "creutzfeldt-jakob disease", "cat-scratch disease"]
benchmarkDict[sarcoidosisString]["webmd"] = ["alcoholism", "kidney stones", "schizophrenia", "sarcoidosis", "hypothyroidism", "poisoning", "alcohol intoxication", "drug overdose", "anemia", "cocaine abuse", "conjunctivitis", "drug dependence", "drug abuse", "acquired immunodeficiency syndrome", "brain tumor", "corneal abrasion", "hyperparathyroidism", "bipolar disorder", "hypoglycemia", "intracranial hematoma", "gout", "blood clot in the legs", "chronic kidney disease"]

hyperString = "weight gain fatigue weakness difficulty thinking confusion trouble concentrating cold sensitivity depression paranoia hearing loss dry skin hair loss"
benchmarkDict[hyperString] = {}
benchmarkDict[hyperString]["isabel"] = ["hypothyroidism", "hyperthyroidism", "hashimoto's thyroiditis", "sarcoidosis", "superior canal dehiscence syndrome", "vitamin b12 deficiency", "brucellosis", "depression", "heart failure", "multiple sclerosis", "postural orthostatic tachycardia syndrome", "diabetic hypoglycemia", "eating disorders", "heavy metal intoxication", "pancreatic cancer", "rhabdomyolysis", "acute porphyria", "gm2 gangliosidosis", "acute disseminated encephalomyelitis", "alcoholic liver disease", "osteitis fibrosa cystica", "renal failure", "celiac disease", "relapsing polychondritis", "scurvy", "syphilis", "brain tumors", "environmental exposure", "work exposure", "lyme disease", "sjogren's syndrome"]
benchmarkDict[hyperString]["webmd"] = ["hypothyroidism", "seasonal depression", "alcohol intoxication", "aspirin poisoning", "hearing loss", "brain aneurysm", "drug allergy", "hypoglycemia", "schizophrenia", "type 2 diabetes", "bipolar disorder", "cocaine abuse", "alcoholism", "hypothermia", "barbiturate abuse", "intoxication", "brain injury", "vasovagal syncope", "chronic fatigue syndrome", "diabetic ketoacidosis", "attention deficit hyperactivity disorder", "acute kidney failure", "cushing's syndrome"]

def main():
    vsm = prepare_vector_space_model()
    #to store data used for evaluation
    evalDict = {}
    #the benchmark illness list for each query is formed by the union of illnesses returned by Isabel Healthcare and WebMD
    for query in benchmarkDict:
        benchmarkDict[query]["union"] = copy.deepcopy(benchmarkDict[query]["isabel"])
        for illness in benchmarkDict[query]["webmd"]:
            if illness not in benchmarkDict[query]["union"]:
                benchmarkDict[query]["union"].append(illness)
        outputDict[query] = []
        evalDict[query] = {"relevance" : 0, "precision": 0, "numRelevant": 0, "RR": 0}
        storeList = vsm.retrieve_ranked_docs(preprocess(query) + preprocess(query, 2), 'euclid')
        #need foundRelevant and counter to trank reciprocal rank
        foundRelevant = False
        counter = 1
        print("\nNext Query: ", query)
        seenIllnesses = {}
        for value in storeList:
            outputDict[query].append(value[0].lower())
            for benchquer in benchmarkDict[query]["union"]:
                if (benchquer in value[0].lower()) and (benchquer not in seenIllnesses) and (value[0].lower() not in seenIllnesses):

                    #prints which benchmark string corresponds to our output string
                    print("benchmark: ", benchquer, "; output: ", value[0].lower())

                    #we increment number relevant responses if a benchmark string is in one of our output strings (our output was sometimes more specific than the benchmark sites)
                    evalDict[query]["numRelevant"] += 1

                    #we did not want to increment relevant responses more than once for matching the same benchmark or output string
                    seenIllnesses[benchquer] = 1
                    seenIllnesses[value[0].lower()] = 1

                    #for reciprocal rank tracking
                    if not foundRelevant:
                        evalDict[query]["RR"] = counter
                        foundRelevant = True
            counter += 1


    avgRelevance = 0.0
    avgPrecision = 0.0
    MRR = 0.0

    for query in evalDict:
        print("\nquery: ", query)
        evalDict[query]["relevance"] = (float(evalDict[query]["numRelevant"]) / float(len(benchmarkDict[query]["union"])))
        evalDict[query]["precision"] = (float(evalDict[query]["numRelevant"]) / float(len(outputDict[query])))
        avgRelevance += evalDict[query]["relevance"]
        avgPrecision += evalDict[query]["precision"]
        MRR += float(1 / evalDict[query]["RR"])
        print("Relevance: ", evalDict[query]["relevance"])
        print("Precision: ", evalDict[query]["precision"])
        print("Reciprocal Rank: 1 / ", evalDict[query]["RR"])

        #the overlap between the illnesses returned by WebMD and Isabel Healthcare for this query divided by the total number of combined returned responses
        print("WebMD, Isabel Healthcare Overlap: ", (len(benchmarkDict[query]["isabel"]) + len(benchmarkDict[query]["webmd"]) - len(benchmarkDict[query]["union"])), ' / ', (len(benchmarkDict[query]["webmd"]) + len(benchmarkDict[query]["isabel"])))

        #the number of illnesses we returned for this query
        print("Ouput size: ", len(outputDict[query]))

    avgRelevance = (avgRelevance / (len(benchmarkDict) * 1.0))
    avgPrecision = (avgPrecision / (len(benchmarkDict) * 1.0))
    fScore = ((2.0 * avgPrecision * avgRelevance) / (avgPrecision + avgRelevance))
    MRR = (MRR / (len(benchmarkDict) * 1.0))
    print("***************************")
    print("avgRelevance: ", avgRelevance)
    print("avgPrecision", avgPrecision)
    print("F-score: ", fScore)
    print("Mean Reciprocal Rank: ", MRR)

if __name__ == '__main__':
    main()
