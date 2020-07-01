function loadDracoHarp(edit, query, bbox, buffer){
      
  edit_value = 0;
  if (typeof edit == 1){
    edit_value = 1;
  }
  else{
    edit_value = 0;
  }

  var d = new Date();
  timeStartVis = d.getTime();

  // Instantiate a loader
  THREE.DRACOLoader.setDecoderPath( '/static/etc' );
  THREE.DRACOLoader.setDecoderConfig( { type: 'js' } );
  var loader = new THREE.DRACOLoader();



  // Load a Draco geometry
  loader.load(
    // resource URL
    "http://127.0.0.1:5000/download/" + filename + "/" + "drc" + "/" + "none",
    // to-be-queried id
    query,
    // called when the resource is loaded
    function ( geometry ) {
      var helftx = (bbox[3] - bbox[0]) / 2;
      var helfty = (bbox[4] - bbox[1]) / 2;

      mid = bbox_mid(bbox);
      mid_wgs = rdnew_to_wgs(mid);

      map.setCameraGeolocationAndZoom(
        new harp.GeoCoordinates(mid_wgs[1], mid_wgs[0]),
        16
     );
        // in this case don't normalise coordinates, because we're going to transform them to WGS84
        if (task == "bufferall" || task == "bufferone"){
          bbox = [0, 0, 0];
          helftx = 0;
          helfty = 0;
        }
      //var d = new Date();
      //var timeStart = d.getTime();

      for(var i = 0; i < geometry['attributes']['position']['array'].length; i++){
        
        c = geometry['attributes']['position']['array'][i];
        if(i % 3 == 0){
          geometry['attributes']['position']['array'][i] = (c * scale[0] + translate[0]) - bbox[0] - helftx;
        }
        else if(i % 3 == 1){
          geometry['attributes']['position']['array'][i] = (c * scale[1] + translate[1]) - bbox[1] - helfty;
        }
        else {
          geometry['attributes']['position']['array'][i] = (c * scale[2] + translate[2]) + edit_value;
        }
      }

      if( task == "editgeomone" || task == "editgeomall"){
        const mesh = {
          indices : new Uint32Array(geometry['index']['array']),
          vertices : new Float32Array(geometry['attributes']['position']['array'])
        };
        const encoderModule = DracoEncoderModule();
        const encoder = new encoderModule.Encoder();
        const meshBuilder = new encoderModule.MeshBuilder();
        const dracoMesh = new encoderModule.Mesh();

        const numFaces = mesh.indices.length / 3;
        const numPoints = mesh.vertices.length;
        meshBuilder.AddFacesToMesh(dracoMesh, numFaces, mesh.indices);
        meshBuilder.AddFloatAttributeToMesh(dracoMesh, encoderModule.POSITION,
          numPoints, 3, mesh.vertices);

        encoder.SetEncodingMethod(encoderModule.MESH_EDGEBREAKER_ENCODING);

        const encodedData = new encoderModule.DracoInt8Array();
        // Use default encoding setting.
        const encodedLen = encoder.EncodeMeshToDracoBuffer(dracoMesh,
                                                          encodedData);
        encoderModule.destroy(dracoMesh);
        encoderModule.destroy(encoder);
        encoderModule.destroy(meshBuilder);
      }
      
      var d = new Date();
      socket.emit('message', ["editgeomall", d.getTime() - timeStartVis, "add"]);
      socket.emit('message', ["editgeomone", d.getTime() - timeStartVis, "add"]);

      if (buffer != undefined && query != "all"){
        //var d = new Date();
        //var timeStart = d.getTime();

        var points = [];

        for(var i = 0; i < geometry.index.array.length; i++){
          var indices = geometry.index.array
          var positions = geometry.attributes.position.array;
          var p = [positions[indices[i]*3], positions[indices[i]*3 + 1]];

          // transform coordinates to WGS84 because that's what turf.js takes
          if (filename == "hdb"){
            p = singapore_to_wgs(p)
          }
          else if (filename == "montreal"){
            p = canada_to_wgs(p)
          }
          else if  (filename == "newyork"){
            p = newyork_to_wgs(p);
          }
          else if (filename == "zurich"){
            p = switzerland_to_wgs(p);
          }
          else{
            p = rdnew_to_wgs(p);
          }
          points.push(turf.point(p));
        }
        points = turf.featureCollection(points);

        var hull = turf.convex(points);

        // buffer unit = km, we want 1m
        if (hull != null){
          var buf = turf.buffer(hull.geometry, 0.1);
        }

        var indices = [];
        var positions = [];

        buf["geometry"]["coordinates"].forEach(function (c, j){
          indices.push(c);
          positions.push(j);
        })

        var d = new Date();
        socket.emit('message', ["bufferone", d.getTime() - timeStartVis, "add"]);
      }
        
    
      var material = new THREE.MeshLambertMaterial();

      var mesh = new THREE.Mesh( geometry, material );
      mesh.geoPosition = new harp.GeoCoordinates(mid_wgs[1], mid_wgs[0]);
      mesh.castShadow = true;
      mesh.receiveShadow = true;
      map.mapAnchors.add(mesh);
      map.update();

    // send time message to Flask app through SocketIO
    var d = new Date();
    socket.emit('message', ["visualise", d.getTime() - timeStartVis, "add"]);
    if (task != "bufferall" && task != "decode"){
      alert(task);
    }
    },
    // called as loading progresses
    function ( xhr ) {

      console.log( ( xhr.loaded / xhr.total * 100 ) + '% loaded' );

    },
    // called when loading has errors
    function ( error ) {
      console.log( 'An error happened' );

    }
  );
}


