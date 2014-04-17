#!/usr/bin/python
# -*- coding: utf-8 -*-

checkpath = "C:/Users/alin/Documents/MyStuff/knapsack"
from collections import namedtuple
Item = namedtuple("Item", ['index', 'value', 'weight'])

def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    firstLine = lines[0].split()
    item_count = int(firstLine[0])
    capacity = int(firstLine[1])

    items = []

    for i in range(1, item_count+1):
        line = lines[i]
        parts = line.split()
        items.append(Item(i-1, int(parts[0]), int(parts[1])))

##    print item_count
##    print capacity
##    print items


##    return NaiveSolver(item_count, capacity, items)
    # a trivial greedy algorithm for filling the knapsack
    # it takes items in-order until the knapsack is full
    writeLP(item_count, capacity, items)
##
##    return DynamicProgSolver(item_count, capacity, items)

    return DFSBranchBound(item_count, capacity, items)
def NaiveSolver(item_count, capacity, items):
    """ naive solver """
    value = 0
    weight = 0
    taken = [0]*len(items)

    for item in items:
        if weight + item.weight <= capacity:
            taken[item.index] = 1
            value += item.value
            weight += item.weight

    # prepare the solution in the specified output format
    output_data = str(value) + ' ' + str(0) + '\n'
    output_data += ' '.join(map(str, taken))
    return output_data

def DFSBranchBound(item_count, capacity, items):
    """ depth first branch and bround """
    items = sorted(items, key = lambda sec: float(sec.value)/float(sec.weight), reverse = True) #reorder the items in terms of value/weight decreasing
    taken = [0]*len(items)
    curOpt = dfsBranch(0, 0, capacity, 0, items, item_count)
    return curOpt
def dfsBranchr(curItem, curOpt, curCap, curVal, items, item_count):
    """ recursive branch function, but cannot handle large problem because of python recursion limit """
    if curItem == item_count:
        #end of a branch
        return max(curOpt,curVal)

    weight = items[curItem].weight
    value = items[curItem].value

    if weight<=curCap:
        #include the curItem
        optEstimate = curVal + value + getEstimate(curItem+1, items, item_count, curCap - weight)
        if optEstimate > curOpt:
            #may produce better result
            leftOpt = dfsBranch(curItem+1, curOpt, curCap-weight, curVal + value, items, item_count)
            if leftOpt > curOpt:
                curOpt = leftOpt

    optEstimate = curVal + getEstimate(curItem+1, items, item_count, curCap)
    if optEstimate > curOpt:
        #not including curItem
        #may produce better result
        rightOpt = dfsBranch(curItem+1, curOpt, curCap, curVal, items, item_count)
        if rightOpt > curOpt:
            curOpt = rightOpt

    return curOpt

def dfsBranch(items, item_count, capacity):
    """ iterative implementation of branch and bound """
    left = [False]*item_count
    right = [False]*item_count
    curOpt = 0
    curVal = 0
    curCap = capacity

    curItem = 0
    while curItem>=0:
        if curItem == item_count-1:
            #leaf node
            if items[curItem].weight <= curCap:
                if curVal + items[curItem].value > curOpt:
                    curOpt = curVal + items[curItem].value
            left[curItem] = True
            right[curItem] = True
        else:
            if not left[curItem]:
                left[curItem] = True
                if items[curItem].weight <= curCap:
                    optEstimate = curVal + value + getEstimate(curItem+1, items, item_count, curCap - weight)
                    if optEstimate > curOpt:
                        curVal = curVal + value
                        curItem = curItem + 1
            elif not right[curItem]:
                right[curItem] = True
                optEstimate = curVal + value + getEstimate(curItem+1, items, item_count, curCap - weight)
                if optEstimate > curOpt:
                    curVal = curVal + value
                    curItem = curItem + 1

        if left[curItem] and right[curItem]:
            #back tracking to the first non-done node, reseting status on the way
            while left[curItem] and right[curItem] and curItem >=0:
                left[curItem] = False
                right[curItem] = False
                curItem-=1


