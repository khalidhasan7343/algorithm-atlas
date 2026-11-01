"""Bounded worked example, executed directly from the repository root."""
import json


def main():
    from solution import surrogate
    import numpy as np
    loss,_,_=surrogate(np.log(.5*np.array([1.3,.7,1.3,.7])),np.log(np.full(4,.5)),[2,2,-2,-2])
    print(json.dumps(dict(loss=loss)))


if __name__ == "__main__":
    main()
