const MODEL_PATH = 'https://tfhub.dev/google/tfjs-model/movenet/singlepose/lightning/4';
const preprocessImage = document.getElementById('preprocessImage');

// const video = document.getElementById('images');
const staticView = document.getElementById('view');
const demosSection = document.getElementById('demos');
const startPreprocessingButton = document.getElementById('startButton');

console.log(link_data.length + '개')

// Check if webcam access is supported.
function getUserMediaSupported() {
    return !!(navigator.mediaDevices &&
        navigator.mediaDevices.getUserMedia);
}


// If webcam supported, add event listener to button for when user
// wants to activate it to call enableCam function which we will 
// define in the next step.
if (getUserMediaSupported()) {
    // startPreprocessingButton.addEventListener('click', enableCam)
    startPreprocessingButton.addEventListener('click', loadAndRunModel)
} else {
    console.warn('getUserMedia() is not supported by your browser');
}

// setInterval(function(){
let imagePath;
// preprocessImage.src = imagePath;
// },1000)

// variable for looping through image links
let n = 0;

let posture;

async function loadAndRunModel(event) {
    // posture = document.getElementById('posture');
    let movenet = await tf.loadGraphModel(MODEL_PATH, {
        fromTFHub: true
    });
    let exampleInputTensor = tf.zeros([1, 192, 192, 3], 'int32');

    event.target.classList.add('removed');
    demosSection.classList.remove('invisible');

    let intervalId = setInterval(async function() {
        n++;

        var imagePath = link_data[n][1];
        posture = link_data[n][2];
        console.log(link_data.length + '개 중 ' + n + '개')
        // var imagePath = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSntGBtyPrAp9ZjJoprI9W2g8w-kiKO1f2uMA&usqp=CAU";//"https://storage.googleapis.com/jmstore/TensorFlowJS/EdX/standing.jpg";//"https://t1.daumcdn.net/cfile/tistory/9927E4455A6E154C17";
        // if (n%2 == 0) {imagePath = "/static/do.png"}
        // if (n%2 == 1) {imagePath = "https://storage.googleapis.com/jmstore/TensorFlowJS/EdX/standing.jpg"}
        // var imagePath = links[n];
        preprocessImage.src = imagePath;

        preprocessImage.onload = async function() {
            tf.engine().startScope();

            let predictionsArray = await predictImage();

            let predictions;

            for (let i = 0; i < predictionsArray.length; i++) {
                if (predictionsArray[i]['class'] == 'person') {
                    predictions = predictionsArray[i];
                    break;
                }
            }
            if (predictions == undefined) {
                return;
            }

            let imageTensor = tf.browser.fromPixels(preprocessImage);
            const [wHeight, wWidth] = imageTensor.shape;

            let bLeft = parseInt(predictions.bbox[0]);
            let bTop = parseInt(predictions.bbox[1]);
            let bWidth = parseInt(predictions.bbox[2]);
            let bHeight = parseInt(predictions.bbox[3]);
            if (bWidth > wWidth - bLeft) {
                bWidth = wWidth - bLeft;
            } // right of the image
            if (bHeight > wHeight - bTop) {
                bHeight = wHeight - bTop;
            } // bottom of the image
            if (bLeft < 0) {
                bLeft = 0;
            } // left of the image
            if (bTop < 0) {
                bTop = 0;
            } // top
            if (bHeight > bWidth) {
                bHeight = bWidth;
            } // if height > width, cut the height from bottom
            let cropStartPoint = [bTop, bLeft, 0]; // red
            let cropSize = [bHeight, bWidth, 3]; // all RGB

            let padAmount;
            let padDirection;

            if (bWidth > bHeight) {
                padAmount = bWidth - bHeight; // most likely not needed
                padDirection = 'y';
            } else if (bWidth < bHeight) {
                padAmount = bHeight - bWidth;
                padDirection = 'x';
            }

            let croppedTensor = tf.slice(imageTensor, cropStartPoint, cropSize);

            let paddedTensor;
            let resizedTensor;

            if (padDirection == 'x') {
                paddedTensor = croppedTensor.pad([
                    [0, padAmount],
                    [0, 0],
                    [0, 0]
                ]);
            } else if (padDirection == 'y') {
                paddedTensor = croppedTensor.pad([
                    [0, 0],
                    [0, padAmount],
                    [0, 0]
                ]);
            } else {
                paddedTensor = croppedTensor;
            }

            resizedTensor = tf.image.resizeBilinear(paddedTensor, [192, 192], true).toInt();

            let tensorOutput = movenet.predict(tf.expandDims(resizedTensor));
            let arrayOutput = await tensorOutput.array();
            const singlePoint = arrayOutput[0][0]; // 17, 3

            const yPoint = singlePoint.map(row => row[0]);
            const xPoint = singlePoint.map(row => row[1]);

            // const flatten = [...yPoint, ...xPoint];

            const flatten = [];
            for (let i = 0; i < yPoint.length; i++) {
                flatten.push(yPoint[i], xPoint[i]);
            }
            sendPostRequest(flatten, imagePath);

            // tf.dispose(imageTensor);
            // tf.dispose(croppedTensor);
            // tf.dispose(resizedTensor);
            // tf.dispose(tensorOutput);
            // tf.dispose(arrayOutput);
            tf.engine().endScope();
        }
        if (n == link_data.length) {
            clearInterval(intervalId);
        }

    }, 5000);

};


