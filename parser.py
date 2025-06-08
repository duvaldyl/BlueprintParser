import pymupdf
import numpy as np
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt
import os

def compute_bounding_box(pts):
        x0 = min(pts[:, 0])
        x1 = max(pts[:, 0])
        y0 = min(pts[:, 1])
        y1 = max(pts[:, 1])

        return (x0, y0, x1, y1)

def draw_region(src, page, page_number, points, width, height, margin):
    bbox = compute_bounding_box(points) 

    page.show_pdf_page(
        pymupdf.Rect(margin, margin, width-margin, height-margin),
        src,
        pno=page_number,
        clip=bbox
    )

def draw_bbox(page, points):
    bbox = compute_bounding_box(points)

    page.draw_rect(
        bbox,
        color=(1, 0, 0),
        width=0.5
    )

def get_drawing_coordinates(paths):
    points = []
    for path in paths:
        for item in path["items"]:  
            if item[0] == "l":  
                points.append([item[1].x, item[1].y])
                points.append([item[2].x, item[2].y])
            elif item[0] == "re":  
                points.append([item[1].x0, item[1].y0])
                points.append([item[1].x1, item[1].y1])
            elif item[0] == "qu": 
                points.append(item[1].ul)
                points.append(item[1].ur)
                points.append(item[1].ll)
                points.append(item[1].lr)
            elif item[0] == "c": 
                # TODO
                # shape.draw_bezier(item[1], item[2], item[3], item[4])
                continue
            else:
                raise ValueError("unhandled drawing", item)

    return np.array(points)

def get_text_coordinates(text):
    points = []
    
    for block in text["blocks"]:
        if block["type"] != 0:
            continue

        for line in block["lines"]:
            for span in line["spans"]:
                bbox = span["bbox"]
                points.append([bbox[0], bbox[1]])
                points.append([bbox[2], bbox[3]])

    return np.array(points)

class BlueprintParser:

    def __init__(self, path, page_size=(640, 640), margin=20, eps=75, min_samples=100):
        self.path = path
        self.doc = pymupdf.open(path)
        self.page_size = page_size
        self.margin = margin
        self.eps = eps
        self.min_samples = min_samples
    
    def parse_page(self, page_number, save_path):
        print("Parsing page: " + str(page_number) + "...")
        page = self.doc[page_number]

        paths = page.get_drawings()
        text = page.get_text('dict')

        folder = save_path + '/Page_' + str(page_number)
        os.makedirs(folder, exist_ok=True)

        outpdf_parse = pymupdf.open()

        outpdf_bbox = pymupdf.open()
        outpage_bbox = outpdf_bbox.new_page(width=page.rect.width, height=page.rect.height)
        outpage_bbox.show_pdf_page(page.rect, self.doc, page_number)

        s = get_drawing_coordinates(paths) 
        t = get_text_coordinates(text)

        plt.scatter(s[:,0], -1 * s[:, 1], s=1, color='blue')
        plt.scatter(t[:, 0], -1 * t[:, 1], s=1, color='orange')

        plt.savefig(folder + "/scatter" + str(page_number) + ".png")
        plt.clf()

        c = np.concatenate((s, t))

        db = DBSCAN(eps=self.eps, min_samples=self.min_samples).fit(c)
        labels = np.unique(db.labels_)

        for l in labels:
            if l != -1:
                filtered_pts = c[db.labels_ == l]

                outpage_parse = outpdf_parse.new_page(width=self.page_size[0], height=self.page_size[1])
                draw_region(self.doc, outpage_parse, page_number, filtered_pts, self.page_size[0], self.page_size[1], self.margin)
                draw_bbox(outpage_bbox, filtered_pts)
        
        outpdf_parse.save(folder + "/parse_" + str(page_number) + ".pdf") 
        outpdf_bbox.save(folder + "/bbox_" + str(page_number) + ".pdf")

    def parse_pdf(self):
        for i in range(len(self.doc)):
            self.parse_page(i, "Blueprint")

