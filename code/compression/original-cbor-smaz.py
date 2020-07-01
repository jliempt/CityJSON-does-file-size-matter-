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
#import bson

ms_time = lambda: int(round(time.time() * 1000))
bytesize = lambda b : len(b.encode('utf-8'))
 
 
def compress(cmpath, comprout, dataset):
    cm_file = open(cmpath)
    cm = cityjson.reader(file=cm_file, ignore_duplicate_keys=True)
    cout = open(comprout, 'wb')
     
    #--- geometries
    # write temporary OBJ and DRC files
    #objpath = temppath + "obj/" + dataset + ".obj"
    #cmd = hf.prep_cmd("encode", objpath, temppath + dataset + ".drc", "-cl 5 -qp 0 --metadata")
    #hf.execute_cmd(cmd)
    #drc = drc = open(temppath + dataset + ".drc", "rb").read()
     
    """
    # remove all geometries from citymodel and assess its size for the purpose of statistics
    geomstr = ""
    geomstr += str(cm.j.pop('vertices'))
    for co in cm.j['CityObjects']:
        if len(cm.j['CityObjects'][co]['geometry']) > 0 and "boundaries" in cm.j['CityObjects'][co]['geometry'][0]:
            geomstr += str(cm.j['CityObjects'][co]['geometry'][0].pop('boundaries'))
    """
            
    #geomsize = bytesize(geomstr)
    #drcsize = os.path.getsize(temppath + "temp.drc")
    #geomperc = drcsize / geomsize
    #print("Geometry is compressed to %f%%" % geomperc)
     
    #--- attributes
    transform = cm.j.pop("transform")
    metadata = cm.j.pop("metadata")
    vertices = cm.j.pop("vertices")

    """
    # don't include elements that are only present once, because it will inhibit performance unnecessarily when decompressing
    for k, v in copy.deepcopy(elements_count).items():
        if v == 1:
            del elements_count[k]
    """
    
    


    def smazValues(d):
        for k,v in d.items():
            if isinstance(v, dict):
                smazValues(v)
            elif isinstance(v, str):
                d[k] = smaz.compress(v)


    def smazKeys(obj):
        if isinstance(obj, list):
            return [smazKeys(element) for element in obj]
        elif isinstance(obj, dict):
            return {smaz.compress(key): smazKeys(value) for key, value in obj.items()}
        else:
            return obj
    
    smazValues(cm.j)
    co = smazKeys(cm.j)
    #print(cm.j["CityObjects"].keys())

        
        
        
    #print(co)
    cm = {}
    #cm[list(co.keys())[0]] = co[list(co.keys())[0]]
    #print(co.keys())
    cm = co
    cm["transform"] = transform
    cm["metadata"] = metadata
    cm["vertices"] = vertices

    cbor = flunn.dumps(cm)
    #print(flunn.loads(cbor))
    cout.write(cbor)
    cout.close()
    cm_file.close()
     
    print("Compression finished")
 
def decompress(cmout, comprout):
    cin = open(comprout, 'rb')
    b = cin.read()
    c = "".join(map(chr, b))
     
    delimlen = int(c[0])
    delim = c[1:delimlen]
 
    drc, cm_s, sorted_elements = c.split(delim)[1:]   # first entry is the first character of the file, so remove
 
    cmd = hf.prep_cmd("decode", temppath + "temp.drc", temppath + "temp2.obj")
    hf.execute_cmd(cmd) 
    geom = open(temppath + "temp2.obj").read()
     
    sorted_elements = ast.literal_eval(sorted_elements)
 
    for i, element in enumerate(sorted_elements):
        cm_s = cm_s.replace("'" + str(i) + "'", '"' + element + '"')
      
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
    json_str = json.dumps(cm.j, separators=(',',':'))
    fo.write(json_str)
     
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
    columns.append("originalcborsmaz," + dataset)
    out = comprout + "originalcborsmaz/" + dataset + "_originalcborsmaz.cbor" 
    
    for i in range(10):   
        start = ms_time()
        compress(file, out, dataset)
        end = ms_time()
        
        benchmark.append(end - start)
        
        print(end - start)
        print(columns)
        break
    benchmarks.append(statistics.mean(benchmark))
    print(benchmarks)
    break
benchmarks = [benchmarks]


create_report("originalcborsmaz", dataset, benchmarks, columns)