// Initialise SocketIO for sending timestamps back to Flask
socket = io();
scene = new THREE.Scene();


function processData(newData){
// Visualisation of prepared CityJSON model
if (method == "original"){
  if (task == "queryone"){
    cm = queryCm(cm);
  }

  else if (task == "queryall"){
    cm = queryCm(cm);
  }
  
  else if (task == "editall" || task == "editone"){
    editCm(cm, task, data);
  }

  else if (task == "editgeomone"){
    editgeomone(cm);
  }

  else if (task == "editgeomall"){
    editgeomall(cm);
  }

  else if (task == "bufferone" || task =="bufferall"){
    buffer(cm);
  }

  else if (task == "decode"){
    var d = new Date();
    socket.emit('message', [task, d.getTime(), "end"]);
    console.log(d.getTime() - decode_start);
    alert(task)
  }

  handleFiles();
  }

else if (method == "originalreplace" || method == "originalreplacezlib"){
  if (task == "decode"){
    var d = new Date();
    var decode_start = d.getTime();
    socket.emit('message', [task, decode_start, "start"]);
  }

  if (method == "originalreplacezlib"){
    newData = pako.inflate(newData);
  }
  // in this case we want a deep copy, because then only either geom or COs need to be compressed again rather than both
  if(task == "editgeomone" || task == "editgeomall" || task == "editall" || task == "editone"){
    var originalCm = JSON.parse(JSON.stringify(newData["cm"]));
  }
  else{
    var originalCm = newData["cm"];
  }
  var attr = newData["attr"]

  /*
  var cm_s = JSON.stringify(cborCm);
  console.log(cborAttr)
  for (const [i, e] of cborAttr.entries()){
    var re = new RegExp('"' + i.toString() + '"', 'g');
    var newVal = '"' + e + '"';
    cm_s = cm_s.replace(re, newVal)
  }
  console.log(JSON.parse(cm_s));
  */
  //console.log(JSON.parse(JSON.stringify(cborCm)));
  // Pop transform/metadata because they don't need to be processed (and would cause errors in replacement functions). Added back later.
  var transform = originalCm["transform"]
  var metadata = originalCm["metadata"]
  delete originalCm["transform"]
  delete originalCm["metadata"]



  cm = replaceValues(originalCm, attr);
  cm = replaceKeys(cm, attr);

  cm["transform"] = transform;
  cm["metadata"] = metadata;
  cm["vertices"] = newData["geom"];

  delete cm["undefined"]
  console.log(JSON.parse(JSON.stringify(cm)))

  if (task == "queryone"){
    cm = queryCm(cm);
  }

  else if (task == "queryall"){
    cm = queryCm(cm);
  }
  
  else if (task == "editall" || task == "editone"){
    editCm(cm, task, newData);
  }

  else if (task == "editgeomone"){
    editgeomone(cm, newData);
  }

  else if (task == "editgeomall"){
    editgeomall(cm, newData);
  }

  else if (task == "bufferone" || task =="bufferall"){
    buffer(cm);
  }

  else if (task == "decode"){
    var d = new Date();
    socket.emit('message', [task, d.getTime(), "end"]);
    alert(task)
  }

  handleFiles();
}
else if (method == "originalcbor" || method == "originalcborzlib" || method == "originalzlib"){
  if (task == "decode"){
    var d = new Date();
    var decode_start = d.getTime();
    socket.emit('message', [task, decode_start, "start"]);
  }

  if (method == "originalcborzlib"){
    // ".buffer" because CBOR needs arraybuffer
    // https://stackoverflow.com/questions/37228285/uint8array-to-arraybuffer
    newData = pako.inflate(newData).buffer;
    cm = CBOR.decode(newData);
  }
  else if (method == "originalcbor"){
    cm = CBOR.decode(newData);
  }
  else if (method == "originalzlib"){
    var decompressed = pako.inflate(newData, { to: "string"});
    cm = JSON.parse(decompressed);
  }

  var cb = JSON.stringify(cm)


  if (task == "queryone"){
    cm = queryCm(cm);
  }

  else if (task == "queryall"){
    cm = queryCm(cm);
  }
  
  else if (task == "editall" || task == "editone"){
    editCm(cm, task, data);
  }

  else if (task == "editgeomone"){
    editgeomone(cm);
  }

  else if (task == "editgeomall"){
    editgeomall(cm);
  }

  else if (task == "bufferone" || task =="bufferall"){
    buffer(cm);
  }

  else if (task == "decode"){
    var d = new Date();
    socket.emit('message', [task, d.getTime(), "end"]);
    console.log(d.getTime() - decode_start);
    alert(task)
  }

  handleFiles();
}
else if (method == "originalcborsmaz"){
  if (task == "decode"){
    var d = new Date();
    var decode_start = d.getTime();
    socket.emit('message', [task, decode_start, "start"]);
  }

  var data = CBOR.decode(newData);
  var transform = data.transform
  delete data.transform
  var metadata = data.metadata
  delete data.metadata
  var vertices = data.vertices
  delete data.vertices

  /*
  function replaceValues(obj) {
    if (typeof obj === 'object') {
      // iterating over the object using for..in
      for (var keys in obj) {
        if (keys == "3,83,208"){
          if (ArrayBuffer.isView(obj[keys])){
            var val = new TextDecoder("utf-8").decode(obj[keys])
            console.log(val)
            console.log(SMAZ.decompress(val));
            //console.log(SMAZ.decompress(obj[keys]))
          }
        }
        //checking if the current value is an object itself
        if (typeof obj[keys] === 'object') {
          // if so then again calling the same function
          replaceValues(obj[keys])
        } 
        /*
        else if (typeof obj[keys] === 'string' || typeof obj[keys] === 'number') {
          // else getting the value and replacing single { with {{ and so on
          let keyValue = cborAttr[parseInt(obj[keys])];
  
          obj[keys] = keyValue;
        }
        
      }
    }
    return obj;
  }

  replaceValues(data)
  */
}
else if (method == "originalcborreplace" || method == "originalcborreplacehuff" || method == "originalcborreplacezlib"){
  if (task == "decode"){
    var d = new Date();
    var decode_start = d.getTime();
    socket.emit('message', [task, decode_start, "start"]);
  }

  var data = CBOR.decode(newData);

  // in this case we want a deep copy, because then only either geom or COs need to be compressed again rather than both
  if(task == "editgeomone" || task == "editgeomall" || task == "editall" || task == "editone"){
    var cborCm = JSON.parse(JSON.stringify(data["cm"]));
  }
  else{
    var cborCm = data["cm"];
  }
  if (method == "originalcborreplacehuff"){
    text = "some text to encode with huffman";
    huffman = Huffman.treeFromText(text); // generate the tree
    treeEncoded = huffman.encodeTree(); // will return an javascript array with tree representation
    treeAgain = Huffman.Tree.decodeTree(treeEncoded); // restore the tree based on array representation
    console.log(treeAgain)
    treeJSON = JSON.stringify(treeEncoded); // get a JSON string for easy transportation

    //var huffman = Huffman.treeFromText("hoihoiho")
    //var t = Huffman.decodeTree(data["huff"])
    //var cborAttr = huffman.decode(data["attr"])
    //console.log(cborAttr);
  }
  else if (method == "originalcborreplacezlib"){
    var cborAttr = pako.inflate(data["attr"])

    var attrStr = new TextDecoder("utf-8").decode(cborAttr)
    var cborAttr = JSON.parse(attrStr)["attr"];

    if(task == "editgeomone" || task == "editgeomall" || task == "editall" || task == "editone"){
      data["attr"] = cborAttr;
    }
  }
  else{
    var cborAttr = data["attr"];
  }
  /*
  var cm_s = JSON.stringify(cborCm);
  console.log(cborAttr)
  for (const [i, e] of cborAttr.entries()){
    var re = new RegExp('"' + i.toString() + '"', 'g');
    var newVal = '"' + e + '"';
    cm_s = cm_s.replace(re, newVal)
  }
  console.log(JSON.parse(cm_s));
  */
  //console.log(JSON.parse(JSON.stringify(cborCm)));
  // Pop transform/metadata because they don't need to be processed (and would cause errors in replacement functions). Added back later.
  var transform = cborCm["transform"]
  var metadata = cborCm["metadata"]
  delete cborCm["transform"]
  delete cborCm["metadata"]

  
  cm = replaceValues(cborCm, cborAttr);
  cm = replaceKeys(cm, cborAttr);

  cm["transform"] = transform;
  cm["metadata"] = metadata;
  cm["vertices"] = data["geom"];

  /*
  if (task != "visualise"){
    var d = new Date();
    socket.emit('message', [task, d.getTime(), "end"]);
  }
*/
  
  if (task == "queryone"){
    cm = queryCm(cm);
  }

  else if (task == "queryall"){
    cm = queryCm(cm);
  }
  
  else if (task == "editall" || task == "editone"){
    editCm(cm, task, data);
  }

  else if (task == "editgeomone"){
    editgeomone(cm, data);
  }

  else if (task == "editgeomall"){
    editgeomall(cm, data);
  }

  else if (task == "bufferone" || task =="bufferall"){
    buffer(cm);
  }

  else if (task == "decode"){
    var d = new Date();
    socket.emit('message', [task, d.getTime(), "end"]);
    console.log(d.getTime() - decode_start);
    alert(task)
  }

  handleFiles();
}

else if (method == "draco" || method == "dracocbor" || method == "dracocborzlib" || method == "dracocborreplace" || method == "dracozlib" || method == "dracocborreplacezlib" || method == "dracoreplace"){
  if (task == "decode"){
    var d = new Date();
    socket.emit('message', [task, d.getTime(), "start"]);
  }
  
  if (method == "draco" || method == "dracozlib"){
    if (method == "dracozlib"){
      newData = pako.inflate(newData, { to: "string"});
    }
    // Decompose compressed file
    var compr = newData;
    var delimlen = parseInt(compr[0]);
    var delim = compr.slice(1, delimlen);
    var comprsplit = compr.split(delim);
    var cm_s = comprsplit[1];
    
    //var drc_s = comprsplit[2];
    
    cm = JSON.parse(cm_s);
  }
  else if (method == "dracocborzlib"){
    newData = pako.inflate(newData).buffer;
    cm = CBOR.decode(newData);
  }
  else if (method == "dracocbor"){
    console.log(newData);
    cm = CBOR.decode(newData);
  }
  else if (method == "dracocborreplace" || method == "dracocborreplacezlib"){
    //console.log(newData)
    var data = CBOR.decode(newData);
    var cborCm = data["cm"];
    if (method == "dracocborreplacezlib"){
      var cborAttr = pako.inflate(data["attr"])

      var attrStr = new TextDecoder("utf-8").decode(cborAttr)
      var cborAttr = JSON.parse(attrStr)["attr"];
    }
    else{
      var cborAttr = data["attr"];
    }

  // Pop transform/metadata because they don't need to be processed (and would cause errors in replacement functions). Added back later.
  var transform = cborCm["transform"]
  var metadata = cborCm["metadata"]
  delete cborCm["transform"]
  delete cborCm["metadata"]

  cm = replaceValues(cborCm, cborAttr);
  cm = replaceKeys(cborCm, cborAttr);

  cm["transform"] = transform;
  cm["metadata"] = metadata;
  }
  else if (method == "dracoreplace"){
    var data = newData;
    cm = newData["cm"]
    
    var attr = newData["attr"];

    // Pop transform/metadata because they don't need to be processed (and would cause errors in replacement functions). Added back later.
    var transform = cm["transform"]
    var metadata = cm["metadata"]
    delete cm["transform"]
    delete cm["metadata"]

    cm = replaceValues(cm, attr);
    cm = replaceKeys(cm, attr);

    cm["transform"] = transform;
    cm["metadata"] = metadata;
  }
  
  bbox = get_bbox(cm);

  if("transform" in cm){
    scale = cm['transform']['scale'];
    translate = cm['transform']['translate'];
  }
  else{
    scale = [0, 0, 0];
    translate = [0, 0, 0];
  }

  var d = new Date();
  socket.emit('message', [task, d.getTime(), "end"]);

  if (task == "visualise" || task == "decode"){
    loadDracoHarp(undefined, undefined, bbox);
  }

  else if (task == "queryone"){
    cm = queryCm(cm);
  }

  else if (task == "queryall"){
      cm = queryCm(cm);
  }

  else if (task == "editall" || task == "editone"){
      editCm(cm, task, data)
  }

  else if (task == "editgeomall"){
    loadDracoHarp(1, undefined, bbox);
  }

  else if (task == "editgeomone"){
      queryCm(cm, task, data)
  }

  else if (task == "bufferall"){
    loadDracoHarp(undefined, "all", bbox, task);
  }

  else if (task == "bufferone"){
    cm = queryCm(cm);
  }
  
}

}
  
