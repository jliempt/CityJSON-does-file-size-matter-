import glob
import json
from cjio import cityjson
from cjio.cityjson import CityJSON
from collections import Counter, defaultdict
import ast
import json
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
            
 
def compress_dracocborreplace(cmpath, comprout, dataset, cm=None):
    if cm == None:
        cm_file = open(cmpath)
        cm = cityjson.reader(file=cm_file, ignore_duplicate_keys=True)
        
    temppath = load_paths()
        
    cout = open(comprout, 'wb')
     
    #--- geometries
    # write temporary OBJ and DRC files
    objpath = temppath + "obj/" + dataset + ".obj"
    cmd = hf.prep_cmd("encode", objpath, temppath + dataset + ".drc", "-cl 6 -qp 0 --metadata")
    hf.execute_cmd(cmd)
    drc = drc = open(temppath + dataset + ".drc", "rb").read()
    
    
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

    
    def replace_key_val(data, replace_dict):
        try:
            if type(data)== dict:
                return {replace_dict[k] : replace_key_val(v, replace_dict) for k,v in data.items()}
            elif type(data)== list:
                return {replace_dict[k] : replace_key_val(v, replace_dict) for k,v in data}
            return replace_dict[str(data)]
        except:
            pass

    co = replace_key_val(cm.j, sorted_elements)
    
    cm = {}

    cm = co
    cm["transform"] = transform
    cm["metadata"] = metadata
    
    # put list in JSON because easier to read in JS
    attrlist = json.dumps({"attr": list(sorted_elements.keys())})

    out = {"geom": drc, "cm": cm, "attr": attrlist}
    
    cbor = flunn.dumps(out)
    
    cout.write(cbor)
    cout.close()
    #cm_file.close()
     
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
    method = "dracocborreplacezlib"
    
    for file in files:
        benchmark = []
        
        dataset = file.split('\\')[-1].split('.')[0]
        #if dataset != "hdb":
        #    continue
        columns.append(dataset)
        out = comprout + "dracocborreplace/" + dataset + "_dracocborreplace.cbor" 
        
        for i in range(3):   
            start = ms_time()
            compress_dracocborreplace(file, out, dataset)
            end = ms_time()
            
            benchmark.append(end - start)
            
            print(end - start)
            print(columns)
            
        benchmarks.append(statistics.mean(benchmark))
        print(benchmarks)
        compression_factors(file, dataset, method)
    benchmarks = [benchmarks]
    
    
    create_report("dracocborreplace", dataset, benchmarks, columns)
    
    frequency = 2500  # Set Frequency To 2500 Hertz
    duration = 1000  # Set Duration To 1000 ms == 1 second
    winsound.Beep(frequency, duration)