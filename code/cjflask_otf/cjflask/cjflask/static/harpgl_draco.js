function loadDracoHarp(edit, query, bbox, buffer){

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

      for(var i = 0; i < geometry['attributes']['position']['array'].length; i++){
        
        c = geometry['attributes']['position']['array'][i];
        if(i % 3 == 0){
          geometry['attributes']['position']['array'][i] = (c * scale[0] + translate[0]) - bbox[0] - helftx;
        }
        else if(i % 3 == 1){
          geometry['attributes']['position']['array'][i] = (c * scale[1] + translate[1]) - bbox[1] - helfty;
        }
        else {
          geometry['attributes']['position']['array'][i] = (c * scale[2] + translate[2]);
        }
      } 
    
      var material = new THREE.MeshLambertMaterial();

      var mesh = new THREE.Mesh( geometry, material );
      mesh.geoPosition = new harp.GeoCoordinates(mid_wgs[1], mid_wgs[0]);
      mesh.castShadow = true;
      mesh.receiveShadow = true;
      map.mapAnchors.add(mesh);
      map.update();

    // send time message to Flask app through SocketIO
    if (task == "visualise"){
      var d = new Date();
      socket.emit('message', ["visualise", d.getTime(), "end"]);
      alert(task)
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