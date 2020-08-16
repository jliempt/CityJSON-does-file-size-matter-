from cjio import cityjson
import flunn
import json
import glob
import statistics
import time
import helper_functions as hf
import os
import pandas as pd
import csv

ms_time = lambda: int(round(time.time() * 1000))
bytesize = lambda b : len(b.encode('utf-8'))

def compress_dracocbor(cmpath, comprout, dataset, cm=None):
    if cm == None:
        cm_file = open(cmpath)
        cm = cityjson.reader(file=cm_file, ignore_duplicate_keys=True)
    
    temppath = load_paths()
    
    # geometries
    hf.cj_to_obj(cm, dataset=dataset)
    objpath = temppath + "obj/" + dataset + ".obj"
    cmd = hf.prep_cmd("encode", objpath, temppath + dataset + ".drc", "-cl 6 -qp 0 --metadata")
    hf.execute_cmd(cmd)
    
    drc = open(temppath + dataset + ".drc", "rb").read()
    cout = open(comprout, 'wb')
    
    del cm.j['vertices']
    for co in cm.j['CityObjects']:
        if len(cm.j['CityObjects'][co]['geometry']) > 0 and "boundaries" in cm.j['CityObjects'][co]['geometry'][0]:
            del cm.j['CityObjects'][co]['geometry'][0]['boundaries']
    cm.j["draco"] = drc
    
    cbor = flunn.dumps(cm.j)
    
    cout.write(cbor)
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


def compression_factors(cmpath, dataset, method):
    if cmpath != None:
        cm_file = open(cmpath)
        cm = cityjson.reader(file=cm_file, ignore_duplicate_keys=True)
    else:
        cm = cmin
    
    originalsize = bytesize(str(cm.j))
    compressedsize = os.path.getsize("../../datasets/" + method + "/" + dataset + "_" + method + ".cbor" )
    
    # remove all geometries from citymodel and assess its size for the purpose of statistics
    geomstr = ""
    geomstr += str(cm.j.pop('vertices'))
    for co in cm.j['CityObjects']:
        if len(cm.j['CityObjects'][co]['geometry']) > 0 and "boundaries" in cm.j['CityObjects'][co]['geometry'][0]:
            geomstr += str(cm.j['CityObjects'][co]['geometry'][0].pop('boundaries'))

    geomsize = bytesize(geomstr)
    drcsize = os.path.getsize(temppath + dataset + ".drc")
    
    
    totalcompression = originalsize - compressedsize
    #print(totalcompression)
    geomcompression = geomsize - drcsize
    #print(geomcompression)
    attrcompression = (originalsize - geomsize) - bytesize(str(cm.j))
    #print(attrcompression)
    
    compressionfactor = compressedsize / originalsize
    geomfactor = geomcompression / totalcompression
    #attrfactor = attrcompression / totalcompression
    attrfactor = 1 - geomfactor
    
    f = open("../benchmark/" + "compressionfactors.csv", "a", newline='')
    
    factors = [method, dataset, str(compressionfactor), str(geomfactor), str(attrfactor)]

    writer = csv.writer(f)
    writer.writerow(factors)
    f.close()

def create_report(method_name, dataset_name, benchmarks, columns):
    fn = "../benchmark/" + method_name + "/" + method_name + "_encodingtimes" + ".csv"

    if not os.path.exists(os.path.dirname(fn)):
        os.makedirs(os.path.dirname(fn))
        
    f = open(fn, "w")
    df = pd.DataFrame(benchmarks, columns = columns)
    
    f.write(df.to_csv(index=True))
    f.close()
    
    
def load_paths():
    # folders
    with open("paths.json", "r") as paths_json:
        paths = json.load(paths_json)
        temppath = paths["temppath"]
        cmpath = paths["cmpath"]
        comprout = paths["comprout"]
        cmout = paths["cmout"]
        
        return(temppath)
        

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
    method = "dracocbor"
    
    for file in files:
        benchmark = []
        
        dataset = file.split('\\')[-1].split('.')[0]
        columns.append(dataset)
        out = comprout + method + "/" + dataset + "_dracocbor.cbor" 
        
        for i in range(10):   
            start = ms_time()
            compress_dracocbor(file, out, dataset)
            end = ms_time()
            
            benchmark.append(end - start)
            
            print(end - start)
            print(columns)
            
        benchmarks.append(statistics.mean(benchmark))
        #compression_factors(file, dataset, method)
        print(benchmarks)
        
        
    benchmarks = [benchmarks]
    
    create_report("dracocbor", dataset, benchmarks, columns)
    #decompress(cmout, comprout)