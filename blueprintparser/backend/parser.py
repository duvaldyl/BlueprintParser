import uuid
import pymupdf
import numpy as np
from sklearn.cluster import DBSCAN
import os

def compute_bounding_box(pts):
    x0 = min(pts[:, 0])
    x1 = max(pts[:, 0])
    y0 = min(pts[:, 1])
    y1 = max(pts[:, 1])

    return (x0, y0, x1, y1)

def convert_xyxyn2bbox(xyxyn, width, height):
    x0 = xyxyn[0]
    x1 = xyxyn[2]
    y0 = xyxyn[1]
    y1 = xyxyn[3]

    return (x0*width, y0*height, x1*width, y1*height)

def draw_region(src, page, page_number, points, width, height, margin):
        bbox = compute_bounding_box(points)

        page.show_pdf_page(
            pymupdf.Rect(margin, margin, width - margin, height - margin),
            src,
            pno=page_number,
            clip=bbox,
        )

def draw_bbox(page, points):
    bbox = compute_bounding_box(points)

    page.draw_rect(bbox, color=(1, 0, 0), width=0.5)

class BlueprintParser:

    def __init__(self, path, page_size=(640, 640), margin=20, eps=75, min_samples=100):
        self.path = path
        self.doc = pymupdf.open(path)
        self.page_size = page_size
        self.margin = margin
        self.eps = eps
        self.min_samples = min_samples

    def clip_region(self, page_number, bbox, scale=1, sizing_mode='bounding-box', fixed_width=None, fixed_height=None, clips_dir=None):
        # Get the original page to understand its dimensions
        original_page = self.doc[page_number]
        page_rect = original_page.rect
        
        # Convert display coordinates to PDF coordinates
        # bbox comes in as (startX, startY, endX, endY) from the display
        x0, y0, x1, y1 = bbox
        
        # Ensure coordinates are in the correct order (min/max)
        min_x = min(x0, x1)
        max_x = max(x0, x1)
        min_y = min(y0, y1)
        max_y = max(y0, y1)
        
        # Convert from display scale to PDF coordinates
        # The scale factor represents how much the PDF was scaled down to fit the display
        pdf_x0 = min_x / scale
        pdf_y0 = min_y / scale
        pdf_x1 = max_x / scale
        pdf_y1 = max_y / scale
        
        # Create the clipping rectangle
        clip_rect = pymupdf.Rect(pdf_x0, pdf_y0, pdf_x1, pdf_y1)
        
        # Calculate dimensions for the output page based on sizing mode
        if sizing_mode == 'fixed-size' and fixed_width and fixed_height:
            # Use fixed dimensions
            output_width = fixed_width
            output_height = fixed_height
            
            # Calculate the original clipped content dimensions
            clip_width = pdf_x1 - pdf_x0
            clip_height = pdf_y1 - pdf_y0
            
            # Calculate scaling to fit the content within the fixed dimensions (preserving aspect ratio)
            scale_x = (output_width - 2*self.margin) / clip_width
            scale_y = (output_height - 2*self.margin) / clip_height
            content_scale = min(scale_x, scale_y)
            
            # Calculate the actual content size after scaling
            scaled_content_width = clip_width * content_scale
            scaled_content_height = clip_height * content_scale
            
            # Calculate centering offsets
            offset_x = (output_width - scaled_content_width) / 2
            offset_y = (output_height - scaled_content_height) / 2
            
        else:
            # Use bounding box size (original behavior)
            clip_width = pdf_x1 - pdf_x0
            clip_height = pdf_y1 - pdf_y0
            output_width = clip_width + 2*self.margin
            output_height = clip_height + 2*self.margin
            content_scale = 1.0
            offset_x = self.margin
            offset_y = self.margin
            scaled_content_width = clip_width
            scaled_content_height = clip_height
        
        # Create output PDF with appropriate size
        outpdf = pymupdf.open()
        outpage = outpdf.new_page(width=output_width, height=output_height)
        
        # Show the clipped region on the new page
        outpage.show_pdf_page(
            pymupdf.Rect(offset_x, offset_y, 
                        offset_x + scaled_content_width, 
                        offset_y + scaled_content_height),
            self.doc,
            pno=page_number,
            clip=clip_rect,
        )

        uuid_tag = str(uuid.uuid4())
        
        # Use provided clips_dir or fall back to default
        if clips_dir is None:
            clips_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'clips')
        
        save_path = os.path.join(clips_dir, f"{page_number+1}_{uuid_tag}_clip.pdf")
        
        outpdf.save(save_path)
        outpdf.close()
        
        return uuid_tag

    def auto_clip_page(self, page_number):
        # TODO: This method needs proper ML model import
        # Commenting out to prevent runtime errors until macro is properly imported
        pass
        # page = self.doc[page_number]
        # pix = page.get_pixmap()
        # temp_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'temp')
        # os.makedirs(temp_dir, exist_ok=True)
        # temp_file = os.path.join(temp_dir, 'temp.jpg')
        # pix.save(temp_file)
        # results = macro.predict(temp_dir)  # macro is not defined
        # print('this is it')

        # for result in results:
        #     for box in result.boxes:
        #         cls_id = int(box.cls[0].item())
        #         conf = float(box.conf[0].item())
        #         xyxyn = box.xyxyn[0].tolist()
        #         page = self.doc[page_number]
        #         bbox = convert_xyxyn2bbox(xyxyn, page.rect.width, page.rect.height)
        #         self.clip_region(page_number, bbox, sizing_mode='fixed-size', fixed_width=640, fixed_height=640)


    def save_clips(self, src_path, save_path):
        outpdf = pymupdf.open()
        clips = [f for f in os.listdir(src_path) if f.endswith(".pdf")]
        
        # Sort clips by creation time to maintain the order they were taken
        clip_paths = [os.path.join(src_path, clip) for clip in clips]
        clip_paths.sort(key=lambda x: os.path.getctime(x))

        for full_path in clip_paths:
            src_pdf = pymupdf.open(full_path)
            outpdf.insert_pdf(src_pdf)
            src_pdf.close()

        outpdf.save(save_path)
        outpdf.close()

    def parse_page(self, page_number, save_path):
        page = self.doc[page_number]
        paths = page.get_drawings()
        # folder = os.path.join(save_path, f"Page_{page_number}")
        # os.makedirs(folder, exist_ok=True)

        points = []

        outpdf_parse = pymupdf.open()

        outpdf_bbox = pymupdf.open()
        outpage_bbox = outpdf_bbox.new_page(
            width=page.rect.width, height=page.rect.height
        )
        outpage_bbox.show_pdf_page(page.rect, self.doc, page_number)

        for path in paths:
            for item in path["items"]:
                if item[0] == "l":
                    points.append([item[1].x, item[1].y])
                    points.append([item[2].x, item[2].y])
                elif item[0] == "re":
                    points.append([item[1].x0, item[1].y0])
                    points.append([item[1].x1, item[1].y1])
                elif item[0] == "qu":
                    # shape.draw_quad(item[1])
                    # print("Quad")
                    continue
                elif item[0] == "c":
                    # shape.draw_bezier(item[1], item[2], item[3], item[4])
                    # print("Curve")
                    continue
                else:
                    raise ValueError("unhandled drawing", item)

        p = np.array(points)

        db = DBSCAN(eps=self.eps, min_samples=self.min_samples).fit(p)
        labels = np.unique(db.labels_)

        for l in labels:
            if l != -1:
                filtered_pts = p[db.labels_ == l]

                outpage_parse = outpdf_parse.new_page(
                    width=self.page_size[0], height=self.page_size[1]
                )
                draw_region(
                    self.doc,
                    outpage_parse,
                    page_number,
                    filtered_pts,
                    self.page_size[0],
                    self.page_size[1],
                    self.margin,
                )
                # draw_bbox(outpage_bbox, filtered_pts)

        outpdf_parse.save(os.path.join(save_path, f"parse_{page_number}.pdf"))
        # outpdf_bbox.save(folder + "/bbox" + str(page_number) + ".pdf")

    def parse_pdf(self, output_dir="Blueprint"):
        for i in range(len(self.doc)):
            self.parse_page(i, output_dir)
