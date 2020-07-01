import os
import pandas as pd
import statistics
import numpy as np
import glob
import json
from pandas.io.json import json_normalize
from pandas import IndexSlice
from matplotlib.font_manager import FontProperties
import matplotlib.pyplot as plt
from scipy import stats
import csv

#f = open("C:/Users/jordi/Dropbox/Geomatics/Thesis/benchmark/report.txt")
f = open("C:/Users/jordi/Dropbox/Geomatics/Thesis/benchmark/decodingreport.txt")

report = []

# split line into comma separated. the table has multiple spaces between every cell.
for l in f.readlines():
    l = list(filter(None, l.split('  ')))
    # remove newlines
    if "\n" in l[-1]:
        l[-1] = l[-1][:-1]
    
    # remove numbers in parantheses behind results
    for i, e in enumerate(l):
        if "(" in e:
            l[i] = e.split()[0]
            
    # fix row names
    for i, e in enumerate(l):
        if "[" in e:
            l[i] = e[e.find("[")+1:e.find("]")]
    
    # split dataset and compression number
    if "-" in l[0]:
        rowheader = l[0].split("-")
        
        del l[0]
    
        b = l[:]
        b.insert(0, rowheader[0])
        
        l = b[:]
        l.insert(1, rowheader[1])
    else:
        #otherwise it's the header. update it to have compression number.
        b = l[:]
        b.insert(1, "compression")
        l = b

    report.append(l)
    

    
fcsv = open("C:/Users/jordi/Dropbox/Geomatics/Thesis/benchmark/dracodecodingreport.csv", "w", newline="")
writer = csv.writer(fcsv)
writer.writerows(report)
fcsv.close()