function initViewer(){
  
  // Loading harp.gl map
  const canvas = document.getElementById('map');
  map = new harp.MapView({
     canvas,
     //theme: "../../static/harpgltheme.json",
     theme: "https://unpkg.com/@here/harp-map-theme@latest/resources/berlin_tilezen_night_reduced.json",
     //For tile cache optimization:
     maxVisibleDataSourceTiles: 40, 
     tileCacheSize: 100
  });
  
  const mapControls = new harp.MapControls(map);
  const ui = new harp.MapControlsUI(mapControls);
  canvas.parentElement.appendChild(ui.domElement);
  
  mapControls.maxPitchAngle = 90;
  
  map.resize(window.innerWidth, window.innerHeight);
  window.onresize = () => map.resize(window.innerWidth, window.innerHeight);
  
  const omvDataSource = new harp.OmvDataSource({
     baseUrl: "https://xyz.api.here.com/tiles/herebase.02",
     apiFormat: harp.APIFormat.XYZOMV,
     styleSetName: "tilezen",
     authenticationCode: 'ACrmXbstQJO4gKaVpEWNIAA',
  });
  map.addDataSource(omvDataSource);
}

// https://stackoverflow.com/questions/49962490/replace-all-object-values-recursively
function replaceValues(obj, cborAttr) {
  if (typeof obj === 'object') {
    // iterating over the object using for..in
    for (var keys in obj) {
      if (keys == "boundaries"){
        return;
      }
      //checking if the current value is an object itself
      else if (typeof obj[keys] === 'object') {
        // if so then again calling the same function
        replaceValues(obj[keys], cborAttr)
      } 

      else if (typeof obj[keys] === 'string' || typeof obj[keys] === 'number') {
        let keyValue = cborAttr[parseInt(obj[keys])];

        obj[keys] = keyValue;
      }
    }
  }
  return obj;
}

  // https://stackoverflow.com/questions/19752516/renaming-object-keys-recursively
  function replaceKeys(o, cborAttr){
    var build, key, destKey, ix, value;

    build = {};
    for (key in o) {
        // Get the destination key
        destKey = cborAttr[parseInt(key)]
        // Get the value
        value = o[key];

        // If this is an object, recurse
        if (typeof value === "object") {
          if (key == "boundaries"){
            build["boundaries"] = value;
            return build;
          }
          // because this would be [0] from "geometry" and not [0] in cborAttr
          else if (key == 0){
            destKey = 0
            value = replaceKeys(value, cborAttr);
            
          }
          else{
            value = replaceKeys(value, cborAttr);
          }
        }

        // Set it on the result using the destination key
        build[destKey] = value;
    }
    return build;
}