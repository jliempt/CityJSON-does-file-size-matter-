from cjio import cityjson
import helper_functions as hf
import json
from cjio.cityjson import CityJSON

def draco_compress(cmpath, comprout, cmin=None):
    if cmpath != None:
        cm_file = open(cmpath)
        cm = cityjson.reader(file=cm_file, ignore_duplicate_keys=True)
    else:
        cm = cmin
    
    # geometries
    hf.cj_to_obj(cm)
    cmd = hf.prep_cmd("encode", temppath + "temp.obj", temppath + "temp.drc", "-cl 1 -qp 0 --metadata")
    hf.execute_cmd(cmd)
    drc = open(temppath + "temp.drc", "rb").read()
    cout = open(comprout, 'wb')
    
    del cm.j['vertices']
    for co in cm.j['CityObjects']:
        if len(cm.j['CityObjects'][co]['geometry']) > 0 and "boundaries" in cm.j['CityObjects'][co]['geometry'][0]:
            del cm.j['CityObjects'][co]['geometry'][0]['boundaries']
            
            
    delim = "DELIM".encode() # compute shortest string that is not yet in the file? then put that as first word to select as delimiter
    cout.write(str(len(delim) + 1).encode() + delim)
    cout.write(str(cm.j).encode())
    cout.write(delim)
    cout.write(drc)
    
    cout.close()
    
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
    json_str = json.dumps(cm.j, separators=(',',':'))
    fo.write(json_str)
    
    print("Decompression finished")
    
    
    
# folders
with open("paths.json", "r") as paths_json:
    paths = json.load(paths_json)
    temppath = paths["temppath"]
    cmpath = paths["cmpath"]
    comprout = paths["comprout"]
    cmout = paths["cmout"]
            
#draco_compress(cmpath, comprout)
#draco_decompress(cmout, comprout)