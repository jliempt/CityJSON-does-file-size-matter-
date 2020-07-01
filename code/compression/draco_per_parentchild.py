from cjio import cityjson, subset
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


def compress(cmpath, comprout, dataset):
    cm_file = open(cmpath)
    cm = cityjson.reader(file=cm_file, ignore_duplicate_keys=True)
    
    dataset = cmpath.split("/")
    dataset = dataset[-1].split(".")[0]

    # geometries
    collection = {"type": "CityJSONCollection",
                  "features": []}
    
    cout = open(comprout, 'wb')
    
    
    for i, co_id in enumerate(cm.j["CityObjects"]):
        cjf = {}
        cjf["type"] = "CityJSONFeature"
        cjf["id"] = co_id
        
        if "children" in cm.j["CityObjects"][co_id]:
            co_ids = [co_id] + cm.j["CityObjects"][co_id]["children"]
            cos = cm.get_subset_ids(co_ids)
            
            hf.cj_to_obj(cos, dataset + "_parentchild", i)
            cmd = hf.prep_cmd("encode", temppath + "obj/" + dataset + "_parentchild" + str(i) + ".obj", temppath + "obj/" + dataset + "_parentchild" + str(i) + ".drc", "-cl 1 -qp 0 --metadata")
            hf.execute_cmd(cmd)
            drc = open(temppath + "obj/" + dataset + "_parentchild" + str(i) + ".drc", "rb").read()
            
            cjf["drc"] = drc
            
            for co_id in cos.j["CityObjects"]:    
                if len(cos.j['CityObjects'][co_id]['geometry']) > 0 and "boundaries" in cos.j['CityObjects'][co_id]['geometry'][0]:
                    del cos.j['CityObjects'][co_id]['geometry'][0]['boundaries']
            
            for k,v in cos.j.items():
                if k != "type" and k != "version" and k != "transform" and k != "metadata" and k != "vertices":
                    cjf[k] = v
            
            
        # in this case it's a child and would already be processed when its parent is encountered
        elif "parents" in cm.j["CityObjects"][co_id]:
            continue
            
        else:
            co = cm.get_subset_ids([co_id])
            
            drc = open(temppath + "obj/" + dataset + str(i) + ".drc", "rb").read()
            
            if len(co.j['CityObjects'][co_id]['geometry']) > 0 and "boundaries" in co.j['CityObjects'][co_id]['geometry'][0]:
                del co.j['CityObjects'][co_id]['geometry'][0]['boundaries']
            
            cjf["drc"] = drc
            
            for k,v in co.j.items():
                if k != "type" and k != "version" and k != "transform" and k != "metadata" and k != "vertices":
                    cjf[k] = v
                    
            #print(json.dumps(cjf, indent=4))

        collection["features"].append(cjf)
    
    if "transform" in cm.j:
        collection["transform"] = cm.j["transform"]
    if "metadata" in cm.j:
        collection["metadata"] = cm.j["metadata"]
        
    #print(collection)
    #json.dump(collection, cout)
    flunn.dump(collection, cout)
    cout.close()
    cm_file.close()
    
    """
    for i, co in enumerate(cm.j["CityObjects"]):
        try:
            co_cm = cm.get_subset_ids([co])            
        except:
            # in this case the CO was a parent and didn't have a geometry. in that case just add it without its geometry.
            print(cm.j["CityObjects"][co])
            cjf = {}
            cjf["type"] = "CityJSONFeature"
            cjf["id"] = co
            del cm.j["CityObjects"][co]["geometry"]
            cjf["CityObjects"] = cm.j["CityObjects"][co]
            cjf["drc"] = ""
            collection["features"].append(cjf)
            continue
        hf.cj_to_obj(co_cm, dataset, i)
        cmd = hf.prep_cmd("encode", temppath + "obj/" + dataset + str(i) + ".obj", temppath + "obj/" + dataset + str(i) + ".drc", "-cl 1 -qp 0")
        hf.execute_cmd(cmd)
        drc = open(temppath + "obj/" + dataset + str(i) + ".drc", "rb").read()
        #if len(cm2.j['CityObjects'][co]['geometry']) > 0 and "boundaries" in cm2.j['CityObjects'][co]['geometry'][0]:
        #    del cm2.j['CityObjects'][co]['geometry'][0]['boundaries']
        
        #if len(cm2.j['CityObjects'][co]['geometry']) > 0 and "boundaries" in cm2.j['CityObjects'][co]['geometry'][0]:
        
        
        cjf = {}
        cjf["type"] = "CityJSONFeature"
        cjf["id"] = co
        cjf["CityObjects"] = co_cm.j["CityObjects"]
        cjf["drc"] = drc
        collection["features"].append(cjf)
        
        for geom in cjf["CityObjects"][co]["geometry"]:
            if "boundaries" in geom:
                del geom["boundaries"]

        #if len(cm2.j['CityObjects'][co]['geometry']) > 0:
        #    del cm2.j['CityObjects'][co]['geometry'][0]['boundaries']
        #    cm2.j['CityObjects'][co]['geometry'][0]['draco'] = drc
        #else:
            #cm2.j['CityObjects'][co]['geometry']['draco'] = drc
    
    cbor = flunn.dumps(collection)
    
    cout.write(cbor)
    cout.close()
    
    print("Compression finished")
    """
    
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
method = "cjcollectiondracocborparentchild"

for file in files:
    benchmark = []
    
    dataset = file.split('\\')[-1].split('.')[0]
    columns.append(dataset)
    out = comprout + method + "/" + dataset + "_cjcollectiondracocbor.cbor" 
    
    compress(file, out, dataset)