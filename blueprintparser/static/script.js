import * as pdfjsLib from "../static/pdfjs-5.3.31-dist/build/pdf.mjs"

pdfjsLib.GlobalWorkerOptions.workerSrc = "../static/pdfjs-5.3.31-dist/build/pdf.worker.mjs";

let totalPages = null;

let pageNumber = 1;
let scale = 1;
let displayScale = 1; // Scale factor used for display
let userZoom = 1; // User-controlled zoom level
let pdfViewport = null; // Store the viewport for coordinate calculations
let baseFitScale = 1; // Base scale to fit PDF in container

let marginTop = 'auto';
let marginBottom = 'auto';
let marginLeft = 'auto';
let marginRight = 'auto';

let isRendering = null;

async function renderPageAux(pageNumber) {
    if(isRendering) {
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
        const canvasContainer = document.getElementById("canvas-container");
        const context = pdfCanvas.getContext('2d');

        var viewport = page.getViewport({scale: 2});

        baseFitScale = Math.min(viewer.clientHeight/viewport.height, viewer.clientWidth/viewport.width);

        pdfCanvas.width = viewport.width;
        pdfCanvas.height = viewport.height;
        
        pdfCanvas.style.width = viewport.width*baseFitScale*userZoom + "px";
        pdfCanvas.style.height = viewport.height*baseFitScale*userZoom + "px";

        boundingBoxCanvas.style.width = viewport.width*baseFitScale*userZoom + "px";
        boundingBoxCanvas.style.height = viewport.height*baseFitScale*userZoom + "px";

        canvasContainer.style.height = viewport.height*baseFitScale*userZoom + "px";
        canvasContainer.style.width = viewport.width*baseFitScale*userZoom + "px";

        boundingBoxCanvas.width = viewport.width*baseFitScale*userZoom;
        boundingBoxCanvas.height = viewport.height*baseFitScale*userZoom;


        const renderContext = {
            canvasContext: context,
            viewport: viewport 
        };

        canvasContainer.style.marginTop = marginTop;
        canvasContainer.style.marginBottom = marginBottom;
        canvasContainer.style.marginLeft = marginLeft;
        canvasContainer.style.marginRight = marginRight;


        await page.render(renderContext).promise;

    } catch (error) {
        console.error('Error rendering page:', error);
    } finally {
        isRendering = false;
    }
}

async function renderPage(pageNumber) {
    if (isRendering) {
        return;
    }

    isRendering = true;
    
    try {
        const loadingTask = pdfjsLib.getDocument('/upload/blueprint.pdf');
        const pdf = await loadingTask.promise;
        const page = await pdf.getPage(pageNumber);
        totalPages = pdf.numPages;
        
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
    if(!isRendering && pageNumber != totalPages) {
        pageNumber++;
        document.getElementById('page-number-input').value = pageNumber;
        userZoom = 1;
        await renderPageAux(pageNumber);
    }
});

document.getElementById('page-down').addEventListener('click', async (e) => {
    if(!isRendering && pageNumber != 1) {
        pageNumber--;
        document.getElementById('page-number-input').value = pageNumber;
        userZoom = 1;
        await renderPageAux(pageNumber);
    }
});

// Zoom functionality
document.getElementById('zoom-in').addEventListener('click', async () => {
    if (!isRendering) {
        userZoom = Math.min(userZoom * 1.5, 5); // Max 5x zoom
        let canvasContainer = document.getElementById('canvas-container');
        /*
        marginTop = canvasContainer.style.marginTop;
        marginBottom = canvasContainer.style.marginBottom;
        marginLeft = canvasContainer.style.marginLeft;
        marginRight = canvasContainer.style.marginRight;
        */
        await renderPageAux(pageNumber);
    }
});

document.getElementById('zoom-out').addEventListener('click', async () => {
    if (!isRendering) {
        userZoom = Math.max(userZoom / 1.5, 0.5); // Min 0.1x zoom
        await renderPageAux(pageNumber);
    }
});

let inputTimeout;
document.getElementById('page-number-input').addEventListener('input', e => {
    const newPageNumber = parseInt(e.target.value);

    clearTimeout(inputTimeout);

    console.log('inside');
    
    inputTimeout = setTimeout(() => {
        if (!isRendering && newPageNumber > totalPages) {
            pageNumber = totalPages;
            e.target.value = pageNumber;
            userZoom = 1;
            renderPageAux(pageNumber);
        } else if(!isRendering && newPageNumber <= 0 || !isRendering && isNaN(newPageNumber)) {
            pageNumber = 1;
            e.target.value = pageNumber;
            userZoom = 1;
            renderPageAux(pageNumber);
        } else if (!isRendering && newPageNumber !== pageNumber) {
            pageNumber = newPageNumber;
            userZoom = 1;
            renderPageAux(pageNumber);
        }
    }, 1000);
});

