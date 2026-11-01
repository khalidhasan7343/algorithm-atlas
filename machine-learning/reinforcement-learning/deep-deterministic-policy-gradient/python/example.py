"""Bounded worked example, executed directly from the repository root."""
import json


def main():
    from solution import DDPG,actor_forward,soft_update
    import numpy as np
    m=DDPG(low=[-2],high=[4],hidden=2)
    for v in m.actor.values():v[:]=0
    a=actor_forward(m.actor,[[1.]],m.low,m.high)[0][0,0]
    t={'bias':np.array([0.])};o={'bias':np.array([2.])};soft_update(t,o,.25)
    print(json.dumps(dict(action=float(a),target_bias=float(t['bias'][0]))))


if __name__ == "__main__":
    main()
