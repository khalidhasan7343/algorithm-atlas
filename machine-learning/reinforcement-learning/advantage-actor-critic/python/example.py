"""Bounded worked example, executed directly from the repository root."""
import json


def main():
    from solution import A2C,loss_gradients
    import numpy as np
    m=A2C(hidden=2)
    for p in (m.actor,m.critic):
        for v in p.values():v[:]=0
    m.critic['b2'][:]=.25
    al,cl,ag,cg=loss_gradients(m.actor,m.critic,[[1.]],np.array([1]),[1.])
    print(json.dumps(dict(actor_loss=al,critic_loss=cl)))


if __name__ == "__main__":
    main()
