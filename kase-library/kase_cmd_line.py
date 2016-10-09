__author__ = 'Jeremy'

from importTestArray import importSubstrateDefinitionsFile
from importTestArray import importSignificantSubstrates
import randomSelectReplacement as rsr
from mytimer import mytimer
import sys
import copy
import math
import scipy.stats
import numpy

if __name__ == "__main__":

    if len(sys.argv) != 5:
        print "python "+sys.argv[0]+" arg1 arg2 arg3"
        print "arg1\tfile listing significant substrates in your data"
        print "arg2\tfile mapping substrates to kinases in experiment"
        print "arg3\tnumber of simulations (permutations) to run"
        print "arg4\tfilename to write tsv results"
        sys.exit(0)

    mt = mytimer()
    mt.start()

    (substrate2kinases, allKinases) = importSubstrateDefinitionsFile(sys.argv[2])
    # substrate2kinases     text to (list of text) dictionary
    # allKinases            text to (integer count) dictionary

    (sigSubstrates, sigKinaseCount) = importSignificantSubstrates(sys.argv[1], substrate2kinases)
    #sigSubstrates          list of significant substrates
    #sigKinaseCount         text to count of kinases corresponding to significant substrates


    numSimulations = int(sys.argv[3])
    numSubstrates = len(sigSubstrates)

    kinaseSimulationsCounts = dict()

    #empty array with one member for each simulation
    emptyCounts = [0 for x in range(0, numSimulations)]

    simulations = dict()
    for kinase in allKinases.keys():
        simulations[kinase] = copy.deepcopy(emptyCounts)
    #now simulations[kin][s] points to kinase by name kin, sth simulation

    for s in range(0, numSimulations):
        (substratesChosen, kinaseCounts) = rsr.randoPermutationSimulation(substrate2kinases, numSubstrates)
        for substrate in substratesChosen:
            kinases = substrate2kinases[substrate]
            for kinase in kinases:
                simulations[kinase][s] += 1
        if (s % 1000 == 999):   print "Simulation "+str(s+1)+" complete\t"+mt.elapsed()

    meanSimulations = [0 for x in allKinases.keys()]
    stdSimulations = [0 for x in allKinases.keys()]
    zscoreKinases = [0 for x in allKinases.keys()]
    pvalueKinases = [0 for x in allKinases.keys()]
    results = []

    for k in range(0, len(allKinases.keys())):
        #meanSimulations[k] = math.mean(simulations[k])
        meanSimulations[k] = numpy.mean(simulations[allKinases.keys()[k]])
        #stdSimulations[k] = math.stdev(simulations[k])
        stdSimulations[k] = numpy.std(simulations[allKinases.keys()[k]])
        # if stdSimulations[k] == 0:
        #     print "nan detected"
        # if numpy.isnan(stdSimulations[k]):
        #     print "nan detected"
        kinase = allKinases.keys()[k]

        if stdSimulations[k] == 0:
            zscoreKinases[k] = "inf"
            pvalueKinases[k] = 0
        else:
            if kinase in sigKinaseCount:
                zscoreKinases[k] = (sigKinaseCount[kinase] - meanSimulations[k]) / stdSimulations[k]
            else:
                zscoreKinases[k] = (0 - meanSimulations[k]) / stdSimulations[k]
            pvalueKinases[k] = scipy.stats.norm.sf(abs(zscoreKinases[k]))*2

        results.append( (pvalueKinases[k], allKinases.keys()[k], zscoreKinases[k]) )

    print "sorting results\t"+mt.elapsed()
    results.sort()
    print "sorting complete\t"+mt.elapsed()

    outFile = open(sys.argv[4],'w')
    print "(kinase)\t(z-score)\t(p-value 2 tail)"
    outFile.write("(kinase)\t(z-score)\t(p-value 2 tail)\n")

    for result in results:
        (p, kinase, z) = result
        print kinase+"\t"+str(z)+"\t"+str(p)
        outFile.write(kinase+"\t"+str(z)+"\t"+str(p)+"\n")