from cjflask import app
from flask import send_file, render_template
from flask_socketio import SocketIO

import json
import os
import time
import copy
import sys

from cjio.cityjson import CityJSON
from cjio import cityjson, subset
from shapely import geometry
from shapely.ops import triangulate

#sys.path.append("../compression")
#import draco_only

# to store arrays of corresponding start and end times
start = {}
end = {}
# for report filename (e.g. visualise, analysis, querying)
task_name = ""
# for report filename (e.g. original, draco, attributes_only, huffman)
method_name = ""
# for report filename
dataset_name = ""

# number of iterations for test
test_i = 10
# to retrieve time in milliseconds
ms_time = lambda: int(round(time.time() * 1000))
    
# outputs report after test_i is met
def create_report():
    global start, task_name
    fn = "../../benchmark/" + method_name + "/" + method_name + "_" + dataset_name + ".json"
    # if the benchmark file already exists, update it
    if os.path.exists(fn):
        
        f = open(fn)
        j = json.load(f)
        f.close()
        
        for k in start.keys():
            j[k] = start[k]
        
        
        f = open(fn, "w")
        json.dump(j, f)
        
        

    else:
        f = open(fn, "w")
        json.dump(start, f)

    print("Report created at %s" %fn)
    
    start = {}
    

# to receive end time message from JavaScript
# SocketIO will keep on running and catch all messages sent from JS
socketio = SocketIO(app)
socketio.run(app)

@socketio.on('message')
def handle_message(message):  
    # in this case message comes from JS and has final time rather than start or end
    if len(message) == 3:
        if message[0] == task_name:
            print(message)
            if message[2] == "start":
                if task_name not in start.keys():
                    start[task_name] = [message[1]]
                else:
                    start[task_name].append(message[1])
            elif message[2] == "end":
                start[task_name][-1] = int(message[1]) - start[task_name][-1]
                
                # print current test iteration info
                print(len(start[task_name]), str(start[task_name][-1]) + "ms", task_name, method_name)
                
            # here we have segmented timing, transmission time has already been processed in above way, 
            # this part will add the time of task itself to that
            elif message[2] == "add":
                print(message[1])
                print(start[task_name][-1])
                print(len(start[task_name]), str(start[task_name][-1]) + "ms", task_name, method_name)
                start[task_name][-1] += int(message[1])
                print(len(start[task_name]), str(start[task_name][-1]) + "ms", task_name, method_name)
        
    print(start)

# to simulate receiving message but within python
def end_time(message):
        if message[0] == task_name: # otherwise a message for a different task is received
            start[task_name][-1] = int(message[1]) - start[task_name][-1]
            
            # if there have been test_i iterations, output results
            # in the mean time, print current iteration number
            print(len(start[task_name]), str(start[task_name][-1]) + "ms", task_name, method_name)

#=== start of Flask routes
@app.route('/report/')
def cmd_report():
    create_report()
    return render_template("overview.html")


@app.route('/collections/<filename>/query/<field>/<value>/<method>')
def cmd_query(filename, field, value, method):
    global task_name, method_name, dataset_name
    if value == " ":
        task_name = "queryall"

    method_name = method
    dataset_name = filename
    
    """
    if method == "original":
        # start measuring time
        if task_name not in start.keys():
            start[task_name] = [ms_time()]
        else:
            start[task_name].append(ms_time())
            
        cmf = getcm(filename)
        cm = cityjson.reader(file=cmf, ignore_duplicate_keys=True)
        if cm == None:
            return render_template("wrongdataset.html")
        else:        
            cm2 = query_cj(cm, field, value)
            
            f = open('../../datasets/task/' + filename + "_" + task_name + '.json', 'w')

            json.dump(cm2.j, f)
                
            return render_template("visualisation.html", method=method, task=task_name, filename=filename)


    elif method == "draco" or method == "dracozlib" or method == "dracocbor" or method == "dracoreplace" or method == "dracocborzlib" or method == "dracocborreplace" or method == "dracocborreplacezlib" or method == "originalreplace" or method == "originalreplacezlib" or method == "originalcborreplace" or method == "originalcbor" or method == "originalzlib" or method == "originalcborzlib" or method == "originalcborreplacezlib" or method == "originalcborreplacehuff" or method == "originalcborsmaz":
        """
    # start measuring time
    if task_name not in start.keys():
        start[task_name] = [ms_time()]
    else:
        start[task_name].append(ms_time())
        
    return render_template("visualisation.html", filename=filename, task=task_name, method=method, field=field, value=value)
    
    
