  
function shareButtonClicked(){
  var copyText = document.getElementById("myInput");
  copyText.select();
  document.execCommand("copy");
}

  document.getElementById("copyButton").addEventListener(onclick,shareButtonClicked())