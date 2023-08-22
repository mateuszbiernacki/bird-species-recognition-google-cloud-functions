//const ENDPOINT = "https://europe-central2-birdspec.cloudfunctions.net/python-fitting-model"
const ENDPOINT = "http://localhost:8080/"

var results = [];
let mediaRecorder;
const buttonLabel = document.getElementById("buttonLabel");
const button = document.getElementById("recordButton")

const recordAudio = () =>
  new Promise(async resolve => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mediaRecorder = new MediaRecorder(stream);
    const audioChunks = [];

    mediaRecorder.addEventListener("dataavailable", event => {
      audioChunks.push(event.data);
    });

    const start = () => mediaRecorder.start();

    const stop = () =>
      new Promise(resolve => {
        mediaRecorder.addEventListener("stop", () => {
          const chunks = audioChunks;
          const audioBlob = new Blob(audioChunks);
          const audioUrl = URL.createObjectURL(audioBlob);
          const audio = new Audio(audioUrl);
          const play = () => audio.play();
          stream.getTracks().forEach((track) => track.stop());
          resolve({chunks, audioBlob, audioUrl, play });
        });

        mediaRecorder.stop();
      });

    resolve({ start, stop });
  });

const sleep = time => new Promise(resolve => setTimeout(resolve, time));


// Funcje


function startClicked(){
    buttonLabel.innerText = "Recording";
    button.disabled = true;
    (async () => {
        const recorder = await recordAudio();
        recorder.start();
        await sleep(10000);
        const audio = await recorder.stop();
        sendDataToFit(audio);
        buttonLabel.innerText = "Start";
        button.disabled = false;
        audio.play();
        })();
        

}



function sendDataToFit(audioToSend) {
    console.log(audioToSend.chunks[0]);
    fetch(ENDPOINT, {
      method: "POST",
      body: audioToSend.audioBlob
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



function fetchDataFromEndpoint() {

}

function errorMessage(message){
    console.log(message)
}