@app.route('/collections/<filename>/index/<index>/<method>')
def cmd_by_index(filename, index, method):
    global task_name, method_name, dataset_name

    task_name = "queryone"
    method_name = method
    dataset_name = filename
    
    """
    if method == "original":
        # start measuring time
        if task_name not in start.keys():
            start[task_name] = [ms_time()]
        else:
            start[task_name].append(ms_time())
            
        cmf = getcm(filename)
        cm = cityjson.reader(file=cmf, ignore_duplicate_keys=True)
        if cm == None:
            return render_template("wrongdataset.html")
        else:        
            cm2, co = co_by_index(cm, index)
            return render_template("visualisation.html", cm=cm2.j, method=method, task=task_name)
    elif method == "draco" or method == "dracozlib" or method == "dracocbor" or method == "dracoreplace" or method == "dracocborzlib" or method == "dracocborreplace" or method == "dracocborreplacezlib" or method == "originalreplace" or method == "originalreplacezlib" or method == "originalcborreplace" or method == "originalcbor" or method == "originalzlib" or method == "originalcborzlib" or method == "originalcborreplacezlib" or method == "originalcborreplacehuff" or method == "originalcborsmaz":
        """
    # start measuring time
    if task_name not in start.keys():
        start[task_name] = [ms_time()]
    else:
        start[task_name].append(ms_time())
    return render_template("visualisation.html", mimetype='text/xml', filename=filename, task=task_name, method=method)
    
    
@app.route('/collections/<filename>/<index>/edit/attributes/<field>/<operation>/<value>/<method>')
def cmd_edit_attr(filename, index, field, operation, value, method):
    global task_name, method_name, dataset_name
    method_name = method
    dataset_name = filename
    
    """
    if method == "original":
        cmf = getcm(filename)
        cm = cityjson.reader(file=cmf, ignore_duplicate_keys=True)
        if cm == None:
            return render_template("wrongdataset.html")
        else:       
            if method == "original":
                if operation == "append":
                    # for all objects
                    if index == "all":
                        task_name = "editall"
                        # start measuring time
                        if task_name not in start.keys():
                            start[task_name] = [ms_time()]
                        else:
                            start[task_name].append(ms_time())
                            
                        cm2 = copy.copy(cm)
                        cm2.j["CityObjects"] = {}
                        for co in cm.j["CityObjects"]:
                            cm2.j["CityObjects"][co + value] = cm.j["CityObjects"][co]
                            
                        f = open('../../datasets/task/' + filename + "_" + task_name + '.json', 'w')
                        json.dump(cm2.j, f)
                        
                        return render_template("visualisation.html", method=method, task=task_name, filename=filename)
                            
                    # for one object
                    else:
                        task_name = "editone"
                        # start measuring time
                        if task_name not in start.keys():
                            start[task_name] = [ms_time()]
                        else:
                            start[task_name].append(ms_time())

                        co = list(cm.j["CityObjects"].keys())[int(index)]
                        
                        cm.j["CityObjects"][co + value] = cm.j["CityObjects"].pop(co)
                        
                        f = open('../../datasets/task/' + filename + "_" + task_name + '.json', 'w')
                        json.dump(cm.j, f)
                    
                        return render_template("visualisation.html", cm=str(cm.j), method=method, task=task_name)
        
    elif method == "draco" or method == "dracozlib" or method == "dracocbor" or method == "dracoreplace" or method == "dracocborzlib" or method == "dracocborreplace" or method == "dracocborreplacezlib" or method == "originalcborreplace" or method == "originalreplace" or method == "originalreplacezlib" or method == "originalcbor" or method == "originalzlib" or method == "originalcborzlib" or method == "originalcborreplacezlib" or method == "originalcborreplacehuff" or method == "originalcborsmaz":
        """
    if index == "all":
        task_name = "editall"
    else:
        task_name = "editone"
        
    # start measuring time
    if task_name not in start.keys():
        start[task_name] = [ms_time()]
    else:
        start[task_name].append(ms_time())

    return render_template("visualisation.html", filename=filename, task=task_name, method=method, field=field, value=value, start=start)
        


