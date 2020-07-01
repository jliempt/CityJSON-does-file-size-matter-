function buffer(cm){
    var cos = {"CityObjects": {}, "vertices": []};

    if (task == "bufferone"){
        var first_id = Object.keys(cm["CityObjects"])[0];
        cos["CityObjects"][first_id] = cm["CityObjects"][first_id];
    }
    // otherwise it's bufferall
    else{
        // clone cm
        var cos = JSON.parse(JSON.stringify(cm));
        cos["vertices"] = [];
    }

    var vertices_i = -1;

    for (const [key, co] of Object.entries(cos["CityObjects"])) {
        var geometry = co["geometry"];

        for (const [key, geom] of Object.entries(geometry)) {
            var turfGeom = [];
            out = [];

            geom_to_turf(cm["vertices"], geom["boundaries"], turfGeom);

            var points = turf.featureCollection(turfGeom);
            var hull = turf.convex(points);

            // buffer unit = km, we want 1m
            if (hull != null){
            var buf = turf.buffer(hull.geometry, 0.1);
            }
        }

        var t = [];
            buf["geometry"]["coordinates"].forEach(function (v, v_i){
                v.forEach(function (c, j){
                    if (j != 3){
                        vertices_i += 1;
                        t.push(vertices_i)
                        cos["vertices"].push([c[0], c[1], 2])
                    }
                    out.push([t])
                })
            })

        geometry["boundaries"] = [out];
        geometry["type"] = "MultiSurface";
    }
    cm = cos;

    var d = new Date();
    socket.emit('message', [task, d.getTime(), "end"]);
    alert(task);
}

function geom_to_turf(cj_vertices, boundaries, turfGeom){
    try{
        boundaries.forEach(function (b, i){
            if (!Array.isArray(b) || b.length > 4){
                geom_to_turf(cj_vertices, b, turfGeom);
            }
            
            else if (typeof b != "undefined"){
                b.forEach(function (v_is){
                    v_is.forEach(function (v_i){
                        var scale = cm['transform']['scale'];
                        var translate = cm['transform']['translate']

                        var v1 = (cj_vertices[v_i][0] * scale[0] + translate[0])
                        var v2 = (cj_vertices[v_i][1] * scale[1] + translate[1])
                        var v3 = (cj_vertices[v_i][2] * scale[2] + translate[2])
                        var p = [v1, v2, v3];
                        
                        // transform to WGS84 because that's what turf.js takes
                        if (filename == "hdb"){
                            p = singapore_to_wgs(p)
                          }
                          else if (filename == "montreal"){
                            p = canada_to_wgs(p)
                          }
                          else if  (filename == "newyork"){
                              var h = p
                              console.log(h)
                            p = newyork_to_wgs(p);
                            console.log(p)
                          }
                          else if (filename == "zurich"){
                            p = switzerland_to_wgs(p);
                          }
                          else{
                            p = rdnew_to_wgs(p);
                          }
                        turfGeom.push(turf.point(p));
                    })
                })
            }
        })
    }
    catch (ex){
        console.log(ex);
    }
}

function editgeomall(cm, cborData){
    cm["vertices"].forEach(function (v, i){
        v[2] += 1;
    })

    if (method == "originalcborreplace" || method == "originalcborreplacezlib"){
        var cbor = {"geom": cm["vertices"], "cm": cborData["cm"], "attr": cborData["attr"]}
        CBOR.encode(cbor);

        var d = new Date();
        socket.emit('message', [task, d.getTime(), "end"]);
        alert(task);
    }
    else if (method == "originalreplace"){
        var d = new Date();
        socket.emit('message', [task, d.getTime(), "end"]);
        alert(task);
    }
    else if(method == "originalcbor" || method == "originalcborzlib"){
        var cbor = CBOR.encode(cm);

        if (method == "originalcborzlib"){
            pako.deflate(cbor)
        }

        var d = new Date();
        socket.emit('message', [task, d.getTime(), "end"]);
        alert(task);
    }
    else if (method == "originalzlib"){
        pako.deflate(JSON.stringify(cm));

        var d = new Date();
        socket.emit('message', [task, d.getTime(), "end"]);
        alert(task);
    }

    else if (method == "original"){
        var d = new Date();
        socket.emit('message', [task, d.getTime(), "end"]);
        alert(task);
    }

    return cm;
}