// Enable the live webcam view and start classification.
// async function enableCam(event) {
//   // Only continue if the COCO-SSD has finished loading.
//   // if (!model) {
//   //   return;
//   // }

//   // Hide the button once clicked.
//   event.target.classList.add('removed');  

//   // getUsermedia parameters to force video but not audio.
//   const constraints = {
//     video: true
//   };
//   let display = await navigator.mediaDevices
//     .getUserMedia(constraints);

//   // Returns a sequence of MediaStreamTrack objects 
//   // representing the video tracks in the stream

//   let settings = display.getVideoTracks()[0]
//       .getSettings();

//   let width = settings.width;
//   let height = settings.height;

//   console.log('Actual width of the camera video: '
//       + width + 'px');
//   console.log('Actual height of the camera video:'
//       + height + 'px');
//   const p = document.createElement('p');
//   p.innerText = width + 'X' + height;
//   var d = document.getElementsByTagName('div');
//   d[0].append(p);

//   // Activate the webcam stream.
//   navigator.mediaDevices.getUserMedia(constraints).then(function(stream) {
//     video.srcObject = stream;
//     video.addEventListener('loadeddata', predictWebcam);
//   });
// }

var model = undefined;

// Before we can use COCO-SSD class we must wait for it to finish
// loading. Machine Learning models can be large and take a moment 
// to get everything needed to run.
// Note: cocoSsd is an external object loaded from our index.html
// script tag import so ignore any warning in Glitch.
cocoSsd.load().then(function(loadedModel) {
    model = loadedModel;
    // Show demo section now model is ready to use.
    demosSection.classList.remove('invisible');
});

var children = [];



// display
function predictImage() {
    return new Promise((resolve) => {
        // Now let's start classifying a frame in the stream.
        model.detect(preprocessImage).then(function(predictions) {
            // Remove any highlighting we did previous frame.
            for (let i = 0; i < children.length; i++) {
                staticView.removeChild(children[i]);
            }
            children.splice(0);

            // Now lets loop through predictions and draw them to the live view if
            // they have a high confidence score.
            for (let n = 0; n < predictions.length; n++) {
                // if (predictions[n].class == "person") {

                // If we are over 66% sure we are sure we classified it right, draw it!
                if (predictions[n].score > 0.66) {
                    const p = document.createElement('p');
                    p.innerText = predictions[n].class + ' - with ' +
                        Math.round(parseFloat(predictions[n].score) * 100) +
                        '% confidence.';
                    p.style = 'margin-left: ' + predictions[n].bbox[0] + 'px; margin-top: ' +
                        (predictions[n].bbox[1] - 10) + 'px; width: ' +
                        (predictions[n].bbox[2] - 10) + 'px; top: 0; left: 0;';

                    const highlighter = document.createElement('div');
                    highlighter.setAttribute('class', 'highlighter');
                    highlighter.style = 'left: ' + predictions[n].bbox[0] + 'px; top: ' +
                        predictions[n].bbox[1] + 'px; width: ' +
                        predictions[n].bbox[2] + 'px; height: ' +
                        predictions[n].bbox[3] + 'px;';

                    staticView.appendChild(highlighter);
                    staticView.appendChild(p);
                    children.push(highlighter);
                    children.push(p);

                    // Resolve the promise with the current prediction
                    resolve(predictions);
                }
            }
        });
    });
}


// 주기적으로 POST 요청을 보내는 함수
async function sendPostRequest(output, receivedImagePath) {
    // POST 요청을 보낼 데이터를 준비합니다.
    var data = {
        "movenet_output": output,
        "posture": posture,
        "location": receivedImagePath
    };
    // POST 요청을 보냅니다.
    fetch('/record-post-endpoint', {
            method: 'POST',
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