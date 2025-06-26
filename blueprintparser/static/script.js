import * as pdfjsLib from "../static/pdfjs-5.3.31-dist/build/pdf.mjs"

pdfjsLib.GlobalWorkerOptions.workerSrc = "../static/pdfjs-5.3.31-dist/build/pdf.worker.mjs";

let pageNumber = 1;
let scale = 1;

function renderPage(pageNumber) {
    var loadingTask = pdfjsLib.getDocument('static/uploads/blueprint.pdf');
    // pageNumber = parseInt(e.target.value);
    loadingTask.promise.then(function(pdf) {
        pdf.getPage(pageNumber).then(function(page) {
            var viewer = document.getElementById("viewer");
            var pdfCanvas = document.getElementById("pdf-viewer");
            var boundingBoxCanvas = document.getElementById("bounding-box");

            var viewport = page.getViewport({scale: 1});
            scale = Math.min(viewer.clientWidth/viewport.width, viewer.clientHeight/viewport.height);
            viewport = page.getViewport({scale: scale});

                        
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
}

document.getElementById('page-up').addEventListener('click', e => {
    pageNumber++;
    document.getElementById('page-number-input').value = pageNumber;
    renderPage(pageNumber);
});

document.getElementById('page-down').addEventListener('click', e => {
    pageNumber--;
    document.getElementById('page-number-input').value = pageNumber;
    renderPage(pageNumber);
});

document.getElementById('page-number-input').addEventListener('input', e => {
    pageNumber = parseInt(e.target.value);
    renderPage(pageNumber);
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
            endY: endY,
            scale: scale
        })
    })
    .then(response => response.json())
    .then(data => {
        if(!data.success) {
            console.log(data.error);
        }
    })
});
