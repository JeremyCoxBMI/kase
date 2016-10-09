__author__ = 'Jeremy'

import mytimer as mt

#returns 0-indexed array from 0 (inclusive) to n (exclusive)
def randoChooseWithoutReplacement(n , r):
    result = []
    count = 0
    while (count < r):
        rando = mt.rando(n) - 1
        if not rando in result:
            result.append(rando)
            count += 1
    return result


def randoPermutationSimulation(substrate2kinases, numSignificant):
    indexes = randoChooseWithoutReplacement(len(substrate2kinases), numSignificant)

    substratesChosen = []
    kinaseCounts = dict()
    for x in indexes:
        substratesChosen.append(substrate2kinases.keys()[x])
        for kinase in substrate2kinases[ substrate2kinases.keys()[x] ]:
            if kinase in kinaseCounts:
                kinaseCounts[kinase] += 1
            else:
                kinaseCounts[kinase] = 1

    return (substratesChosen, kinaseCounts)