function editgeomone(cm, cborData){
    var first_id = Object.keys(cm["CityObjects"])[0];
    var vs_changed = [];
    var geom = cm["CityObjects"][first_id]["geometry"][0];

    heighten_geom(cm, geom["boundaries"], vs_changed)
    


    if (method == "originalcborreplace" || method == "originalcborreplacezlib"){
        var cbor = {"geom": cm["vertices"], "cm": cborData["cm"], "attr": cborData["attr"]}
        CBOR.encode(cbor);

        var d = new Date();
        socket.emit('message', [task, d.getTime(), "end"]);
        alert(task);
    }
    else if (method == "originalreplace"){
        var d = new Date();
        socket.emit('message', [task, d.getTime(), "end"]);
        alert(task);
    }
    else if (method == "originalcbor" || method == "originalcborzlib"){
        var cbor = CBOR.encode(cm);
        if (method == "originalcborzlib"){
            pako.deflate(cbor);
        }

        var d = new Date();
        socket.emit('message', [task, d.getTime(), "end"]);
        alert(task);
    }
    else if (method == "originalzlib"){
        pako.deflate(JSON.stringify(cm));

        var d = new Date();
        socket.emit('message', [task, d.getTime(), "end"]);
        alert(task);
    }
    else if (method == "original"){
        var d = new Date();
        socket.emit('message', [task, d.getTime(), "end"]);
        alert(task);
    }
}

function heighten_geom(cm, boundaries, vs_changed){
    var added_height = 1;

    boundaries.forEach(function (b, i){
        if (typeof b == "array"){
            heighten_geom(cm, b, vs_changed)
        }
        else if (typeof b != "undefined"){
            b.forEach(function (v_i, i){
                if (!v_i in vs_changed){
                    var v = cm["vertices"][v_i];
                    cm["vertices"][v_i] = [v[0], v[1], v[2] + added_height];
                    vs_changed.push(v_i);
                }
            })
        }
    })
}

function calculate_bbox(cm){
    var bbox = [99999999, 99999999, 99999999, 99999999, 99999999, 99999999];

    cm["vertices"].forEach(function (v, index){
        for (var i = 0; i < 3; i++){
            if (v[i] < bbox[i]){
                bbox[i] = v[i];
            }
        }
        for (var i = 0; i < 3; i++){
            if (v[i] > bbox[i+3]){
                bbox[i+3] = v[i];
            }
        }
        if ("transform" in cm){
            for (var i = 0; i < 3; i++){
                bbox[i] = (bbox[i] * cm["transform"]["scale"][i]) + cm["transform"]["translate"][i]
            }
            for (var i = 0; i < 3; i++){
                bbox[i+3] = (bbox[i+3] * cm["transform"]["scale"][i]) + cm["transform"]["translate"][i]
            }
        }
    })
    return bbox;
}

function update_array_indices(a, dOldNewIDs, oldarray, newarray, slicearray){
    a.forEach(function (each, i) {
        if (typeof each == "object"){
            update_array_indices(each, dOldNewIDs, oldarray, newarray, slicearray)
        }
        else if (typeof each != "undefined"){
            if ((slicearray == -1) || (slicearray == 0 && i == 0) || (slicearray == 1 && i > 0) ){
                if (each in dOldNewIDs){
                    a[i] = dOldNewIDs[each]
                }
                else{
                    a[i] = newarray.length;
                    dOldNewIDs[each] = newarray.length;
                    newarray.push(oldarray[each])
                }
            }
        }
    })
}

function queryOne(cm){
    
    var first_id = Object.keys(cm["CityObjects"])[0];

    if (method == "originalcborreplace" || method == "originalcbor" || method == "originalcborreplacezlib" || method == "originalcborzlib" || method == "originalzlib"
        || method == "originalreplace"){
        var co = cm["CityObjects"][first_id];

        var oldnewids = {};
        var newvertices = [];

        var geom = co["geometry"][0]
        update_array_indices(geom["boundaries"], oldnewids, cm["vertices"], newvertices, -1);
        cm["CityObjects"] = [co];
        cm["vertices"] = newvertices;
        cm["metadata"]["geographicalExtent"] = calculate_bbox(cm);
        
        return cm;
    }
}

