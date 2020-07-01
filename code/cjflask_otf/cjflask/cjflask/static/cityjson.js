function get_bbox(json) {
    if(!"metadata" in json){
      return calculate_bbox(json);
    }
    if(!"geographicalExtent" in json["metadata"]){
      return calculate_bbox(json);
    }
  return json["metadata"]["geographicalExtent"];
  
}

function bbox_mid(bbox){
  var midx = bbox[0] + ((bbox[3] - bbox[0]) / 2);
  var midy = bbox[1] + ((bbox[4] - bbox[1]) / 2);
  return([midx, midy]);
}

function rdnew_to_wgs(v){
  v_wgs = proj4("+proj=sterea +lat_0=52.15616055555555 +lon_0=5.38763888888889 +k=0.9999079 +x_0=155000 +y_0=463000 +ellps=bessel +towgs84=565.417,50.3319,465.552,-0.398957,0.343988,-1.8774,4.0725 +units=m +no_defs",
  proj4('EPSG:4326'),
  v);
  return(v_wgs);
}

function singapore_to_wgs(v){
  v_wgs = proj4("+proj=tmerc +lat_0=1.366666666666667 +lon_0=103.8333333333333 +k=1 +x_0=28001.642 +y_0=38744.572 +ellps=WGS84 +units=m +no_defs",
  proj4('EPSG:4326'),
  v);
  return(v_wgs);
}

function canada_to_wgs(v){
  v_wgs = proj4("+proj=lcc +lat_1=49 +lat_2=77 +lat_0=49 +lon_0=-95 +x_0=0 +y_0=0 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs",
  proj4('EPSG:4326'),
  v);
  return(v_wgs);
}

function newyork_to_wgs(v){
  v_wgs = proj4("+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs",
  proj4('EPSG:4326'),
  v);
  return(v_wgs);
}

function switzerland_to_wgs(v){
  v_wgs = proj4("+proj=somerc +lat_0=46.95240555555556 +lon_0=7.439583333333333 +k_0=1 +x_0=2600000 +y_0=1200000 +ellps=bessel +towgs84=674.374,15.056,405.346,0,0,0,0 +units=m +no_defs",
  proj4('EPSG:4326'),
  v);
  return(v_wgs);
}