@app.route('/collections/<filename>/buffer/<index>/<method>')
def cmd_buffer(filename, index, method):
    global task_name, method_name, dataset_name

    method_name = method
    dataset_name = filename
    
    """
    if method == "original":
        cmf = getcm(filename)
        cm = cityjson.reader(file=cmf, ignore_duplicate_keys=True)
        if cm == None:
            return render_template("wrongdataset.html")
        else:
            # buffer first object
            if index == "0":
                task_name = "bufferone"
            
                # get CityObject
                cm2, co_id = co_by_index(cm, 0)
                
                
                # start measuring time
                if task_name not in start.keys():
                    start[task_name] = [ms_time()]
                else:
                    start[task_name].append(ms_time())
                
                # restore original coordinates
                cm2.decompress()
                
                # remove all vertices since we'll get new coordinates, store old ones in list
                cj_vertices = cm2.j["vertices"]
                cm2.j["vertices"] = []
                vertices_i = -1
                
                
                for geom in cm2.j["CityObjects"][co_id]["geometry"]:
                    geom_2d = []
                    geom_to_shapely(cj_vertices, geom["boundaries"], geom_2d)
                    geom_2d.append(geom_2d[0])
                    
                    p = geometry.Polygon(geom_2d).convex_hull

                    buf = p.buffer(1.0)
                    #buf_triangles = triangulate(buf)
                    out = []
                    geom["boundaries"] = [[]]
                    #print(buf_triangles)
                    #for triangle in buf_triangles:
                    t = []
                    t_i = []
                    for v_i, v in enumerate(list(buf.exterior.coords)):
                        if v_i != 3:
                            v = list(v)
                            vertices_i += 1
                            t.append(vertices_i)
                            cm2.j["vertices"].append([v[0], v[1], 2])   
                    out.append([t])
                        
                    geom["boundaries"] = out
                    geom["type"] = "MultiSurface"
                    
                    # gives an error with RotterdamLod1LoD2, probably because geometry part is complicated
                    #try:
                    #    cm2.remove_duplicate_vertices()
                    #except:
                    #    pass
                    
                return render_template("visualisation.html", cm=str(cm2.j), method=method, task=task_name)
                
            # buffer all objects
            else:
                task_name = "bufferall"
                
                cm2 = copy.copy(cm)
                # restore original coordinates
                cm2.decompress()
                
                # start measuring time
                if task_name not in start.keys():
                    start[task_name] = [ms_time()]
                else:
                    start[task_name].append(ms_time())

                # remove all vertices since we'll get new coordinates, 
                # store old ones in list
                vertices_i = -1
                cj_vertices = cm2.j["vertices"]
                cm2.j["vertices"] = []
                
                polys = []
                
                for co in cm2.j["CityObjects"]:
                    for geom in cm2.j["CityObjects"][co]["geometry"]:
                        geom_2d = []
                        geom_to_shapely(cj_vertices, geom["boundaries"], geom_2d)
                        geom_2d.append(geom_2d[0])
                        
                        p = geometry.Polygon(geom_2d).convex_hull
                        buf = p.buffer(1.0)
                        
                        polys.append(buf)
                        
                        #buf_triangles = triangulate(buf)
                        
                        out = []
                        geom["boundaries"] = [[]]
                        
                        #for triangle in buf_triangles:
                        t = []
                        t_i = []
                        for v_i, v in enumerate(list(buf.exterior.coords)):
                            if v_i != 3:
                                v = list(v)
                                vertices_i += 1
                                t.append(vertices_i)
                                cm2.j["vertices"].append([v[0], v[1], 2])
                        out.append([t])

                        geom["boundaries"] = out               
                        geom["type"] = "MultiSurface"
                #cm2.remove_duplicate_vertices()
                
                f = open('../../datasets/task/' + filename + "_" + task_name + '.json', 'w')

                json.dump(cm2.j, f)
                
                return render_template("visualisation.html", method=method, task=task_name, filename=filename)

    
    elif method == "draco" or method == "dracozlib" or method == "dracocbor" or method == "dracoreplace" or method == "dracocborzlib" or method == "dracocborreplace" or method == "dracocborreplacezlib" or method == "originalcborreplace" or method == "originalreplace" or method == "originalreplacezlib" or method == "originalcbor" or method == "originalzlib" or method == "originalcborzlib" or method == "originalcborreplacezlib" or method == "originalcborreplacehuff" or method == "originalcborsmaz":
        """
    if index == "0":
        task_name = "bufferone"
    else:
        task_name = "bufferall"
        
    # start measuring time
    if task_name not in start.keys():
        start[task_name] = [ms_time()]
    else:
        start[task_name].append(ms_time())
        
    return render_template("visualisation.html", filename=filename, method=method, task=task_name)
        

