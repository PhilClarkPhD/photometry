import numpy as np
from scipy.sparse import csc_matrix, eye, diags  # TODO: add to requirements.txt
from scipy.sparse.linalg import spsolve
from sklearn.linear_model import Lasso


def smooth_signal(x, window_len=10, window='flat'):
    if x.ndim != 1:
        raise (ValueError, "smooth only accepts 1 dimension arrays.")

    if x.size < window_len:
        raise (ValueError, "Input vector needs to be bigger than window size.")

    if window_len < 3:
        return x

    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise (ValueError, "Window is one of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'")

    s = np.r_[x[window_len - 1:0:-1], x, x[-2:-window_len - 1:-1]]

    if window == 'flat':  # Moving average
        w = np.ones(window_len, 'd')
    else:
        w = eval('np.' + window + '(window_len)')

    y = np.convolve(w / w.sum(), s, mode='valid')

    return y[(int(window_len / 2) - 1):-int(window_len / 2)]


# TODO: differences unused
def WhittakerSmooth(x, w, lambda_, differences=1):
    X = np.matrix(x)
    m = X.size
    i = np.arange(0, m)  # TODO this isn't used
    E = eye(m, format='csc')
    D = E[1:] - E[:-1]  # numpy.diff() does not work with sparse matrix. This is a workaround.
    W = diags(w, 0, shape=(m, m))
    A = csc_matrix(W + (lambda_ * D.T * D))
    B = csc_matrix(W * X.T)
    background = spsolve(A, B)
    return np.array(background)


def airPLS(x, lambda_=100, porder=1, itermax=15):
    m = x.shape[0]
    w = np.ones(m)
    for i in range(1, itermax + 1):
        z = WhittakerSmooth(x, w, lambda_, porder)
        d = x - z
        dssn = np.abs(d[d < 0].sum())
        if dssn < 0.001 * (abs(x)).sum() or i == itermax:
            if i == itermax:
                print('WARING max iteration reached!')
            break
        w[d >= 0] = 0  # d>0 means that this point is part of a peak, so its weight is set to 0 in order to ignore it
        w[d < 0] = np.exp(i * np.abs(d[d < 0]) / dssn)
        w[0] = np.exp(i * (d[d < 0]).max() / dssn)
        w[-1] = w[0]
    return z


def get_zdFF(reference, signal, smooth_win=10, lambd=5e4, porder=1, itermax=50):
    # Smooth signal
    reference = smooth_signal(reference, smooth_win)
    signal = smooth_signal(signal, smooth_win)

    # Remove slope using airPLS algorithm
    r_base = airPLS(reference, lambda_=lambd, porder=porder, itermax=itermax)
    s_base = airPLS(signal, lambda_=lambd, porder=porder, itermax=itermax)

    # Remove baseline and the begining of recording
    reference = (reference - r_base)
    signal = (signal - s_base)

    # Standardize signals
    reference = (reference - np.median(reference)) / np.std(reference)
    signal = (signal - np.median(signal)) / np.std(signal)

    # Align reference signal to calcium signal using non-negative robust linear regression
    lin = Lasso(alpha=0.0001, precompute=True, max_iter=1000,
                positive=True, random_state=9999, selection='random')
    n = len(reference)
    lin.fit(reference.reshape(n, 1), signal.reshape(n, 1))
    reference = lin.predict(reference.reshape(n, 1)).reshape(n, )

    # z dFF
    zdFF = (signal - reference)

    return zdFF
