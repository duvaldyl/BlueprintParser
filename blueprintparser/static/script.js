import * as pdfjsLib from "../static/pdfjs-5.3.31-dist/build/pdf.mjs"

pdfjsLib.GlobalWorkerOptions.workerSrc = "../static/pdfjs-5.3.31-dist/build/pdf.worker.mjs";

let pageNumber = 1;
let scale = 1;
let displayScale = 1; // Scale factor used for display
let pdfViewport = null; // Store the viewport for coordinate calculations

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

        // Get the natural viewport at scale 1
        const naturalViewport = page.getViewport({scale: 1});
        
        // Calculate display scale to fit container
        displayScale = Math.min(viewer.clientWidth/naturalViewport.width, viewer.clientHeight/naturalViewport.height);
        
        // Use higher resolution for better quality (2x device pixel ratio or minimum 2x)
        const devicePixelRatio = window.devicePixelRatio || 1;
        const renderScale = Math.max(displayScale * devicePixelRatio, displayScale * 2);
        
        // Create viewport for rendering at higher resolution
        const renderViewport = page.getViewport({scale: renderScale});
        
        // Store the display viewport for coordinate calculations
        pdfViewport = page.getViewport({scale: displayScale});
        scale = displayScale; // Keep this for backwards compatibility
        
        // Set canvas size for high resolution
        pdfCanvas.width = renderViewport.width;
        pdfCanvas.height = renderViewport.height;
        
        // Set display size to fit container
        pdfCanvas.style.width = pdfViewport.width + 'px';
        pdfCanvas.style.height = pdfViewport.height + 'px';

        // Set bounding box canvas to match display size
        boundingBoxCanvas.width = pdfViewport.width;
        boundingBoxCanvas.height = pdfViewport.height;
        boundingBoxCanvas.style.width = pdfViewport.width + 'px';
        boundingBoxCanvas.style.height = pdfViewport.height + 'px';
        
        // Center both canvases in the container
        const containerRect = viewer.getBoundingClientRect();
        const canvasLeft = (containerRect.width - pdfViewport.width) / 2;
        const canvasTop = (containerRect.height - pdfViewport.height) / 2;
        
        pdfCanvas.style.left = canvasLeft + 'px';
        pdfCanvas.style.top = canvasTop + 'px';
        boundingBoxCanvas.style.left = canvasLeft + 'px';
        boundingBoxCanvas.style.top = canvasTop + 'px';

        const context = pdfCanvas.getContext('2d');
        
        // Scale context for high resolution rendering
        const scaleRatio = renderScale / displayScale;
        context.scale(scaleRatio, scaleRatio);
        
        const renderContext = {
            canvasContext: context,
            viewport: page.getViewport({scale: displayScale})
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

// Helper function to get mouse coordinates relative to the bounding box canvas
function getMouseCoordinates(e, canvas) {
    const rect = canvas.getBoundingClientRect();
    return {
        x: e.clientX - rect.left,
        y: e.clientY - rect.top
    };
}

canvas.addEventListener('mousedown', e => {
    isDrawing = true;
    const coords = getMouseCoordinates(e, canvas);
    startX = coords.x;
    startY = coords.y;
})

canvas.addEventListener('mousemove', e => {
    if (isDrawing) {
        const coords = getMouseCoordinates(e, canvas);
        endX = coords.x;
        endY = coords.y;
        
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.strokeStyle = 'red';
        ctx.lineWidth = 2;
        ctx.strokeRect(startX, startY, endX-startX, endY-startY);
    }
});

canvas.addEventListener('mouseup', e => {
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

// Initialize by rendering the first page
document.addEventListener('DOMContentLoaded', () => {
    renderPage(pageNumber);
});
