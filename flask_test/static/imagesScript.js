const MODEL_PATH = 'https://tfhub.dev/google/tfjs-model/movenet/singlepose/lightning/4';
const preprocessImage = document.getElementById('preprocessImage');

const video = document.getElementById('webcam');
const liveView = document.getElementById('liveView');
const demosSection = document.getElementById('demos');
const enableWebcamButton = document.getElementById('webcamButton');

// Check if webcam access is supported.
function getUserMediaSupported() {
  return !!(navigator.mediaDevices &&
    navigator.mediaDevices.getUserMedia);
}


// If webcam supported, add event listener to button for when user
// wants to activate it to call enableCam function which we will 
// define in the next step.
if (getUserMediaSupported()) {
  enableWebcamButton.addEventListener('click', enableCam)
  enableWebcamButton.addEventListener('click', loadAndRunModel)
}
else {
  console.warn('getUserMedia() is not supported by your browser');
}

setInterval(function(){
var imagePath = "https://storage.googleapis.com/jmstore/TensorFlowJS/EdX/standing.jpg";
preprocessImage.src = imagePath;
},1000)

async function loadAndRunModel() {
  let  movenet = await tf.loadGraphModel(MODEL_PATH, {fromTFHub: true});
  let exampleInputTensor = tf.zeros([1, 192, 192, 3], 'int32');
  
  let cropStartPoint = [15, 170, 0];
  let cropSize = [345, 345, 3];

  setInterval (async function(){
    
    var imagePath = "https://t1.daumcdn.net/cfile/tistory/9927E4455A6E154C17";
    preprocessImage.src = imagePath;
    
    tf.engine().startScope();
    let imageTensor = tf.browser.fromPixels(preprocessImage);
    // let croppedTensor = tf.slice(imageTensor, cropStartPoint, cropSize);

    // let resizedTensor = tf.image.resizeBilinear(croppedTensor, [192, 192], true).toInt();
    let resizedTensor = tf.image.resizeBilinear(imageTensor, [192, 192], true).toInt();
    // console.log(resizedTensor.shape);

    let tensorOutput = movenet.predict(tf.expandDims(resizedTensor));
    let arrayOutput = await tensorOutput.array();
    console.log(arrayOutput);
    sendPostRequest(arrayOutput);
    // tf.dispose(imageTensor);
    // tf.dispose(croppedTensor);
    // tf.dispose(resizedTensor);
    // tf.dispose(tensorOutput);
    // tf.dispose(arrayOutput);
    tf.engine().endScope();

  }, 1000);


};


// Enable the live webcam view and start classification.
async function enableCam(event) {
  // Only continue if the COCO-SSD has finished loading.
  // if (!model) {
  //   return;
  // }
  
  // Hide the button once clicked.
  event.target.classList.add('removed');  
  
  // getUsermedia parameters to force video but not audio.
  const constraints = {
    video: true
  };
  let display = await navigator.mediaDevices
    .getUserMedia(constraints);

  // Returns a sequence of MediaStreamTrack objects 
  // representing the video tracks in the stream

  let settings = display.getVideoTracks()[0]
      .getSettings();

  let width = settings.width;
  let height = settings.height;

  console.log('Actual width of the camera video: '
      + width + 'px');
  console.log('Actual height of the camera video:'
      + height + 'px');
  const p = document.createElement('p');
  p.innerText = width + 'X' + height;
  var d = document.getElementsByTagName('div');
  d[0].append(p);

  // Activate the webcam stream.
  navigator.mediaDevices.getUserMedia(constraints).then(function(stream) {
    video.srcObject = stream;
    video.addEventListener('loadeddata', predictWebcam);
  });
}

// Store the resulting model in the global scope of our app.
// var model = undefined;

// Before we can use COCO-SSD class we must wait for it to finish
// loading. Machine Learning models can be large and take a moment 
// to get everything needed to run.
// Note: cocoSsd is an external object loaded from our index.html
// script tag import so ignore any warning in Glitch.
// cocoSsd.load().then(function (loadedModel) {
//   model = loadedModel;
//   // Show demo section now model is ready to use.
//   demosSection.classList.remove('invisible');
// });


// 주기적으로 POST 요청을 보내는 함수
async function sendPostRequest(output) {
  // POST 요청을 보낼 데이터를 준비합니다.
  var data = {
      movenet_output: output
  };
  // POST 요청을 보냅니다.
  fetch('/record-images', {
      method: 'GET',
      headers: {
          'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
  })
  .then(response => response.text())
  .then(result => console.log(result))
  .catch(error => console.error(error));
}

// 특정 간격(밀리초)마다 POST 요청을 보내도록 설정합니다.
// setInterval(sendPostRequest, 5000); // 5초마다 POST 요청을 보냅니다.

// 이미지 링크를 가져오는 함수

const API_KEY = 'replace';
const SEARCH_ENGINE_ID = 'replace';


function fetchImageLinks() {
  // Google Custom Search API를 통해 이미지 링크를 가져오는 AJAX 요청 등을 수행합니다.
  // 이 예시에서는 fetch() 함수를 사용하도록 가정합니다.
  var url = `https://www.googleapis.com/customsearch/v1?cx=${SEARCH_ENGINE_ID}&key=${API_KEY}&q=correct%20sitting%20posture&searchType=image`
  fetch(url)
    .then(response => response.json())
    .then(data => {
      // 이미지 링크가 포함된 결과 데이터를 받아옵니다.
      const imageLinks = data.items.map(item => item.link);
      
      // 이미지 링크를 웹 페이지에 표시합니다.
      displayImages(imageLinks);
    })
    .catch(error => {
      console.error('Error fetching image links:', error);
    });
}

// 이미지를 표시하는 함수
function displayImages(imageLinks) {
  const imageContainer = document.getElementById('imageContainer');
  
  // 기존에 표시된 이미지를 제거합니다.
  imageContainer.innerHTML = '';
  
  // 이미지를 생성하고 컨테이너에 추가합니다.
  imageLinks.forEach(link => {
    const image = document.createElement('img');
    image.src = link;
    imageContainer.appendChild(image);
  });
}

// 페이지 로드 후 5초마다 이미지 링크를 가져오기 위해 setInterval() 함수를 사용합니다.
window.addEventListener('load', () => {
  fetchImageLinks(); // 페이지 로드 후 첫 번째 이미지 링크를 가져옵니다.
  setInterval(fetchImageLinks, 5000); // 5초마다 이미지 링크를 업데이트합니다.
});