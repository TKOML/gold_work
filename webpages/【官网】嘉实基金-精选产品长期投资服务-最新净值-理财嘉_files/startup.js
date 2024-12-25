function loadJS(id, fileUrl,loadCallBack){
    var scriptTag = document.getElementById(id),
    	oHead = document.getElementsByTagName('head').item(0),
    	oScript = document.createElement("script");
    if (scriptTag) {
    	oHead.removeChild(scriptTag); 
    }
    oScript.id = id; 
    oScript.type = "text/javascript"; 
    oScript.src = fileUrl;
    oHead.appendChild(oScript); 
	oScript.onload = oScript.onreadystatechange = function( _, isAbort ) {
		if (isAbort || !oScript.readyState || /loaded|complete/.test(oScript.readyState)){
			oScript.onload = oScript.onreadystatechange = null;
			if(loadCallBack){
				loadCallBack();
			}
		}
	};
}
loadJS("version","/ws/scripts/version.js?v="+Math.random(),function(){
	loadJS("thinkiveJS","/ws/scripts/thinkiveJs.min.js?v="+window._sysVersion);
});