from cjio import cityjson
from cjio.cityjson import CityJSON
import glob
import json
from collections import Counter, defaultdict
import ast
import zlib
import helper_functions as hf
import statistics
import time
import flunn
from dahuffman import HuffmanCodec
import winsound
import copy
import os
import pandas as pd
import zlib
import pickle
import smaz
import zlib
import csv
#import bson

ms_time = lambda: int(round(time.time() * 1000))
bytesize = lambda b : len(b.encode('utf-8'))
 
     
def count_elements(d, elements_count):
    for k,v in d.items():
        if isinstance(v, dict):
            if k in elements_count.keys():
                elements_count[k] += 1
            else:
                elements_count[k] = 1
            count_elements(v, elements_count)
        elif isinstance(v, list):
            #if k == "boundaries":
            #    print(v)
            if k in elements_count.keys():
                elements_count[k] += 1
            else:
                elements_count[k] = 1
            
            for e in v:
                # because geometry has a list with a dict
                try:
                    if isinstance(e, dict):
                        count_elements(e, elements_count)
                    elif isinstance(v[0], str):
                        for s in v:
                            if v in elements_count.keys():
                                elements_count[s] += 1
                            else:
                                elements_count[s] = 1
                    elif isinstance(e, list):
                        pass
                    else:
                        pass
                except:
                    pass
            
                    
        elif not isinstance(v, str):
            if k in elements_count.keys():
                elements_count[k] += 1
            else:
                elements_count[k] = 1
        else:
            if k in elements_count.keys():
                elements_count[k] += 1
            else:
                elements_count[k] = 1
             
            if v in elements_count.keys():
                elements_count[v] += 1
            else:
                elements_count[v] = 1
            
 
def compress_dracoreplace(cmpath, comprout, dataset, cm=None):
    if cm == None:
        cm_file = open(cmpath)
        cm = cityjson.reader(file=cm_file, ignore_duplicate_keys=True)
    cout = open(comprout, 'w')
    
    temppath = load_paths()
     
    #--- geometries
    # write temporary OBJ and DRC files
    objpath = temppath + "obj/" + dataset + ".obj"
    cmd = hf.prep_cmd("encode", objpath, temppath + dataset + ".drc", "-cl 6 -qp 0 --metadata")
    hf.execute_cmd(cmd)
    drc = open(temppath + dataset + ".drc", "rb").read()
    
    del cm.j['vertices']
    for co in cm.j['CityObjects']:
        if len(cm.j['CityObjects'][co]['geometry']) > 0 and "boundaries" in cm.j['CityObjects'][co]['geometry'][0]:
            del cm.j['CityObjects'][co]['geometry'][0]['boundaries']
     
    #--- attributes
    transform = cm.j.pop("transform")
    metadata = cm.j.pop("metadata")
    
    elements_count = {}
    count_elements(cm.j, elements_count)


    sorted_elements = sorted(elements_count.items(), key=lambda kv: kv[1], reverse=True)

    sorted_elements = {e[0]: i for i, e in enumerate(sorted_elements)}
    
    def replace_key_val(data, replace_dict, prev_key=None):
        try:
            if type(data)== dict:
                return {replace_dict[k] : replace_key_val(v, replace_dict, replace_dict[k]) for k,v in data.items()}
            elif type(data)== list:
                if type(data[0])== dict and "boundaries" in data[0].keys():
                    # in this case, we have the boundaries from a geometry
                    # return the boundaries as is, and put these in a dictionary together with a dictionary containing replaced keys/values of other parts from geom dict (which are LOD and type)
                    d = {}
                    d["boundaries"] = data[0]["boundaries"]
                    # concatenate dicts)
                    return [{**d, **{replace_dict[k] : replace_key_val(v, replace_dict, replace_dict[k]) for k,v in data[0].items() if k != "boundaries"}}]
                else:
                    return {replace_dict[prev_key] : replace_key_val(e, replace_dict, replace_dict[prev_key]) for e in data}
            if str(data) in replace_dict:
                return replace_dict[str(data)]
            else:
                return data
        except:
            pass
            

    co = replace_key_val(cm.j, sorted_elements)

    cm = {}

    cm = co
    cm["transform"] = transform
    cm["metadata"] = metadata

    out = {"geom": "", "cm": cm, "attr": list(sorted_elements.keys())}

    json.dump(out, cout)
    #flunn.dump(out, cout)
    cout.close()
    #cm_file.close()
     
    print("Compression finished")
 
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
    
    
    totalcompression = originalsize - (compressedsize + drcsize)
    #print(totalcompression)
    geomcompression = geomsize - drcsize
    #print(geomcompression)
    attrcompression = (originalsize - geomsize) - bytesize(str(cm.j))
    #print(attrcompression)
    
    compressionfactor = (compressedsize + drcsize) / originalsize
    geomfactor = geomcompression / totalcompression
    #attrfactor = attrcompression / totalcompression
    attrfactor = 1 - geomfactor
    
    f = open("../benchmark/" + "compressionfactors.csv", "a", newline='')
    
    factors = [method, dataset, str(compressionfactor), str(geomfactor), str(attrfactor)]
    
    print(factors)
    
    writer = csv.writer(f)
    writer.writerow(factors)
    f.close()
    
def create_report(method_name, dataset_name, benchmarks, columns):
    fn = "../benchmark/" + method_name + "/" + method_name + "_encodingtimes" + ".csv"

    if not os.path.exists(os.path.dirname(fn)):
        os.makedirs(os.path.dirname(fn))
        
    f = open(fn, "w")
    df = pd.DataFrame(benchmarks, columns = columns)
    
    df = df.T
    
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
    method = "dracoreplace"
    
    for file in files:
        benchmark = []
        
        dataset = file.split('\\')[-1].split('.')[0]
        #if dataset != "hdb":
        #    continue
        columns.append("dracoreplace," + dataset)
        out = comprout + "dracoreplace/" + dataset + "_dracoreplace.txt" 
        
        for i in range(3):   
            start = ms_time()
            compress_dracoreplace(file, out, dataset)
            end = ms_time()
            
            benchmark.append(end - start)
            
            print(end - start)
            print(columns)

        benchmarks.append(statistics.mean(benchmark))
        print(benchmarks)
        #compression_factors(file, dataset, method)
    benchmarks = [benchmarks]
    
    
    create_report("dracoreplace", dataset, benchmarks, columns)
    
    frequency = 1500  # Set Frequency To 2500 Hertz
    duration = 1000  # Set Duration To 1000 ms == 1 second
    winsound.Beep(frequency, duration)
     
     
    # test full zlib compression
     
     
    """
    cm_file = open(cmpath)
    cm = cityjson.reader(file=cm_file, ignore_duplicate_keys=True)
     
    cmstr = str(cm.j)
     
    compr = zlib.compress(str(cm.j).encode())
    with open(temppath + "denhaagtest.txt", "wb") as file:
        file.write(compr)
    """