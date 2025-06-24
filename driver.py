from parser import BlueprintParser

b = BlueprintParser("Blueprint.pdf", eps=110, min_samples=100)
# b.parse_page(34, "Drawings")
# b.parse_pdf()
b.clip_region(34, [1141, 89, 1653, 507])
