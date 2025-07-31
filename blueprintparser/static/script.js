import * as pdfjsLib from "../static/pdfjs-5.3.31-dist/build/pdf.mjs"

pdfjsLib.GlobalWorkerOptions.workerSrc = "../static/pdfjs-5.3.31-dist/build/pdf.worker.mjs";

let pageNumber = 1;
let scale = 1;

var isRendering = null;

async function renderPage(pageNumber) {
    if (isRendering) {
        return;
    }

    isRendering = true;
    
    try {
        const loadingTask = pdfjsLib.getDocument('/upload/blueprint.pdf');
        const pdf = await loadingTask.promise;
        const page = await pdf.getPage(pageNumber);
        
        const viewer = document.getElementById("blueprint-viewer");
        const pdfCanvas = document.getElementById("pdf-viewer");
        const boundingBoxCanvas = document.getElementById("bounding-box");

        let viewport = page.getViewport({scale: 1});
        scale = Math.min(viewer.clientWidth/viewport.width, viewer.clientHeight/viewport.height);
        
        viewport = page.getViewport({scale: scale});
        
        pdfCanvas.height = viewport.height;
        pdfCanvas.width = viewport.width; 

        boundingBoxCanvas.height = pdfCanvas.clientHeight;
        boundingBoxCanvas.width = pdfCanvas.clientWidth;

        const context = pdfCanvas.getContext('2d');
        const renderContext = {
            canvasContext: context,
            viewport: viewport
        };

        await page.render(renderContext).promise;
        
    } catch (error) {
        console.error('Error rendering page:', error);
    } finally {
        isRendering = false;
    }
}

document.getElementById('page-up').addEventListener('click', async () => {
    if(!isRendering) {
        pageNumber++;
        document.getElementById('page-number-input').value = pageNumber;
        await renderPage(pageNumber);
    }
});

document.getElementById('page-down').addEventListener('click', async (e) => {
    if(!isRendering) {
        pageNumber--;
        document.getElementById('page-number-input').value = pageNumber;
        await renderPage(pageNumber);
    }
});

let inputTimeout;
document.getElementById('page-number-input').addEventListener('input', e => {
    const newPageNumber = parseInt(e.target.value);

    clearTimeout(inputTimeout);
    
    inputTimeout = setTimeout(() => {
        if (!isRendering && newPageNumber !== pageNumber) {
            pageNumber = newPageNumber;
            renderPage(pageNumber);
        }
    }, 300);
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
            console.error(data.error);
        } else {
            let uuid = data.uuid;
            let clippedImagesContainer = document.getElementById("clipped-images");
            let iframe = document.createElement('iframe');
            iframe.src = "/clips/" + parseInt(pageNumber) + "_" + uuid + "_clip.pdf";
            clippedImagesContainer.appendChild(iframe);
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        }
    });
});

document.getElementById('save').addEventListener('click', e => {
    fetch('/save', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            good: true,
        })
    })
    .then(response => response.json())
    .then(data => {
        if(!data.success) {
            console.error(data.error)
        }
    });
    const link = document.createElement('a');
    link.href = "/save/final.pdf";
    link.download = "blueprint.pdf";

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
});