def getEstimate(firstItem, items, item_count, Cap):
    """ give a upperbound of the knapsack problem:
        select from items[firstItem .....(item_count)-1] subject to capacity = Cap.
        by relaxing the binary constraint.
        Because vmIndex is ordered by value per weight, the relaxed LP can be solved easily by
        starting from the first one and keep putting until the capacity is hit.
    """
    if Cap == 0:
        return 0.0
    totalValue = 0.0
    for i in range(firstItem, item_count):
        if items[i].weight <= Cap:
            totalValue = totalValue + items[i].value
            Cap = Cap - items[i].weight
        else:
            totalValue = totalValue + items[i].value *(float(Cap)/items[i].weight)
            break
    return totalValue

def DynamicProgSolver(item_count, Capacity, items):
    """ Solver using dynamic programming """
    O = {}
    for cap in range(0, Capacity+1):
        O[(cap, 0)] = 0

    for n in range(1, item_count+1):
        for cap in range(0, Capacity+1):
            updateOracle(O, cap, n, items)

#    printOracle(O, item_count, Capacity)
    output_data = str(O[(Capacity, item_count)])
    return output_data

def updateOracle(O, CAP, N, items):
    """ find O[(CAP, N)] i.e, using only the first N items with knapsack capacity as CAP, find the optimal soltuion
        O[(CAP, N)] = 0  if CAP = 0
                    = O[(CAP, N-1)] if items[N-1].weight > CAP
                    = max{ O[(CAP, N-1)], items[N-1].value + O[(CAP-items[N-1].weight, N-1)]
    """
    if CAP == 0:
        O[(CAP, N)] = 0
    elif items[N-1].weight > CAP:
        O[(CAP, N)] = O[(CAP, N-1)]
    else:
        O[(CAP, N)] = max(O[(CAP, N-1)], items[N-1].value + O[(CAP-items[N-1].weight, N-1)])

#################################################################
# utility function

def printOracle(O,item_count, Capacity):
    """ print out the oracle for a check """
    checkFile = checkpath + "/check.csv"
    f = open(checkFile, 'w')
    line = "*"
    for i in range(0, item_count+1):
        line = line + "," + str(i)
    f.write(line + "\n")
    for cap in range(0, Capacity+1):
        line = str(cap)
        for i in range(0, item_count + 1):
            line = line + "," + str(O[(cap,i)])
        f.write(line + "\n")
    f.close()

def writeLP(item_count, capacity, items):
    """ formulate the problem as an MIP """
    lpfile = checkpath + '/knapsack.lp'
    f = open(lpfile, 'w')
    f.write("Maximize\n")
    f.write("Objective:\n")
    cns = ""
    cnt = 0
    for i in range(0, item_count):
        xVar = "x_"+str(i)
        cns = cns + " + " + str(items[i].value) + " " + xVar
        cnt = cnt  + 1
        if cnt % 5 == 4:
            f.write(cns + "\n")
            cns = ""
            cnt = 0
    f.write(cns + "\n")

    f.write("Subject To\n")
    cns = ""
    cnt = 0
    for i in range(0, item_count):
        xVar = "x_"+str(i)
        cns = cns + " + " + str(items[i].weight) + " " + xVar
        cnt = cnt  + 1
        if cnt % 5 == 4:
            f.write(cns + "\n")
            cns = ""
            cnt = 0
    f.write(cns + " <= " + str(capacity) + "\n")

    f.write("Binaries\n")
    for i in range(0, item_count):
        xVar = "x_"+str(i)
        f.write(xVar + "\n")
    f.write("End")
    f.close()
import sys

if __name__ == '__main__':
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        input_data_file = open(file_location, 'r')
        input_data = ''.join(input_data_file.readlines())
        input_data_file.close()
        print solve_it(input_data)
    else:
        file_location = "C:/Users/alin/Documents/MyStuff/knapsack/data/ks_1000_0"
        input_data_file = open(file_location, 'r')
        input_data = ''.join(input_data_file.readlines())
        input_data_file.close()
        print solve_it(input_data)
    #    solve_it(input_data)
#        print 'This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/ks_4_0)'