function queryCm(){
    if (task == "queryone"){
        
        
        var first_id = Object.keys(cm["CityObjects"])[0];

        if (method == "originalcborreplace" || method == "originalcbor" || method == "originalcborreplacezlib" || method == "originalcborzlib" || method == "originalzlib"
            || method == "originalreplace" || method == "original"){
            var co = cm["CityObjects"][first_id];

            var oldnewids = {};
            var newvertices = [];

            var geom = co["geometry"][0]
            update_array_indices(geom["boundaries"], oldnewids, cm["vertices"], newvertices, -1);
            cm["CityObjects"] = [co];
            cm["vertices"] = newvertices;
            cm["metadata"]["geographicalExtent"] = calculate_bbox(cm);

            var d = new Date();
            socket.emit('message', [task, d.getTime(), "end"]);
            alert(task)

            return cm;
        }
        else{
            var d = new Date();
            var timeStart = d.getTime();

            var co = cm["CityObjects"][first_id];

            var d = new Date();
            socket.emit('message', ["queryone", d.getTime() - timeStart, "add"]);

            loadDracoHarp(undefined, first_id, bbox);
        }
    }
    else if (task == "queryall"){
        var d = new Date();
        var timeStart = d.getTime();

        cos = [];
        for (co in cm["CityObjects"]){
            attr = cm["CityObjects"][co]["attributes"]
            if (typeof attr != "undefined" && field in attr){
                if (value == " " || attr[field] == value){
                    cos.push(co);
                }
            }
        }

        var d = new Date();
        
        if (method == "originalcborreplace" || method == "originalcbor" || method == "originalcborreplacezlib" || method == "originalcborzlib" || method == "originalzlib"
            || method == "originalreplace" || method == "original"){
            socket.emit('message', ["queryall", d.getTime(), "end"]);
            alert(task);
        }
        else {
            socket.emit('message', ["queryall", d.getTime() - timeStart, "add"]);
        }

        loadDracoHarp(undefined, undefined, bbox);
    }
    else if (task == "editgeomone"){
        first_id = Object.keys(cm["CityObjects"])[0];
        loadDracoHarp(1, first_id, bbox)
        
    }
    else if (task == "bufferone"){
        first_id = Object.keys(cm["CityObjects"])[0];
        loadDracoHarp(undefined, first_id, bbox, 1)
    }
}

