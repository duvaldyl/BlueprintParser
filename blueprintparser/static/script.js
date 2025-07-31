import * as pdfjsLib from "../static/pdfjs-5.3.31-dist/build/pdf.mjs"

pdfjsLib.GlobalWorkerOptions.workerSrc = "../static/pdfjs-5.3.31-dist/build/pdf.worker.mjs";

let pageNumber = 1;
let scale = 1;
let displayScale = 1; // Scale factor used for display
let userZoom = 1; // User-controlled zoom level
let pdfViewport = null; // Store the viewport for coordinate calculations
let baseFitScale = 1; // Base scale to fit PDF in container

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
        const canvasContainer = document.getElementById("canvas-container");
        const pdfCanvas = document.getElementById("pdf-viewer");
        const boundingBoxCanvas = document.getElementById("bounding-box");

        // Get the natural viewport at scale 1
        const naturalViewport = page.getViewport({scale: 1});
        
        // Calculate base scale to fit container (used as reference)
        baseFitScale = Math.min(viewer.clientWidth/naturalViewport.width, viewer.clientHeight/naturalViewport.height);
        
        // Apply user zoom to the base fit scale
        displayScale = baseFitScale * userZoom;
        
        // Use higher resolution for better quality
        const devicePixelRatio = window.devicePixelRatio || 1;
        const renderScale = Math.max(displayScale * devicePixelRatio, displayScale * 2);
        
        // Create viewport for rendering at higher resolution
        const renderViewport = page.getViewport({scale: renderScale});
        
        // Store the display viewport for coordinate calculations
        pdfViewport = page.getViewport({scale: displayScale});
        scale = displayScale; // Keep this for backwards compatibility with clip function
        
        // Calculate display dimensions
        const displayWidth = pdfViewport.width;
        const displayHeight = pdfViewport.height;
        
        // Container dimensions
        const containerWidth = viewer.clientWidth;
        const containerHeight = viewer.clientHeight;
        
        // Set canvas container size to match PDF display size
        canvasContainer.style.width = displayWidth + 'px';
        canvasContainer.style.height = displayHeight + 'px';
        
        // Center the container when PDF is smaller than viewer
        if (displayWidth < containerWidth) {
            canvasContainer.style.marginLeft = 'auto';
            canvasContainer.style.marginRight = 'auto';
        } else {
            canvasContainer.style.marginLeft = '0';
            canvasContainer.style.marginRight = '0';
        }
        
        if (displayHeight < containerHeight) {
            canvasContainer.style.marginTop = 'auto';
            canvasContainer.style.marginBottom = 'auto';
        } else {
            canvasContainer.style.marginTop = '0';
            canvasContainer.style.marginBottom = '0';
        }
        
        // Set canvas size for high resolution
        pdfCanvas.width = renderViewport.width;
        pdfCanvas.height = renderViewport.height;
        
        // Set display size to actual PDF size
        pdfCanvas.style.width = displayWidth + 'px';
        pdfCanvas.style.height = displayHeight + 'px';

        // Set bounding box canvas to match PDF display size
        boundingBoxCanvas.width = displayWidth;
        boundingBoxCanvas.height = displayHeight;
        boundingBoxCanvas.style.width = displayWidth + 'px';
        boundingBoxCanvas.style.height = displayHeight + 'px';

        const context = pdfCanvas.getContext('2d');
        
        // Clear canvas
        context.clearRect(0, 0, pdfCanvas.width, pdfCanvas.height);
        
        // Scale context for high resolution rendering
        const scaleRatio = renderScale / displayScale;
        context.setTransform(scaleRatio, 0, 0, scaleRatio, 0, 0);
        
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

// Zoom functionality
document.getElementById('zoom-in').addEventListener('click', async () => {
    if (!isRendering) {
        userZoom = Math.min(userZoom * 1.2, 5); // Max 5x zoom
        await renderPage(pageNumber);
    }
});

document.getElementById('zoom-out').addEventListener('click', async () => {
    if (!isRendering) {
        userZoom = Math.max(userZoom / 1.2, 0.1); // Min 0.1x zoom
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
    // Transform canvas coordinates back to original PDF coordinates (scale 1)
    // Canvas coordinates are at displayScale, we need to get back to scale 1
    const originalPdfStartX = startX / displayScale;
    const originalPdfStartY = startY / displayScale;
    const originalPdfEndX = endX / displayScale;
    const originalPdfEndY = endY / displayScale;

    console.log('Canvas coordinates:', {startX, startY, endX, endY});
    console.log('Display scale:', displayScale);
    console.log('Original PDF coordinates:', {originalPdfStartX, originalPdfStartY, originalPdfEndX, originalPdfEndY});

    fetch('/clip', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            pageNumber: pageNumber,
            startX: originalPdfStartX,
            startY: originalPdfStartY,
            endX: originalPdfEndX,
            endY: originalPdfEndY,
            scale: 1  // Always send scale 1 since we're sending original PDF coordinates
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
            console.error(data.error);
        } else {
            // Only download after the server confirms the file was created successfully
            const link = document.createElement('a');
            link.href = "/save/final.pdf";
            link.download = "blueprint.pdf";

            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    })
    .catch(error => {
        console.error('Error saving clips:', error);
    });
});

// Initialize by rendering the first page
document.addEventListener('DOMContentLoaded', () => {
    renderPage(pageNumber);
});
