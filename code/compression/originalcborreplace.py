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
            
 
def compress_originalcborreplace(cmpath, comprout, cm=None):
    if cm == None:
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
    
    elements_count = {}
    count_elements(cm.j, elements_count)

    """
    # don't include elements that are only present once, because it will inhibit performance unnecessarily when decompressing
    for k, v in copy.deepcopy(elements_count).items():
        if v == 1:
            del elements_count[k]
    """
            
    sorted_elements = sorted(elements_count.items(), key=lambda kv: kv[1], reverse=True)
    #sorted_elements = [e[0] for e in sorted_elements]
    sorted_elements = {e[0]: i for i, e in enumerate(sorted_elements)}
    
    # use this if don't want to include values that only occur once
    #sorted_elements = {e[0]: i for i, e in enumerate(sorted_elements) if e[1] != 1}
    #print(sorted_elements)
    """
    # TODO: implement a better way
    co_s = str(cm.j)
    for i, e in enumerate(sorted_elements):
        co_s = co_s.replace("'" + e + "'", '"'  + str(i) + '"')
    co_s = co_s.replace("'", '"')
    #cm_s = cm_s.replace ("'", '"')
    co = json.loads(co_s)
    """
    
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
            #return replace_dict[str(data)]
            pass
            

    co = replace_key_val(cm.j, sorted_elements)
    #print(co)
    cm = {}
    #cm[list(co.keys())[0]] = co[list(co.keys())[0]]
    #print(co.keys())
    cm = co
    cm["transform"] = transform
    cm["metadata"] = metadata
    cm["vertices"] = vertices
    #compr = zlib.compress((cm_s + str(sorted_elements)).encode())
    #print(compr)
    #cmtest = json.loads(cm_s)
         
    """
    ### Huffman-encode list of attributes
    codec = HuffmanCodec.from_data(str(list(sorted_elements.keys())))
    encoded = codec.encode(str(list(sorted_elements.keys())))
    
    tree = codec.get_code_table()
    # stringify _EOF (end of file) custom type to be able to store it
    for k in tree.keys():
        if type(k) != str and type(k) != int and type(k) != float:
            tree["_EOF"] = tree.pop(k)     
    print(codec.print_code_table())
    """
    
    ### ZLIB
    # put list in JSON because easier to read in JS
    attrlist = json.dumps({"attr": list(sorted_elements.keys())})
    #encoded = zlib.compress(attrlist.encode())

    out = {"geom": vertices, "cm": cm, "attr": attrlist}
    #out = {"drc": "", "cm": cm, "attr": encoded}
    #out = {"geom": vertices, "cm": cm, "attr": encoded}
    #out = {"geom": vertices, "cm": cm, "attr": encoded, "huff": json.dumps(tree)}

            
        
    
    
    
    #cout.write(drc)
    #cout.write(delim)
    #cout.write(cm_s.encode())
    #cout.write(delim)
    #cout.write(str(sorted_elements).encode())
    #cout.write(encoded)
    #cout.write(bson.dumps(cmtest))
    #cout.write(compr)
    
    #print(cm.j)
    #j = json.dumps(cm, indent=4)

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

        columns.append("originalcborreplace," + dataset)
        out = comprout + "originalcborreplace/" + dataset + "_originalcborreplace.cbor" 
        
        for i in range(10):   
            start = ms_time()
            compress_originalcborreplace(file, out)
            end = ms_time()
            
            benchmark.append(end - start)
            
            print(end - start)
            print(columns)
            break
        benchmarks.append(statistics.mean(benchmark))
        print(benchmarks)
    
    benchmarks = [benchmarks]
    
    
    create_report("originalcborreplace", dataset, benchmarks, columns)
    
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