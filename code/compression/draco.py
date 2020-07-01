from cjio import cityjson
import helper_functions as hf
import json
from cjio.cityjson import CityJSON
import glob
import time
import os
import pandas as pd
import statistics
import pickle
import csv

ms_time = lambda: int(round(time.time() * 1000))
bytesize = lambda b : len(b.encode('utf-8'))

def compress_draco(cmpath, comprout, dataset, cm=None):
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
    #cm.j["draco"] = drc
            
    delim = "DRCDLM".encode() # compute shortest string that is not yet in the file? then put that as first word to select as delimiter
    cout.write(str(len(delim) + 1).encode() + delim)
    cout.write(json.dumps(cm.j).encode())
    cout.write(delim)
    cout.write(drc)

    cout.close()
    #cm_file.close()
    
    print("Compression finished")
    
    
def draco_decompress(cmout, comprout):
    cin = open(comprout, 'rb')
    b = cin.read()
    c = "".join(map(chr, b))
    
    delimlen = int(c[0])
    delim = c[1:delimlen]

    cm_s, drc = c.split(delim)[1:]   # first entry is the first character of the file, so remove

    cmd = hf.prep_cmd("decode", temppath + "temp.drc", temppath + "temp2.obj")
    hf.execute_cmd(cmd) 
    geom = open(temppath + "temp2.obj").read()
     
    cm_s = cm_s.replace ("'", '"')
    cm = CityJSON()
    
    cm.j = json.loads(cm_s)
    
    vertices, faces = hf.obj_to_vf(geom)
    
    cm.j['vertices'] = vertices
    
    for o_id, fs in faces.items():
        
        co = cm.j['CityObjects'][o_id]
        if "boundaries" not in co['geometry'][0].keys():
            co['geometry'][0]['boundaries'] = []

        if "Solid" in co['geometry'][0]['type']:
            co['geometry'][0]['boundaries'].extend([fs])
        elif co['geometry'][0]['type'] == "MultiSurface":
            co['geometry'][0]['boundaries'].extend(fs)
    
    fo = open(cmout, "w")
    # see old version
    
    print("Decompression finished")
    
    
def compression_factors(cmpath, dataset, method):
    if cmpath != None:
        cm_file = open(cmpath)
        cm = cityjson.reader(file=cm_file, ignore_duplicate_keys=True)
    else:
        cm = cmin
    
    originalsize = bytesize(str(cm.j))
    compressedsize = os.path.getsize("../../datasets/" + method + "/" + dataset + "_" + method + ".txt" )
    
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
    method = "draco"
    
    for file in files:
        print(file)
        benchmark = []
        
        dataset = file.split('\\')[-1].split('.')[0]
        columns.append(dataset)
        out = comprout + "draco/" + dataset + "_draco.txt" 
        
        for i in range(2):        
            start = ms_time()
            compress_draco(file, out, dataset)
            end = ms_time()
            
            benchmark.append(end - start)
            print(end - start)
            print(columns)
            print(benchmarks)

        benchmarks.append(statistics.mean(benchmark))
        #compression_factors(file, dataset, method)
        print(benchmarks)
    # for loading into pandas
    benchmarks = [benchmarks]
    
    #create_report("draco", dataset, benchmarks, columns)
        
    #draco_decompress(cmout, comprout)