@app.route('/collections/<filename>/visualise/<method>')
def cmd_visualise(filename, method):
    global task_name, method_name, dataset_name
    # for test report name
    task_name = "visualise"
    method_name = method
    dataset_name = filename

    """
    if method == "original":
        # start measuring time
        if task_name not in start.keys():
            start[task_name] = [ms_time()]
        else:
            start[task_name].append(ms_time())

        #cmf = getcm(filename)
        #cm = cityjson.reader(file=cmf, ignore_duplicate_keys=True)

        #if cm == None:
        #    return render_template("wrongdataset.html") 
        return render_template("visualisation.html", filename=filename, method=method, task=task_name)
        
    elif (method == "draco" or method == "dracozlib" or method == "dracocbor" or method == "dracoreplace" or method == "dracocborzlib" or method == "dracocborreplace" or method == "dracocborreplacezlib" or method == "originalcborreplace" or method == "originalreplace" or method == "originalreplacezlib" or method == "originalcborzlib" or method == "originalcborreplacehuff" 
          or method == "originalcbor" or method == "originalzlib" or method == "originalcborreplacezlib" or method == "originalcborsmaz"):
        """
    # start measuring time
    if task_name not in start.keys():
        start[task_name] = [ms_time()]
    else:
        start[task_name].append(ms_time())
    print(start)
    

    return render_template("visualisation.html", filename=filename, method=method, task=task_name, start=start)
    
@app.route('/collections/<filename>/decode/<method>')
def cmd_decode(filename, method):
    global task_name, method_name, dataset_name
    # for test report name
    task_name = "decode"
    method_name = method
    dataset_name = filename
        

    return render_template("visualisation.html", filename=filename, method=method, task=task_name, start=start)

# is used to download compressed CJ files because having Flask send a blob is troublesome
@app.route('/download/<filename>/<method>/<task>')
def download(filename, method, task):
    # download draco geom only
    if method == "drc":
        if "_" in filename:
            filename = filename.split("_")[0]
        p = '../../../datasets/drc/' + filename + ".drc"
        f = open(p, "rb")
        return send_file(f, attachment_filename=filename + ".drc")
    # download citymodels
    cm = getcm(filename, method, task)
    
    """
    if method == "original":
        return send_file(cm, attachment_filename=filename + ".json")
    else:
        """
    return send_file(cm, attachment_filename=filename + "_" + method + ".txt")

    
# heighten all vertices by 1 metre
@app.route('/collections/<filename>/heighten/<co>/<method>')
def cmd_heighten(filename, co, method):
    global task_name, method_name, dataset_name
    
    # for test report name
    method_name = method
    dataset_name = filename
    
    """
    if method == "original":
        cmf = getcm(filename)
        cm = cityjson.reader(file=cmf, ignore_duplicate_keys=True)
        if cm == None:
            return render_template("wrongdataset.html")
        else:        
            cm2 = copy.copy(cm)
            
            vs_changed = []
            if co == "all":
                task_name = "editgeomall"
                print("start " + task_name)
                # start measuring time
                if task_name not in start.keys():
                    start[task_name] = [ms_time()]
                else:
                    start[task_name].append(ms_time())
            
                for v in cm2.j["vertices"]:
                    v[2] += 1
                        
                f = open('../../datasets/task/' + filename + "_" + task_name + '.json', 'w')
                json.dump(cm2.j, f)
                print(task_name + " saved")
                return render_template("visualisation.html", method=method, task=task_name, filename=filename)
            
            else:
                task_name = "editgeomone"
                # start measuring time
                if task_name not in start.keys():
                    start[task_name] = [ms_time()]
                else:
                    start[task_name].append(ms_time())
                    
                for geom in cm2.j["CityObjects"][co]["geometry"]:
                    heighten_geom(cm2, geom["boundaries"], vs_changed)
            
                return render_template("visualisation.html", cm=str(cm2.j), method=method, task=task_name)
        
    elif method == "draco" or method == "dracozlib" or method == "dracocbor" or method == "dracoreplace" or method == "dracocborzlib" or method == "dracocborreplace" or method == "dracocborreplacezlib" or method == "originalcborreplace" or method == "originalreplace" or method == "originalreplacezlib" or method == "originalcbor" or method == "originalzlib" or method == "originalcborzlib" or method == "originalcborreplacezlib" or method == "originalcborreplacehuff" or method == "originalcborsmaz":
        """
    if co == "all":
        task_name = "editgeomall"
    else:
        task_name = "editgeomone"
        
    # start measuring time
    if task_name not in start.keys():
        start[task_name] = [ms_time()]
    else:
        start[task_name].append(ms_time())
        
    return render_template("visualisation.html", filename=filename, method=method, task=task_name)
    
    

