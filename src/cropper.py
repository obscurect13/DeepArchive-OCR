def crop_regions(image, boxes, padding=4):
    h, w = image.shape[:2]
    crops = []

    pad_offset = padding // 2

    for box in boxes:
        x1, x2 = min(box[0], box[2]), max(box[0], box[2])
        y1, y2 = min(box[1], box[3]), max(box[1], box[3])

        x1p = max(0, x1 - pad_offset)
        y1p = max(0, y1 - pad_offset)
        x2p = min(w, x2 + pad_offset)
        y2p = min(h, y2 + pad_offset)

        crop = image[y1p:y2p, x1p:x2p]
        if crop.size > 0:
            crops.append(crop)
    return crops