/*
document.getElementById('auto-clip-page').addEventListener('click', e => {
    fetch('/autoclip/page', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            pageNumber: pageNumber,
        })
    })
    .then(response => response.json())
    .then(data => {
        if(!data.success) {
            console.error(data.error);
        } else {
            const link = document.createElement('a');
            link.href = "/save/autoclip.pdf";
            link.download = "autoclip.pdf";

            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    });
});
*/

const canvas = document.getElementById('bounding-box');
const ctx = canvas.getContext('2d');

let startX, startY, endX, endY;
let isDrawing = false;

// Helper function to get mouse coordinates relative to the bounding box canvas
function getMouseCoordinates(e, canvas) {
    const rect = canvas.getBoundingClientRect();
    return {
        //x: e.clientX - rect.left,
        //y: e.clientY - rect.top
        x: e.clientX - rect.left + canvas.scrollLeft,
        y: e.clientY - rect.top + canvas.scrollTop
    };
}
canvas.addEventListener('mousedown', e => {
    isDrawing = true;
    const coords = getMouseCoordinates(e, canvas);
    startX = coords.x;
    startY = coords.y;
});

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
});

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

    // Get sizing options
    const sizingMode = document.querySelector('input[name="sizing-mode"]:checked').value;
    let fixedWidth = null;
    let fixedHeight = null;
    
    if (sizingMode === 'fixed-size') {
        fixedWidth = parseInt(document.getElementById('fixed-width').value) || 640;
        fixedHeight = parseInt(document.getElementById('fixed-height').value) || 640;
    }

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
            scale: userZoom,
            sizingMode: sizingMode,
            fixedWidth: fixedWidth,
            fixedHeight: fixedHeight
        })
    })
    .then(response => response.json())
    .then(data => {
        if(!data.success) {
            console.error(data.error);
        } else {
            let uuid = data.uuid;
            let filename = parseInt(pageNumber) + "_" + uuid + "_clip.pdf";
            let clippedImagesContainer = document.getElementById("clipped-images");
            
            // Create a container for the clip with delete button
            let clipContainer = document.createElement('div');
            clipContainer.className = 'clip-container';
            clipContainer.setAttribute('data-filename', filename);
            
            // Create a canvas for the PDF preview
            let canvas = document.createElement('canvas');
            canvas.className = 'clip-preview';
            canvas.width = 170; // Fixed width for consistent previews
            canvas.height = 120; // Fixed height
            
            // Render the PDF clip to the canvas
            renderClipPreview(canvas, "/clips/" + filename);
            
            // Create the delete button
            let deleteBtn = document.createElement('button');
            deleteBtn.className = 'delete-clip-btn';
            deleteBtn.innerHTML = '×';
            deleteBtn.title = 'Delete this clip';
            
            // Add click handler for delete button
            deleteBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                deleteClip(filename, clipContainer);
            });
            
            // Add elements to container
            clipContainer.appendChild(canvas);
            clipContainer.appendChild(deleteBtn);
            
            // Add container to the clips area
            clippedImagesContainer.appendChild(clipContainer);
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

// Function to delete a clip
function deleteClip(filename, clipContainer) {
    fetch(`/delete/${filename}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Remove the clip container from the DOM
            clipContainer.remove();
        } else {
            console.error('Error deleting clip:', data.error);
            alert('Failed to delete clip. Please try again.');
        }
    })
    .catch(error => {
        console.error('Error deleting clip:', error);
        alert('Failed to delete clip. Please try again.');
    });
}

// Function to render a PDF clip preview
function renderClipPreview(canvas, clipUrl) {
    pdfjsLib.getDocument(clipUrl).promise.then(pdf => {
        pdf.getPage(1).then(page => {
            // Use higher scale for better quality
            const scale = 0.8; // Increased from 0.2 to 0.8
            const viewport = page.getViewport({scale: scale});
            const context = canvas.getContext('2d');
            
            // Set canvas size to match the scaled viewport
            canvas.width = viewport.width;
            canvas.height = viewport.height;
            
            // Set display size to fit in the container (170x120)
            canvas.style.width = '170px';
            canvas.style.height = '120px';

            page.render({
                canvasContext: context,
                viewport: viewport,
            });
        });
    });
}

// Sizing options functionality
document.addEventListener('DOMContentLoaded', async () => {
    // Handle radio button changes for sizing options
    const sizingModeRadios = document.querySelectorAll('input[name="sizing-mode"]');
    const fixedSizeInputs = document.getElementById('fixed-size-inputs');
    
    sizingModeRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            if (e.target.value === 'fixed-size') {
                fixedSizeInputs.style.visibility = 'visible';
            } else {
                fixedSizeInputs.style.visibility = 'hidden';
            }
        });
    });
    
    // Initialize by rendering the first page
    await renderPage(pageNumber);
});
