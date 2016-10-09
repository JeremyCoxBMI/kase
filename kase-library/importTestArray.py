__author__ = 'Jeremy'

import sys

def importSubstrateDefinitionsFile( filename ):
    resultSub2Kinase = dict()
    resultKinases = dict()
    for line in open(filename):
        line = line.upper()
        splits = line.split(',')
        substrate = splits[0]
        kinases = splits[1].split()
        resultSub2Kinase[substrate] = kinases
        for kinase in kinases:
            if kinase in resultKinases:
                resultKinases[kinase] += 1
            else:
                resultKinases[kinase] = 1
    return (resultSub2Kinase, resultKinases)

def importSignificantSubstrates( filename, resultSub2Kinase ):
    result = []
    sigKinaseCount = dict()
    for line in open(filename):
        line = line.upper()
        substrate = line.strip('\n')
        if not substrate in resultSub2Kinase.keys():
            print "\tWARNING\tSubstrate found in sig. substrate list NOT in substrate-kinase definition file :: offender ::\t"+substrate
            sys.exit(0)
        result.append(substrate)
        for kinase in resultSub2Kinase[substrate]:
            if kinase in sigKinaseCount:
                sigKinaseCount[kinase] += 1
            else:
                sigKinaseCount[kinase] = 1
    return (result, sigKinaseCount)