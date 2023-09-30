from scipy.stats import chi2
import numpy as np

# N = number of occurrences
# n1 = percentage best
# n2 = percentage to eval

def get_pvalue(N, n1, n2, pval=0.5):
    n1 = N * n1
    n2 = N * n2
    p0 = (n1+n2) / (N*2)

    # Null hypothesis
    n10 = N * p0
    n20 = N * p0

    # Chi-square test
    observed = np.array([n1, N-n1, n2, N-n2])
    expected = np.array([n10, N-n10, n20, N-n20])
    diff = observed-expected
    chi2stat = sum(np.power(diff,2)/expected)
    pval_ = 1-chi2(1).cdf(chi2stat)
    if pval_<pval:
        print('Yes')
    else:
        print('No')

get_pvalue(1199,0.61,0.57)
