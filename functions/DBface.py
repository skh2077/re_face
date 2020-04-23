import numpy as np
import torch
import torch.nn.functional as F
import torch.nn as nn
import cv2
import sys

HAS_CUDA = torch.cuda.is_available()
sys.path.append('..')
dbfacemod = __import__('DBFace.model.DBFace')
dbfacecommon = __import__('DBFace.common')
def nms(objs, iou=0.5):

    if objs is None or len(objs) <= 1:
        return objs

    objs = sorted(objs, key=lambda obj: obj.score, reverse=True)
    keep = []
    flags = [0] * len(objs)
    for index, obj in enumerate(objs):

        if flags[index] != 0:
            continue

        keep.append(obj)
        for j in range(index + 1, len(objs)):
            if flags[j] == 0 and obj.iou(objs[j]) > iou:
                flags[j] = 1
    return keep


def detect(model, image, threshold=0.4, nms_iou=0.5):

    mean = [0.408, 0.447, 0.47]
    std = [0.289, 0.274, 0.278]

    image = dbfacecommon.common.pad(image)
    image = ((image / 255.0 - mean) / std).astype(np.float32)
    image = image.transpose(2, 0, 1)

    torch_image = torch.from_numpy(image)[None]
    if HAS_CUDA:
        torch_image = torch_image.cuda()

    hm, box, landmark = model(torch_image)
    hm_pool = F.max_pool2d(hm, 3, 1, 1)
    scores, indices = ((hm == hm_pool).float() * hm).view(1, -1).cpu().topk(1000)
    hm_height, hm_width = hm.shape[2:]

    scores = scores.squeeze()
    indices = indices.squeeze()
    ys = list((indices / hm_width).int().data.numpy())
    xs = list((indices % hm_width).int().data.numpy())
    scores = list(scores.data.numpy())
    box = box.cpu().squeeze().data.numpy()
    landmark = landmark.cpu().squeeze().data.numpy()

    stride = 4
    objs = []
    for cx, cy, score in zip(xs, ys, scores):
        if score < threshold:
            break

        x, y, r, b = box[:, cy, cx]
        xyrb = (np.array([cx, cy, cx, cy]) + [-x, -y, r, b]) * stride
        x5y5 = landmark[:, cy, cx]
        x5y5 = (dbfacecommon.common.exp(x5y5 * 4) + ([cx]*5 + [cy]*5)) * stride
        box_landmark = list(zip(x5y5[:5], x5y5[5:]))
        objs.append(dbfacecommon.common.BBox(0, xyrb=xyrb, score=score, landmark=box_landmark))
    return nms(objs, iou=nms_iou)


def detect_image(model, file):

    image = dbfacecommon.common.imread(file)
    objs = detect(model, image)

    for obj in objs:
        dbfacecommon.common.drawbbox(image, obj)

    dbfacecommon.common.imwrite("detect_result/" + dbfacecommon.common.file_name_no_suffix(file) + ".draw.jpg", image)



def image_demo():

    dbface = dbfacemod.model.DBFace.DBFace()
    dbface.eval()

    if HAS_CUDA:
        dbface.cuda()

    dbface.load("../DBFace/model/dbface.pth")
    print('loaded')
    detect_image(dbface, "samples/images.jpg")
