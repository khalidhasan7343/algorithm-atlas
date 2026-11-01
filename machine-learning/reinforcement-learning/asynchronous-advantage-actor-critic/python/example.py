"""Bounded worked example, executed directly from the repository root."""
import json


def main():
    from solution import A3C
    m=A3C(seed=1).train(iterations=1,max_steps=1,workers=2)
    print(json.dumps(dict(updates=m.updates_,workers_alive=m.workers_alive_)))


if __name__ == "__main__":
    main()