function editCm(cm, task, cborData){
    value = "1";
    if (task == "editall"){
        var d = new Date();
        var timeStart = d.getTime();

        cm_copy = {"CityObjects": []}
        for(co in cm["CityObjects"]){
            cm_copy["CityObjects"][co + value] = cm["CityObjects"][co];


            if (method == "originalcborreplace" || method == "originalcborreplacezlib"){
                var coIndex = cborData["attr"].indexOf(co);
                cborData["attr"][coIndex] = cborData["attr"][coIndex] + value;
            }
            else if (method == "originalreplace"){
                var coIndex = cborData["attr"].indexOf(co);
                cborData["attr"][coIndex] = cborData["attr"][coIndex] + value;
            }
            else if (method == "dracocborreplace" || method == "dracocborreplacezlib" || method == "dracoreplace"){
                var coIndex = cborData["attr"].indexOf(co);
                cborData["attr"][coIndex] = cborData["attr"][coIndex] + value;
            }
        }
        

        if(method == "dracocbor"){
            CBOR.encode(cm_copy);
        }
        else if (method == "dracocborzlib"){
            cm = CBOR.encode(cm_copy);
            pako.deflate(JSON.stringify(cm));
        }
        else if (method == "dracozlib"){
            pako.deflate(JSON.stringify(cm));
        }
        else if (method == "originalcbor" || method == "originalcborzlib"){
            cm["CityObjects"] = cm_copy["CityObjects"];
            var cbor = CBOR.encode(cm_copy);

            if (method == "originalcborzlib"){
                pako.deflate(cbor);
            }

            var d = new Date();
            socket.emit('message', [task, d.getTime(), "end"]);
            alert(task)
        }
        else if (method == "originalzlib"){
            cm["CityObjects"] = cm_copy["CityObjects"];
            pako.deflate(JSON.stringify(cm_copy));

            var d = new Date();
            socket.emit('message', [task, d.getTime(), "end"]);
            alert(task)
        }
        else if (method == "original"){
            var d = new Date();
            socket.emit('message', [task, d.getTime(), "end"]);
            alert(task)
        }
        else if(method == "dracocborreplace" || method == "dracocborreplacezlib"){
            if ( method == method == "dracocborreplacezlib"){
                pako.deflate(data["attr"]);
            }
            CBOR.encode(cborData);
        }

        if(method == "originalcborreplace" || method == "originalcborreplacezlib"){
            if (method == "originalcborreplacezlib"){
                cborData["attr"] = pako.deflate(cborData["attr"]);
            }
            
            var cbor = {"geom": cborData["geom"], "cm": cborData["cm"], "attr": cborData["attr"]}
            CBOR.encode(cbor);
            var d = new Date();
            socket.emit('message', [task, d.getTime(), "end"]);
            console.log(d.getTime())
            alert(task)
        }
        else if (method == "originalreplace"){
            var d = new Date();
            socket.emit('message', [task, d.getTime(), "end"]);
            console.log(d.getTime());
            alert(task)
        }
        else{
            var d = new Date();
            socket.emit('message', ["editall", d.getTime() - timeStart, "add"]);
        }

        loadDracoHarp(undefined, undefined, bbox);
    }

    // else editone
    else{
        var d = new Date();
        var timeStart = d.getTime();
        
        first_id = Object.keys(cm["CityObjects"])[0];
        cm["CityObjects"][first_id + value] = cm["CityObjects"][first_id];
        delete cm["CityObjects"][first_id];

        if(method == "dracocbor"){
            CBOR.encode(cm_copy);
        }
        else if(method == "dracocborreplace" || method == "dracocborreplacezlib"){
            if ( method == method == "dracocborreplacezlib"){
                pako.deflate(data["attr"]);
            }
            CBOR.encode(cborData);
        }
        
        else if (method == "dracocborzlib"){
            cm = CBOR.encode(cm);
            pako.deflate(JSON.stringify(cm));
        }
        else if (method == "dracozlib"){
            pako.deflate(JSON.stringify(cm));
        }


        if (method == "originalcborreplace" || method == "originalcborreplacezlib"){
            var coIndex = cborData["attr"].indexOf(first_id);
            cborData["attr"][coIndex] = cborData["attr"][coIndex] + value;

            if (method == "originalcborreplacezlib"){
                cborData["attr"] = pako.deflate(cborData["attr"]);
            }

            var cbor = {"geom": cborData["geom"], "cm": cborData["cm"], "attr": cborData["attr"]}
            CBOR.encode(cbor);

            var d = new Date();
            socket.emit('message', [task, d.getTime(), "end"]);
            console.log(d.getTime());
            alert(task);
        }
        else if (method == "dracoreplace"){
            var coIndex = cborData["attr"].indexOf(first_id);
            cborData["attr"][coIndex] = cborData["attr"][coIndex] + value;

            var d = new Date();
            socket.emit('message', [task, d.getTime() - timeStart, "add"]);
            alert(task);
        }
        else if (method == "originalreplace" || method == "dracoreplace"){
            var coIndex = cborData["attr"].indexOf(first_id);
            cborData["attr"][coIndex] = cborData["attr"][coIndex] + value;

            var d = new Date();
            socket.emit('message', [task, d.getTime(), "end"]);
            console.log(d.getTime());
            alert(task);
        }
        else if (method == "originalcbor" || method == "originalcborzlib"){
            var cbor = CBOR.encode(cm);

            if(method == "originalcborzlib"){
                pako.deflate(cbor);
            }

            var d = new Date();
            socket.emit('message', [task, d.getTime(), "end"]);
            alert(task)
        }
        else if (method == "originalzlib"){
            pako.deflate(JSON.stringify(cm));

            var d = new Date();
            socket.emit('message', [task, d.getTime(), "end"]);
            alert(task)
        }
        else if (method == "original"){
            var d = new Date();
            socket.emit('message', [task, d.getTime(), "end"]);
            alert(task)
        }

        else{
            var d = new Date();
            socket.emit('message', ["editone", d.getTime() - timeStart, "add"]);
            
            loadDracoHarp(undefined, undefined, bbox);
        }

    }

}

function count_elements(d, elements_count){
    Object.keys(d).forEach(function(k) {
        var v = d[k];
        if (typeof v === "object") {
            if (k in elements_count){
                elements_count[k] += 1;
            }
            else{
                elements_count[k] = 1
            }
            count_elements(v, elements_count);
        }
        else if (typeof v === "array"){
            if (k in elements_count){
                elements_count[k] += 1;
            }
            else{
                elements_count[k] = 1
            }

            //v.forEach(e =>



        }

     });
}