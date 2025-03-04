from collections import Counter, defaultdict
from math import log, sqrt


class VectorSpaceModel():
    '''
    Retrieves documents using a vector space model.
    Term-weighting components should use the naming conventions from Salton's
    paper.

    Usage:
        vsm = VectorSpaceModel()
        vsm.prepare(doc_tokens)             # prepare for retrieval
        vsm.retrieve_ranked_docs(query)     # get doc_ids ranked by relevance
    '''
    def __init__(self, doc_wt_scheme='tfx', query_wt_scheme='tfx'):
        self.__inverted_idx = defaultdict(lambda: defaultdict(float))
        self.__doc_wt_scheme = doc_wt_scheme
        self.__query_wt_scheme = query_wt_scheme
        self.__doc_weights = defaultdict(lambda: defaultdict(float))
        self.__doc_norms = defaultdict(float)
        self.__coll_freq_comp = defaultdict(float)
        self.docs = set()

    @property
    def doc_wt_scheme(self):
        return self.__doc_wt_scheme

    @doc_wt_scheme.setter
    def doc_wt_scheme(self, wt_scheme):
        self.__check_wt_scheme(wt_scheme)
        self.__doc_wt_scheme = wt_scheme

    @property
    def query_wt_scheme(self):
        return self.__query_wt_scheme

    @query_wt_scheme.setter
    def query_wt_scheme(self, wt_scheme):
        self.__check_wt_scheme(wt_scheme)
        self.__query_wt_scheme = wt_scheme

    def print_inverted_idx(self, token):
        print(self.__inverted_idx[token])

    def __check_wt_scheme(self, wt_scheme):
        if (len(wt_scheme) != 3 or
            wt_scheme[0] not in 'btn' or
            wt_scheme[1] not in 'xfp' or
            wt_scheme[2] not in 'xc'):
            # Accepted schemes are ones from Salton's paper.
            raise Exception('Invalid weighting scheme')

    def prepare(self, doc_tokens, idx_weight, only_index=False):
        '''
        Prepares the vector space model for doc retrieval.
        'doc_tokens' is expected to be a dictionary containing the tokens of
        all the docs and defined as follows:
            doc_tokens[<doc_id>] = [<list of tokens>]
        '''
        self.__index_docs(doc_tokens, idx_weight)
        print('Indexing complete!')

        if not only_index:
            self.__calc_doc_weights()
            print('Weighing complete!')
            self.__calc_doc_norms()
            print('Norming complete!')

            if self.__doc_wt_scheme[2] == 'c':
                # Normalize doc vectors using Euclidean length
                for token in self.__inverted_idx:
                    for doc_id in self.__inverted_idx[token]:
                        self.__doc_weights[doc_id][token] /= self.__doc_norms[doc_id]
            print('All preparations complete!')

    def __index_docs(self, doc_tokens, idx_weight):
        '''
        Updates the inverted index with tokens from 'doc_tokens'.
        '''
        for doc_id, tokens in doc_tokens.items():
            self.docs.add(doc_id)
            token_freqs = Counter(tokens)
            for token in token_freqs:
                self.__inverted_idx[token][doc_id] += token_freqs[token] * idx_weight

    def __calc_doc_weights(self):
        if self.__doc_wt_scheme == 'tfx' or self.__doc_wt_scheme == 'tfc':
            corpus_size = len(self.docs)
            for token in self.__inverted_idx:
                doc_freq = float(len(self.__inverted_idx[token]))
                if doc_freq:
                    self.__coll_freq_comp[token] = log(corpus_size / doc_freq)
                else:
                    print('how is the doc freq 0 for "{}"?????'.format(token))

                f =  self.__coll_freq_comp[token]
                for doc_id in self.__inverted_idx[token]:
                    tf = self.__inverted_idx[token][doc_id]
                    self.__doc_weights[doc_id][token] = tf * f

    def __calc_doc_norms(self):
        for doc_id in self.__doc_weights:
            self.__doc_norms[doc_id] = self.__norm(self.__doc_weights[doc_id].values())

    def __norm(self, wt_vector):
        norm = 0.
        for weight in wt_vector:
            norm += weight ** 2

        return sqrt(norm)

    def retrieve_ranked_docs(self, query, sim_scheme='cosine'):
        '''
        Retrieves a list of the doc ids sorted by descending relevance
        '''

        # Collect docs that contain at least one token from 'query'
        query_token_freqs = Counter(query)
        relevant_docs_ids = set()
        for token in query_token_freqs:
            if token in self.__inverted_idx:
                for doc_id in self.__inverted_idx[token]:
                    relevant_docs_ids.add(doc_id)

        query_weights = self.__calc_query_weights(query_token_freqs)
        similarities = self.__calc_similarities(relevant_docs_ids, query_weights, sim_scheme)
        sorted_docs = sorted(similarities, key=similarities.get, reverse=True)
        return [(doc_id, similarities[doc_id]) for doc_id in sorted_docs]

    def __calc_query_weights(self, query_token_freqs):
        weights = defaultdict(float)
        if self.query_wt_scheme == 'tfx':
            for token in query_token_freqs:
                f = self.__coll_freq_comp[token]
                weights[token] = query_token_freqs[token] * f
        elif self.query_wt_scheme == 'nfx':
            if len(query_token_freqs):
                max_freq = query_token_freqs.most_common(1)[0][1]
            for token, freq in query_token_freqs.items():
                f = self.__coll_freq_comp[token]
                weights[token] = (0.5 + 0.5 * freq / max_freq) * f

        return weights

    def __calc_similarities(self, relevant_docs_ids, query_weights, scheme='cosine'):
        similarities = defaultdict(float)

        query_norm = self.__norm(query_weights.values())
        for doc_id in relevant_docs_ids:
            inner_product = 0.
            for token, query_weight in query_weights.items():
                inner_product += query_weight * self.__doc_weights[doc_id][token]
                if scheme == 'cosine':
                    similarities[doc_id] = inner_product / self.__doc_norms[doc_id] / query_norm
                elif scheme == 'euclid':
                    similarities[doc_id] = -(self.__doc_norms[doc_id] ** 2 - 2 * inner_product + query_norm ** 2)


        return similarities