// https://github.com/google/draco/blob/master/javascript/example/webgl_loader_draco.html
function queryOneDraco(){
  
  var fl = new THREE.FileLoader();
  fl.load('/static/temp.drc', function(drc){
      // Create the Draco decoder.
  const decoderModule = DracoDecoderModule();
  const buffer = new decoderModule.DecoderBuffer();
  //console.log(drc_s);
  var byteArray = drc;

  buffer.Init(drc, drc.byteLength);

  // Create a buffer to hold the encoded data.
  const decoder = new decoderModule.Decoder();

  // Decode the encoded geometry.
  let dracoGeometry;
  let status;
  dracoGeometry = new decoderModule.Mesh();

  status = decoder.DecodeBufferToMesh(buffer, dracoGeometry);

  const subObjAttributeId = decoder.GetAttributeIdByName(dracoGeometry, 'sub_obj');
  // get the sub object attribute, and related data
  let subObjAttribute = null;
  let subObjAttributeData = null;
  if (subObjAttributeId !== -1) {
      subObjAttribute = decoder.GetAttribute(dracoGeometry, subObjAttributeId);
      subObjAttributeData = new dracoDecoder.DracoFloat32Array();
      decoder.GetAttributeFloatForAllPoints(dracoGeometry, subObjAttribute, subObjAttributeData);
  }

  // Query the attributes metadata
  const attributeMetadata = decoder.GetAttributeMetadata(dracoGeometry, subObjAttributeId);
  const metadataQ = new decoderModule.MetadataQuerier();

  let face = new decoderModule.DracoInt32Array();
  for (let i = 0; i < dracoGeometry.num_faces(); i++) {
      decoder.GetFaceFromMesh(dracoGeometry, i, face);
      const subObjIndex = subObjAttributeData.GetValue(face.GetValue(0));
      const subObjectName = metadataQ.GetEntryName(attributeMetadata, subObjIndex);
      console.log(`Sub object name : ${subObjectName} for face with index ${i}`)
  }

  // You must explicitly delete objects created from the DracoDecoderModule
  // or Decoder.
  decoderModule.destroy(dracoGeometry);
  decoderModule.destroy(decoder);
  decoderModule.destroy(buffer);


  },
  	// onProgress callback
	function ( xhr ) {
		console.log( (xhr.loaded / xhr.total * 100) + '% loaded' );
	},

	// onError callback
	function ( err ) {
		console.error( 'An error happened' );
	}
  );
}