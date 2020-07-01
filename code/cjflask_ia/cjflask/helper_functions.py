import re
import subprocess
import shutil
import json

# folders
with open("paths.json", "r") as paths_json:
    paths = json.load(paths_json)
    temppath = paths["temppath"]
    cmpath = paths["cmpath"]
    comprout = paths["comprout"]
    cmout = paths["cmout"]

def obj_to_vf(text):
    """Given a string representing a Wavefront OBJ file, decode to a zmesh.Mesh."""
    vertices = []
    faces = {}
    o_id = ""

    if type(text) is bytes:
      text = text.decode('utf8')
    
    for line in text.split('\n'):
      line = line.strip()
      if len(line) == 0:
        continue
      elif line[0] == '#':
        continue
      elif line[0] == 'f':
        if line.find('/') != -1:
          # e.g. f 6092/2095/6079 6087/2092/6075 6088/2097/6081
          (v1, vt1, vn1, v2, vt2, vn2, v3, vt3, vn3) = re.match(r'f\s+(\d+)/(\d*)/(\d+)\s+(\d+)/(\d*)/(\d+)\s+(\d+)/(\d*)/(\d+)', line).groups()
        else:
          (v1, v2, v3) = re.match(r'f\s+(\d+)\s+(\d+)\s+(\d+)', line).groups()
         # vertex index -1 because OBJ indexing starts at 1
        faces[o_id].append([[int(v1) - 1, int(v2) - 1, int(v3) - 1]])
      elif line[0] == 'o':
          o_id = line[2:]
          if o_id not in faces.keys():
              faces[o_id] = []
              
      elif line[0] == 'v':
        if line[1] == 't': # vertex textures not supported
          # e.g. vt 0.351192 0.337058
          continue 
        else:
          # e.g. v -0.317868 -0.000526 -0.251834
          (v1, v2, v3) = re.match(r'v\s+([-\d\.]+)\s+([-\d\.]+)\s+([-\d\.]+)', line).groups()
          vertices.append([float(v1), float(v2), float(v3)])
    #vertices = np.array(vertices, dtype=np.float32)
    #faces = np.array(faces, dtype=np.uint32)
    
    return vertices, faces
    
    
def cj_to_obj(cm):
    obj = cm.export2obj()
    
    objpath = temppath + "temp.obj"
    
    with open(objpath, "w") as obj_file:
        obj.seek (0)
        shutil.copyfileobj(obj, obj_file)
        
        
def execute_cmd(cmd):
    op = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    R = op.poll()
    if R:
        res = op.communicate()
        raise ValueError(res[1])
    re =  op.communicate()[0]


def prep_cmd(function, fin, fout, params = None):
    dracopath = "../../draco/draco/build/Release/"
    
    cmd = []
    if function == "encode":
        cmd.append(dracopath + "draco_encoder.exe")
    elif function == "decode":
        cmd.append(dracopath + "draco_decoder.exe")
    cmd.append("-i " + fin)
    cmd.append("-o " + fout)
    if params != None:
        cmd.append(params)
    return " ".join(cmd)