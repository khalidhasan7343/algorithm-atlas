import importlib.util
from pathlib import Path
import sys
import pytest
spec=importlib.util.spec_from_file_location('atlas_b7_support',Path(__file__).with_name('support.py'))
support=sys.modules.get(spec.name)
if support is None:
    support=importlib.util.module_from_spec(spec);sys.modules[spec.name]=support;spec.loader.exec_module(support)
@pytest.fixture
def b7():return support
@pytest.fixture
def gradients():
    def check(function,parameters,analytic,atol=2e-6,rtol=3e-4):
        import numpy as np
        for key,array in parameters.items():
            assert analytic[key].shape==array.shape
            for index in np.ndindex(array.shape):
                plus={k:v.copy() for k,v in parameters.items()};minus={k:v.copy() for k,v in parameters.items()}
                plus[key][index]+=1e-6;minus[key][index]-=1e-6
                numeric=(function(plus)-function(minus))/2e-6
                np.testing.assert_allclose(analytic[key][index],numeric,atol=atol,rtol=rtol,err_msg=f'{key}{index}')
    return check
