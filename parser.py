import pymupdf
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
import math

def compute_bounding_box(pts):
        x0 = min(pts[:, 0])
        x1 = max(pts[:, 0])
        y0 = min(pts[:, 1])
        y1 = max(pts[:, 1])

        return (x0, y0, x1, y1)

def draw_shapes(items, pts, shape, width, height, margin):
    x0, y0, x1, y1 = compute_bounding_box(pts)
    dw = x1 - x0
    dh = y1 - y0
    cw = width - (2 * margin) 
    ch = height - (2 * margin) 

    scale_x = cw / dw
    scale_y = ch / dh
    scale = min(scale_x, scale_y)

    cx_drawing = (x1 + x0)/2
    cy_drawing = (y1 + y0)/2

    cx_canvas = width/2
    cy_canvas = height/2

    dx = cx_canvas - scale * cx_drawing
    dy = cy_canvas - scale * cy_drawing

    for item in items:
        if item != 0:
            if item[0] == "l":
                p1 = pymupdf.Point(item[1].x * scale + dx, item[1].y * scale + dy)
                p2 = pymupdf.Point(item[2].x * scale + dx, item[2].y * scale + dy)
                shape.draw_line(p1, p2)
            elif item[1] == "re":
                x0 = item[1].x0 * scale + dx
                x1 = item[1].x1 * scale + dx
                y0 = item[1].y0 * scale + dy
                y1 = item[1].y1 * scale + dy
                shape.draw_rect(x0, y0, x1, y1)

    shape.finish()

def draw_region(src, page, points, width, height, margin):
    bbox = compute_bounding_box(points) 

    page.show_pdf_page(
        pymupdf.Rect(margin, margin, width-margin, height-margin),
        src,
        pno=34,
        clip=bbox
    )

def draw_bbox(page, points):
    bbox = compute_bounding_box(points)
    rect = pymypdf.Rect(bbox)

    page.draw_rect(
        rect,
        color=(1, 0, 0),
        width=0.5
    )

    doc

class BlueprintParser:

    def __init__(self, path, page_size=(640, 640), margin=20, eps=75, min_samples=2):
        self.path = path
        self.page_size = page_size
        self.margin = margin
        self.eps = eps
        self.min_samples = min_samples

    
    def copy_page(self, page_number):
        doc = pymupdf.open(self.path)
        page = doc[page_number]
        
        paths = page.get_drawings()
        text = page.get_text("dict")

        outpdf = pymupdf.open()
        outpage = outpdf.new_page(width=page.rect.width, height=page.rect.height)
        shape = outpage.new_shape()

        # WRITING TEXT
       
        for block in text["blocks"]:
            if block["type"] != 0:
                continue  # skip images and other non-text blocks

            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"]
                    x, y, _, _ = span["bbox"]  # top-left of text box
                    font = span["font"]
                    size = span["size"]
                    dx, dy = line["dir"]
                    angle = math.degrees(math.atan2(dy, dx))

                    # Insert text
                    outpage.insert_text(
                        (x, y),
                        text,
                        fontname='helv',
                        fontsize=size,
                        color=(0, 0, 0),
                        rotate=angle,
                        render_mode=0,  # 0 = fill (normal text)
                    )

        # DRAWING SHAPES
        for path in paths:
            for item in path["items"]:
                if item[0] == "l":  # line
                    shape.draw_line(item[1], item[2])
                elif item[0] == "re":  # rectangle
                    shape.draw_rect(item[1])
                elif item[0] == "qu":  # quad
                    shape.draw_quad(item[1])
                elif item[0] == "c":  # curve
                    shape.draw_bezier(item[1], item[2], item[3], item[4])
                else:
                    raise ValueError("unhandled drawing", item)

        shape.finish()
        shape.commit()
        outpdf.save('copy_page.pdf')
        

    def parse_page(self, page_number):
        doc = pymupdf.open(self.path)
        page = doc[page_number]
        paths = page.get_drawings()

        points = []
        shapes = []

        outpdf = pymupdf.open()

        for path in paths:
            for item in path["items"]:  
                if item[0] == "l":  
                    shapes.append(item)
                    shapes.append(0)
                    points.append([item[1].x, item[1].y])
                    points.append([item[2].x, item[2].y])
                elif item[0] == "re":  
                    shapes.append(item)
                    shapes.append(0)
                    points.append([item[1].x0, item[1].y0])
                    points.append([item[1].x1, item[1].y1])
                elif item[0] == "qu": 
                    # shape.draw_quad(item[1])
                    print("Quad")
                elif item[0] == "c": 
                    # shape.draw_bezier(item[1], item[2], item[3], item[4])
                    print("Curve")
                else:
                    raise ValueError("unhandled drawing", item)

        p = np.array(points)
        s = np.array(shapes, dtype=object)

        db = DBSCAN(eps=self.eps, min_samples=self.min_samples).fit(p)
        labels = np.unique(db.labels_)

        for l in labels:
            if l != -1:
                filtered_pts = p[db.labels_ == l]
                filtered_shapes = s[db.labels_ == l]

                outpage = outpdf.new_page(width=self.page_size[0], height=self.page_size[1])
                # shape = outpage.new_shape()

                # draw_shapes(filtered_shapes, filtered_pts, shape, self.page_size[0], self.page_size[1], self.margin)
                draw_region(doc, outpage, filtered_pts, self.page_size[0], self.page_size[1], self.margin)
                draw_bbox(page, filtered_pts)
                # shape.commit()
        
        outpdf.save("parsed.pdf") 

# Main code
b = BlueprintParser(path="../Blueprint.pdf", eps=100, min_samples=100)
b.parse_page(34)