#=== Flask routes end here
        
def getcm(filename, compression=None, task=None):
    if compression == None or compression == "original":
        #if task == "visualise" or task == None:
        p = '../../../datasets/' + "original/" + filename + '.json'
        #else:
            #p = '../../datasets/task/' + filename + "_" + task + '.json'
        if os.path.isfile(p) == False:
            return None
        f = open(p, "rb")
        return f
    else:
        if compression == "draco" or compression == "dracoreplace":
            fextension = ".txt"
        elif (compression == "dracocbor" or compression == "dracocborzlib" or compression == "dracocborreplace" or compression == "dracocborreplacezlib" or compression == "originalcborreplace" or compression == "originalreplace" or compression == "originalreplacezlib" or compression == "originalcbor" or compression == "originalcborzlib" or compression == "originalcborreplacehuff" or compression == "originalcborsmaz"
            or compression == "originalcborreplacezlib"):
            fextension = ".cbor"
        elif compression == "originalzlib" or compression == "dracozlib":
            fextension = ".zlib"
        
        p = '../../../datasets/' + compression + "/" + filename + "_" + compression + fextension
        print(p)
        if os.path.isfile(p) == False:
            return None
        f = open(p, "rb")
        return f
    
def heighten_geom(cm, boundaries, vs_changed):   
    added_height = 1
    for b in boundaries:
        if any(isinstance(i, list) for i in b):
            heighten_geom(cm, b, vs_changed)
        elif b is not None:
            for v_i in b:
                if v_i not in vs_changed:
                    v = cm.j["vertices"][v_i]
                    cm.j["vertices"][v_i] = [v[0], v[1], v[2] + added_height]
                    vs_changed.append(v_i)

def query_cj(cm, field, value): 
    ids = []
    for co in cm.j["CityObjects"]:
        try:
            attr = cm.j["CityObjects"][co]["attributes"]
            if field in attr:
                if value == " " or attr[field] == value:
                    ids.append(co)
        except:
            ids.append(co)
    return(cm.get_subset_ids(ids))
    
def co_by_index(cm, index):
    index = int(index)
    cm2 = CityJSON()
    #-- copy selected CO to the j2
    co = list(cm.j["CityObjects"].keys())[index]
    cm2.j["CityObjects"][co] = cm.j["CityObjects"][co]
    #-- geometry
    subset.process_geometry(cm.j, cm2.j)
    #-- templates
    #subset.process_templates(cm.j, cm2.j)
    #-- appearance
    #if ("appearance" in cm.j):
    #    cm2.j["appearance"] = {}
    #    subset.process_appearance(cm.j, cm2.j)
    #-- metadata
    if ("metadata" in cm.j):
        cm2.j["metadata"] = cm.j["metadata"]
    #-- transform
    if ("transform" in cm.j):
        cm2.j["transform"] = cm.j["transform"]
    cm2.update_bbox()
    return cm2, co

def geom_to_shapely(cj_vertices, boundaries, geom_2d):
    for b in boundaries:
        if any(isinstance(i, list) for i in b):
            geom_to_shapely(cj_vertices, b, geom_2d)
        elif b is not None:
            for v_i in b:
                v = cj_vertices[v_i]
                geom_2d.append([v[0], v[1]])