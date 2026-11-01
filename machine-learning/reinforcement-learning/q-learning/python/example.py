"""Executed analytical update and bounded chain policy example."""
import json
from solution import QLearning

def main():
    model=QLearning(3,2,alpha=.5,gamma=.9,seed=7)
    model.q[1]=[3,10]
    value=model.update(0,1,1,1)
    print(json.dumps(dict(update=value)))

if __name__=='__main__':main()
