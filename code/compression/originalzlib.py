from cjio import cityjson
import flunn
import json
import statistics
import time
import glob
import os 
import pandas as pd
import zlib
import numpy as np

ms_time = lambda: int(round(time.time() * 1000))
bytesize = lambda b : len(b.encode('utf-8'))

def compress_originalzlib(cmpath, comprout, cm = None):
    if cm == None:
        cm_file = open(cmpath)
        cm = cityjson.reader(file=cm_file, ignore_duplicate_keys=True)
    
    compressed = zlib.compress(json.dumps(cm.j).encode())

    cout = open(comprout, 'wb')
    cout.write(compressed)
    cout.close()
    
    print("Compression finished")

def decompress(cmout, comprout):
    cin = open(comprout, 'rb')
    cbor = str(flunn.loads(cin.read()))
    
    # CBOR outputs JSON with single quotes and with spaces behind semicolons and commas
    cbor = cbor.replace ("'", '"')
    cbor = cbor.replace (": ", ':')
    cbor = cbor.replace (", ", ',')
    
    fo = open(cmout, "w")
    fo.write(cbor)
    
    print("Decompression finished")

def create_report(method_name, dataset_name, benchmarks, columns):
    fn = "../benchmark/" + method_name + "/" + method_name + "_encodingtimes" + ".csv"

    if not os.path.exists(os.path.dirname(fn)):
        os.makedirs(os.path.dirname(fn))
    
    f = open(fn, "w")
    df = pd.DataFrame(benchmarks, columns = columns)
    df = df.T
    
    f.write(df.to_csv(index=True))
    f.close()


if __name__ == "__main__":
    # folders
    with open("paths.json", "r") as paths_json:
        paths = json.load(paths_json)
        temppath = paths["temppath"]
        cmpath = paths["cmpath"]
        comprout = paths["comprout"]
        cmout = paths["cmout"]
                
    columns = []
    benchmarks = []
    
    files = glob.glob(cmpath + '*.json')
    
    for file in files:
        benchmark = []
        
        dataset = file.split('\\')[-1].split('.')[0]
        #if dataset != "hdb":
        #    continue
        columns.append("originalzlib," + dataset)
        out = comprout + "originalzlib/" + dataset + "_originalzlib.zlib" 
        
        for i in range(10):   
            start = ms_time()
            compress_originalzlib(file, out)
            end = ms_time()
            
            benchmark.append(end - start)
            
            print(end - start)
            print(columns)
    
        benchmarks.append(statistics.mean(benchmark))
        print(benchmarks)
    
    benchmarks = [benchmarks]
    print(benchmarks)
    
    create_report("originalzlib", dataset, benchmarks, columns)