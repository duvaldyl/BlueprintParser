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

    def clip_region(self, page_number, bbox, scale=1):
        outpdf = pymupdf.open()
        outpage = outpdf.new_page(width=700, height=700)
        scale_bbox = tuple(map(lambda x: x/scale, bbox)) 
        
        outpage.show_pdf_page(
            pymupdf.Rect(self.margin, self.margin, 640-self.margin, 640-self.margin),
            self.doc,
            pno=page_number,
            clip=scale_bbox,
        )
        outpdf.save("clip.pdf")

    def parse_page(self, page_number, save_path):
        print("Parsing page: " + str(page_number) + "...")
        page = self.doc[page_number]
        paths = page.get_drawings()
        folder = save_path + "/Page_" + str(page_number)
        os.makedirs(folder, exist_ok=True)

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
                draw_bbox(outpage_bbox, filtered_pts)

        outpdf_parse.save(folder + "/parse_" + str(page_number) + ".pdf")
        outpdf_bbox.save(folder + "/bbox" + str(page_number) + ".pdf")

    def parse_pdf(self):
        for i in range(len(self.doc)):
            self.parse_page(i, "Blueprint")
