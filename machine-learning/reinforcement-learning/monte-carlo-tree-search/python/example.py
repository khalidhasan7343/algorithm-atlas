"""Seeded bounded planning example."""
import json


def main():
    from solution import TinyPlanning,search
    a,root=search(TinyPlanning(),(0,0),iterations=200,max_depth=3,seed=91)
    print(json.dumps(dict(action=a,root_visits=root.visits)))


if __name__ == "__main__":
    main()
