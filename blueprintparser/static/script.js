import * as pdfjsLib from "../static/pdfjs-5.3.31-dist/build/pdf.mjs"

pdfjsLib.GlobalWorkerOptions.workerSrc = "../static/pdfjs-5.3.31-dist/build/pdf.worker.mjs";

let pageNumber = 35;

var loadingTask = pdfjsLib.getDocument("/static/Blueprint.pdf");
loadingTask.promise.then(function(pdf) {
    pdf.getPage(pageNumber).then(function(page) {
        console.log('made it in');
        var scale = 1; //TODO
        var viewport = page.getViewport({scale: scale});

        var pdfCanvas = document.getElementById("pdf-viewer");
        var boundingBoxCanvas = document.getElementById("bounding-box");

        pdfCanvas.height = viewport.height;
        pdfCanvas.width = viewport.width; 
        boundingBoxCanvas.height = pdfCanvas.height;
        boundingBoxCanvas.width = pdfCanvas.width;


        var context = pdfCanvas.getContext('2d');

        var renderContext = {
            canvasContext: context,
            viewport: viewport
        }

        page.render(renderContext);
    });
});

const canvas = document.getElementById('bounding-box');
const ctx = canvas.getContext('2d');

let startX, startY, endX, endY;
let isDrawing = false;

canvas.addEventListener('mousedown', e => {
    isDrawing = true;
    startX = e.offsetX;
    startY = e.offsetY;
})

document.addEventListener('mousemove', e => {
    if (isDrawing) {
        endX = e.offsetX;
        endY = e.offsetY;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.strokeRect(startX, startY, endX-startX, endY-startY);
        ctx.strokeStyle = 'red';
        document.getElementById('x-start').textContent = startX;
        document.getElementById('y-start').textContent = startY;
        document.getElementById('x').textContent = endX;
        document.getElementById('y').textContent = endY;
    }
});

document.addEventListener('mouseup', e => {
    isDrawing = false;
})

document.getElementById('clip').addEventListener('click', e => {
    console.log("made it in");
    fetch('/clip', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            pageNumber: pageNumber,
            startX: startX,
            startY: startY,
            endX: endX,
            endY: endY
        })
    });
})
