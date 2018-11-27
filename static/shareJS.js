  
function shareButtonClicked(){
  var copyText = document.getElementById("linkInput");
  copyText.select();
  document.execCommand("copy");
  console.log("2")
}

document.addEventListener('DOMContentLoaded', function() {
  document.getElementById("copyButton").addEventListener("click",shareButtonClicked);
  console.log("1");
}, false);
