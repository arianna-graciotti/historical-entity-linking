import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

#def cosine(vectors):
#    x = pt.FloatTensor([vector[0].tolist() for vector in vectors])
#    x = pt.nn.functional.normalize(x, p=2.0, dim=1)
#    X = pt.matmul(x, x.t())
#    return X

def get_prior(senses, all_senses, all_senses_indices, sense_dist):
    P = []
    for sense, sense_indices, dist in zip(senses, all_senses_indices, sense_dist):
        p = [0]*len(all_senses)
        for i, idx in enumerate(sense_indices):
            p[idx] = dist[i]
        P.append(p)
    return P

def rep_dynamics(X, S, P):
    iter = 1
    while True:
        P_ = np.zeros(P.shape)
        C = 0
        for i in range(X.shape[0]):
            nn = [n for n in np.nonzero(X[i])[0].tolist() if n != i]
            p_i_idxs = P[i].nonzero()[0]
            p_i = P[i, p_i_idxs]
            if p_i.nonzero()[0].shape[0] > 1:
                for j in nn:
                    x_j_idxs = P[j].nonzero()[0]
                    x_j = P[j, x_j_idxs]
                    S_ = X[i, j] * S[np.ix_(p_i_idxs, x_j_idxs)]
                    P_[i, p_i_idxs] = P_[i, p_i_idxs] + np.multiply(p_i, np.dot(S_, x_j.transpose()))
            else:
                P_[i] = p_i
        shift = max(-P_.min() + 1e-20, C)
        P_ = P_ + shift
        P_ = np.multiply(P_, P)
        Pnew = P_ / np.sum(P_, axis=1)[:, None]
        diff = np.linalg.norm(P - Pnew)
        P = Pnew
        if iter >= 1000 or diff < 10e-5:
            return P
        iter += 1

def dot(doc, word_indices, word_vectors, senses, sense_vectors, all_senses, all_senses_vectors, all_senses_indices, sense_dist):
    P = np.zeros((len(word_vectors),len(all_senses_vectors)))
    for i, word_vector in enumerate(word_vectors):
        sim = cosine_similarity(np.array(word_vector + word_vector).reshape(1, -1),
                                np.array([all_senses_vectors[sidx] for sidx in all_senses_indices[i]]))
        P[i][all_senses_indices[i][sim. argmax()]] = 1
        print(all_senses_indices[i][sim.argmax()])
    return P

def wsdg(doc, word_indices, word_vectors, senses, sense_vectors, all_senses, all_senses_vectors, all_senses_indices, sense_dist):
    X = cosine_similarity(word_vectors)
    X[X < .1] = 0
    S = cosine_similarity(all_senses_vectors)
    S[S<0] = 0
    P = np.array(get_prior(senses, all_senses, all_senses_indices, sense_dist))
    P = rep_dynamics(X, S, P)
    return P