import numpy as np
from completepeaker_metabolomics.core import preprocess_data, find_peak_limits_combined

def test_peak_boundaries():
    x = np.linspace(0,10,101)
    y = np.exp(-0.5*(x-5)**2)
    sm = preprocess_data(y)
    apex = np.argmax(sm)
    st, et = find_peak_limits_combined(x, sm, apex)
    assert st < 5 < et
