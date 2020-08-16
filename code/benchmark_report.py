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

out = {}

#draco_sizes = json.load(open("draco_sizes.json", "r"))

# calcute means of results
for subdir, dirs, files in os.walk("./benchmark/"):
    for file in files:
        if file == "benchmark_report.py" or file == "tables.txt" or file == "benchmark.csv" or file == "draco_sizes.json" or file == "all_encodingtimes.csv" or file == "compressionfactors.csv" or file == "compressionfactors.xlsx" or file == "store_decode_results.py":
            continue
        if file[-4:] != "json":
            continue

        
        if "noattr" not in file:
            method, dataset = file.split(".")[0].split("_")
        else:
            method, dataset, addition = file.split(".")[0].split("_")
            dataset += "_" + addition

        if file.split(".")[-1] != "json":
            continue
        
        f = open(subdir + "\\" + file, 'r')

        if method not in out:
            out[method] = {}
        out[method][dataset] = {}

        results = json.load(f)
        
        operations = ["visualise", "editone", "editall", "editgeomone", "editgeomall", "queryone", "queryall", "bufferone", "bufferall"]
        
        for o in operations:
            if o not in results.keys():
                results[o] = [-1]
            

        
        
        for task, result in results.items():
            if task == "decode":
                continue
            # add .drc download times to results of Draco-including compression methods
            #if "draco" in method and task != "visualise":
                #for r in result:
                    #if r != 0:
                        # divide corresponding .drc size by 5000 kb (network speed) and add as milliseconds
                        #r += (draco_sizes[dataset] / 5000)  * 1000
                
            # change these two tasks to a better name
            if task == "editone":
                task = "editattrone"
            if task == "editall":
                task = "editattrall"
                
            # remove values that have Z-score of more than abs 2
            #z = stats.zscore(result).tolist()
            minimum = min(result)
            for i, n in reversed(list(enumerate(result))):  
                if n > minimum * 2 and n != -1:
                    del result[i]
                    
            mu = statistics.median(result)

            out[method][dataset][task] = {}
            out[method][dataset][task]["mu"] = mu


# calculate factors of results
for method in out.keys():
    for dataset in out[method].keys():
        #if "Zurich" in dataset:
        #    continue
        for task in out[method][dataset].keys():
            mu = out[method][dataset][task]["mu"]
            mu_original = out["original"][dataset][task]["mu"]
            
            # can't divide by 0, happens when there is something missing in original dataset
            if mu_original == 0 or mu == -1 or mu > 1000000000:
                out[method][dataset][task]["factor"] = None
            else:
                out[method][dataset][task]["factor"] = round(mu / mu_original, 2)
                

# for full dataframe display
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', -1)


mi_arrays = [[], []]
fs = []
datasets = []
# for multi-index
for method in out.keys():
    for task in out[method]["delft"].keys():
        mi_arrays[0].append(method)
        mi_arrays[1].append(task)
        

for method in out.keys():
    for dataset in out[method].keys():
        dataset_fs = []
        
        # "delft" specifically because order of keys can be different throughout datasets
        for task in out[method]["delft"].keys():
            task_fs = []
            #print(method, dataset, task)
            dataset_fs.append(out[method][dataset][task]["factor"])

        fs.append(dataset_fs)

for dataset in out["original"].keys():   
    datasets.append(dataset)



# transpose factors
dataset_n = len(datasets)

fs_t = []
for i in range(int(len(fs) / dataset_n)):
    tp = np.transpose(np.array(fs[0+dataset_n*i: dataset_n+dataset_n*i])).tolist()
    for j in range(len(tp)):
        fs_t.append(tp[j])
        

mi_tuples = list(zip(*mi_arrays))

index = pd.MultiIndex.from_tuples(mi_tuples, names=['method', 'task'])

df = pd.DataFrame(fs_t, index=index, columns=datasets)

idx = pd.IndexSlice
methods = df.index.levels[0]
tasks = df.index.levels[1]

pd.options.display.float_format = '{:.4f}'.format

fcsv = open("benchmark/benchmark.csv", "w")
fcsv.write(df.to_csv(index=True))
fcsv.close()