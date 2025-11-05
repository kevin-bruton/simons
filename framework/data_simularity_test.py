import numpy as np
from scipy.stats import ks_2samp, ttest_ind, f, wasserstein_distance
from sklearn.metrics.pairwise import rbf_kernel
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from statsmodels.tsa.stattools import adfuller, kpss

# =============================================================================
# 1. Aggregate all thresholds in one dict for easy tuning
# =============================================================================
PARAMS = {
    'alpha_ks':       0.05,   # KS-test significance level
    'alpha_t':        0.05,   # t-test significance level
    'alpha_f':        0.05,   # F-test significance level
    'tau_mmd':        0.01,   # MMD distance threshold
    'delta_wass':     0.1,    # Wasserstein distance threshold
    'acc_threshold':  0.55,   # max classifier accuracy for similarity
    'alpha_adf':      0.05,   # ADF test significance level
    'alpha_kpss':     0.05    # KPSS test significance level
}

# =============================================================================
# 2. Individual Test Functions
# =============================================================================

def test_ks(x, y, alpha):
    """Two-sample Kolmogorov-Smirnov test."""
    stat, p = ks_2samp(x, y)
    return p > alpha

def test_t(x, y, alpha):
    """Two-sample t-test for equal means."""
    stat, p = ttest_ind(x, y, equal_var=True)
    return p > alpha

def test_f(x, y, alpha):
    """F-test for equality of variances."""
    v1, v2 = np.var(x, ddof=1), np.var(y, ddof=1)
    stat = v1 / v2
    dfn, dfd = len(x) - 1, len(y) - 1
    # two-tailed p-value
    p = 2 * min(f.cdf(stat, dfn, dfd), 1 - f.cdf(stat, dfn, dfd))
    return p > alpha

def compute_mmd(x, y, gamma=1.0):
    """Gaussian-kernel MMD, linear estimate."""
    X, Y = x.reshape(-1,1), y.reshape(-1,1)
    Kxx = rbf_kernel(X, X, gamma=gamma)
    Kyy = rbf_kernel(Y, Y, gamma=gamma)
    Kxy = rbf_kernel(X, Y, gamma=gamma)
    return Kxx.mean() + Kyy.mean() - 2 * Kxy.mean()

def test_mmd(x, y, tau, gamma=1.0):
    """Thresholded MMD test."""
    return compute_mmd(x, y, gamma) < tau

def test_wasserstein(x, y, delta):
    """1D Wasserstein (Earth Mover) distance test."""
    return wasserstein_distance(x, y) < delta

def test_classifier(x, y, threshold):
    """Classifier two-sample test with RandomForest."""
    X = np.concatenate([x, y], axis=0)
    if X.ndim == 1:
        X = X.reshape(-1,1)
    labels = np.concatenate([np.zeros(len(x)), np.ones(len(y))], axis=0)
    X_train, X_test, y_train, y_test = train_test_split(
        X, labels, test_size=0.3, stratify=labels, random_state=0
    )
    clf = RandomForestClassifier(n_estimators=100, random_state=0)
    clf.fit(X_train, y_train)
    acc = clf.score(X_test, y_test)
    return acc < threshold

def test_stationarity(x, alpha_adf, alpha_kpss):
    """Combine ADF and KPSS to ensure stationarity."""
    adf_stat, adf_p, *_ = adfuller(x)
    kpss_stat, kpss_p, *_ = kpss(x, regression='c', nlags='auto')
    return (adf_p < alpha_adf) and (kpss_p > alpha_kpss)

# =============================================================================
# 3. Orchestrator: run all tests and aggregate
# =============================================================================

def compare_distributions(in_sample, out_sample, params=PARAMS):
    """Return (all_tests_pass, dict_of_each_test)."""
    results = {
        'ks':         test_ks(in_sample, out_sample, params['alpha_ks']),
        't':          test_t(in_sample, out_sample, params['alpha_t']),
        'f':          test_f(in_sample, out_sample, params['alpha_f']),
        'mmd':        test_mmd(in_sample, out_sample, params['tau_mmd']),
        'wasserstein':test_wasserstein(in_sample, out_sample, params['delta_wass']),
        'clf':        test_classifier(in_sample, out_sample, params['acc_threshold']),
        'stationary': test_stationarity(in_sample, params['alpha_adf'], params['alpha_kpss'])
    }
    return all(results.values()), results

# =============================================================================
# 4. Example Usage
# =============================================================================
if __name__ == "__main__":
    # Generate toy data
    a = np.random.normal(size=500)
    b = np.random.normal(loc=0.1, size=500)  # slight shift
    yesno, detail = compare_distributions(a, b)
    print("Same distribution?", yesno)
    print(detail)


"""
Below is a ready-to-use Python module that encodes the full YES/NO workflow you described. All thresholds live in one place for easy tuning, and each test is implemented as a standalone function. At the end you get a single Boolean plus a dictionary of individual pass/fail flags.

Parameter Defaults
We choose common statistical significance levels and thresholds based on best practices:

KS Test α = 0.05: standard two-sample nonparametric test for distribution equality 
SciPy Documentation
Arize AI

t-Test α = 0.05: two-sample t-test for mean equality under assumed normality 
SciPy Documentation
GeeksforGeeks

F-Test α = 0.05: classic variance equality test via F-distribution 
GeeksforGeeks
Wikipedia

MMD τ = 0.01: small kernel‐MMD threshold with Gaussian RBF (σ² = 1) 
Kaggle
PyTorch

Wasserstein δ = 0.1: Earth-Mover distance for 1D samples 
SciPy Documentation
Medium

Classifier acc_max = 0.55: if a binary model can separate samples above chance by this margin, distributions differ 
arXiv
Seldon Documentation

ADF α = 0.05: reject unit‐root null (non-stationarity) below this p‐value 
MachineLearningMastery.com
Machine Learning Plus

KPSS α = 0.05: reject stationarity null above this p‐value 
MachineLearningMastery.com
Statsmodels

How it works

Thresholds are centralized in PARAMS for instant experimentation.

Each test returns a Boolean “pass” flag.

compare_distributions aggregates them: YES only if all tests pass.

Diagnostics are available in the returned dictionary, so you can quickly see which test flagged a shift.

You can now slot this module into your backtesting pipeline, call compare_distributions on your in-sample vs. candidate out-of-sample, and get an automated YES/NO verdict plus detailed drift diagnostics.
"""
