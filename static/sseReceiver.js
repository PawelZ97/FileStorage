var source = new EventSource("http://pi.iem.pw.edu.pl:8321/zychp/webapp/event",{ withCredentials: true});
source.onmessage = function(event) {
    document.getElementsByClassName("mainClass").innerHTML += event.data + "<br>";
};

