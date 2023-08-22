
// const ENDPOINT = "https://europe-central2-birdspec.cloudfunctions.net/python-fitting-model"
const ENDPOINT = "http://localhost:8080/"
var results = [];
URL = window.URL || window.webkitURL;

var gunStream;

var rec;

var input;

var AudioContext = window.AudioContext || window.webkitAudioContext;
var audioContext //audio context to help us record

var recordButton = document.getElementById("recordButton");
var recordButtonLabel = document.getElementById("buttonLabel");

recordButton.addEventListener("click", startRecording);


function startRecording(){
  console.log("start recording button clicked");
  var cons = {
    audio: true,
    video: false
  }
  recordButton.disabled = true;
  buttonLabel.innerText = "Recording";

  navigator.mediaDevices.getUserMedia(cons).then(function(stream) {
    audioContext = new AudioContext();
    gunStream = stream;
    input = audioContext.createMediaStreamSource(stream);

    rec = new Recorder(input, {
      numChannels: 1
    });

    rec.record();
    console.log("Recording started")
    setTimeout(stopRecording, 10000);
    console.log('test')
  });

}

function stopRecording(){
  recordButton.disabled = false;
  buttonLabel.innerText = "Start";

  rec.stop()
  gunStream.getAudioTracks()[0].stop();

  rec.exportWAV(giveBlob);
}

function giveBlob(blob){
  console.log(blob);

  fetch(ENDPOINT, {
    method: "POST",
    body: blob
  })
  .then(response => response.json())
  .then(data => {
    // Otrzymane dane z serwera
    hadleReturnedData(data);
  })
  .catch(error => {
    console.error("Error fetching data:", error);
    errorMessage("Error fetching data. Details in console.");
  });
}


function showResults(data) {
  console.log(data)
  const listToShow = Object.entries(data);
  listToShow.sort((a, b) => b[1] - a[1]);
  const listFromDocument = document.getElementById("results");
  listFromDocument.innerHTML = "";
  listToShow.forEach(entry => {
      const spec_name = entry[0];
      const propability = entry[1]
      const listItem = document.createElement("li");
      listItem.textContent = "" + spec_name + "\t-\t" + (propability*100).toFixed(2) + "%";
      listFromDocument.appendChild(listItem);
  })
}

function hadleReturnedData(data) {
  if (results.push(data) === 10) {
      results.shift();
  }
  results_to_print = {}
  results.forEach((result) => {
      for (k in result){
          if (!(k in results_to_print)){
              results_to_print[k] = [];
          }
          results_to_print[k].push(result[k]);
      }
          
  });
  results_to_print_ave = {};
  for (k in results_to_print){
      results_to_print_ave[k] = results_to_print[k].reduce((a, b) => a + b, 0) / results_to_print[k].length;
  }
  showResults(results_to_print_ave);
}