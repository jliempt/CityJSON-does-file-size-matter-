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

draco_sizes = json.load(open("draco_sizes.json", "r"))

# calcute means of results
for subdir, dirs, files in os.walk(".\\"):
    for file in files:
        if file == "benchmark_report.py" or file == "tables.txt" or file == "benchmark.csv" or file == "draco_sizes.json" or file == "all_encodingtimes.csv" or file == "all_encodingtimes_fix.csv":
            continue
        if file[-4:] != "json":
            continue
        #print(file.split(".")[0].split("_"))

        if "noattr" not in file:
            method, dataset = file.split(".")[0].split("_")
        else:
            method, dataset, addition = file.split(".")[0].split("_")
            dataset += "_" + addition
        #print(dataset)
        if file.split(".")[-1] != "json":
            continue
        
        f = open(subdir + "\\" + file, 'r')

        if method not in out:
            out[method] = {}
        out[method][dataset] = {}

        results = json.load(f)

        
        # add .drc download times to results of Draco-including compression methods
        for task, result in results.items():
            if task == "decode":
                continue
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
            
            #for i, score in reversed(list(enumerate(z))):
            #    if (score > minimum * 6) and abs(score) > 1.5:
            #        del result[i]
            #        z = stats.zscore(result).tolist()

            mu = statistics.median(result)


            out[method][dataset][task] = {}
            out[method][dataset][task]["mu"] = mu


# calculate factors of results
for method in out.keys():
    for dataset in out[method].keys():
        
        for task in out[method][dataset].keys():
            mu = out[method][dataset][task]["mu"]
            try:
                mu_original = out["original"][dataset][task]["mu"]
            except:
                mu_original = None
                print("error with " + method, dataset, task)

            # can't divide by 0, happens when there is something missing in original dataset
            if mu_original <= 0 or mu_original > 1000000000 or mu == -1 or mu == -1.0 or mu > 1000000000 or mu_original == None:
                print(method, dataset, task)
                out[method][dataset][task]["factor"] = None
            else:
                out[method][dataset][task]["factor"] = round(mu / mu_original, 2)
                #if task == "bufferall" and dataset == "Zurich" and method == "dracocbor":
                    #print(out[method][dataset][task]["factor"])
                

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
        #if method == "dracocborreplace":
            #print(task)
        mi_arrays[0].append(method)
        mi_arrays[1].append(task)
        

for method in out.keys():
    for dataset in out[method].keys():
        dataset_fs = []
        
        # "delft" specifically because order of keys can be different throughout datasets
        for task in out[method]["delft"].keys():
            task_fs = []
            #print(method, dataset, task)
            try:
                dataset_fs.append(out[method][dataset][task]["factor"])
            except:
                dataset_fs.append(-1)
                print("error with " + method, dataset, task)

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
#print(fs)
index = pd.MultiIndex.from_tuples(mi_tuples, names=['method', 'task'])
#index = pd.MultiIndex.from_tuples(fs, mi_tuples, names=['method', 'task'])
#print(fs)

df = pd.DataFrame(fs_t, index=index, columns=datasets)
#print(df)
#print(df)
#print(pd.DataFrame.from_dict(out, orient='index'))
idx = pd.IndexSlice
methods = df.index.levels[0]
tasks = df.index.levels[1]

pd.options.display.float_format = '{:.4f}'.format
#print(df)
#print(fs)
fcsv = open("benchmark.csv", "w")
fcsv.write(df.to_csv(index=True))
fcsv.close()
f = open("tables.txt", "w")

#print(df.round(2))

f.write(df.to_latex(index=True))
f.write("\n\n\n\n\n")

"""
for task in tasks:
    dft = df.loc[idx[:, task], :]
    dft.index = methods
    print(task)
    print(dft)
    # Plot dataframe
    ax = dft.plot.bar()
    #task = task.capitalize()
    ax.set_title("Performance comparison: " + task + " (factor)")
    
    font = FontProperties()
    font.set_size('small')
    ax.legend(bbox_to_anchor=(1.45, 1.0), prop=font, title="Dataset")
    ax.set_ylabel("Time factor")
    #ax.legend(bbox_to_anchor=(0, 1), loc='upper left', ncol=1)
    #ax.set_yticks(np.arange(0, 5.5, step=0.5))
    plt.axhline(y=1, color='y', linestyle='--')
    #print(dft.to_latex)
    #f.write(dft.to_latex)
    #f.write("\n")
"""
"""
df_tasks = None
for task in tasks:
    dft = df.loc[idx[:, task], :]
    dft.index = methods
    dft['mean'] = dft.mean(axis=1)
    #print(dft["mean"])
    
    
    #print(dft['mean'])
    # Plot dataframe
    dft = pd.DataFrame(dft['mean'])
    
    ax = dft.plot.bar()
    #task = task.capitalize()
    ax.set_title("Performance comparison: " + task + " (mean)")
    ax.get_legend().remove()
    ax.set_ylabel("Time factor")
    plt.axhline(y=1, color='y', linestyle='--')
    

    
    #if not isinstance(df_tasks, pd.DataFrame):
    #    df_tasks = dft
    #else:
    #    df_tasks.merge(dft)
#print(df_tasks)
"""
#f.write(dft.to_latex(index=True))
#f.write("\n \\\\ \n")


"""
method_means = []
for method in methods:
    dfm = df.loc[idx[method, :], :]
    dataset_mean = dfm.mean(axis=0)
    #print(dfm)
    method_mean = dataset_mean.mean(axis=0)
    method_means.append(method_mean)


print(methods)
print(method_means)
plt.bar(methods, method_means)
plt.title("Performance comparison: compression methods (mean over all tasks and datasets)")
plt.ylabel("Time factor")
plt.axhline(y=1, color='y', linestyle='--')
#df = df.loc[idx[:, method], :]
#print(df)
#print(df.mean())
"""

f.close()