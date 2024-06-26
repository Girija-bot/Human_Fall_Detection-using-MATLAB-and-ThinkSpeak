import cv2
import numpy as np
import asyncio
from aiocoap import Context, Message
from aiocoap.numbers.codes import Code
import os

# Supporting functions

def modify_mask(fg_mask, strel_type, strel_size):
    kernel = cv2.getStructuringElement(strel_type, (strel_size, strel_size))
    fg_close = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
    return fg_close

def mask_inside_bbox(fg_mask, bbox):
    fg_bbox = np.zeros_like(fg_mask)
    fg_bbox[bbox[1]:bbox[1]+bbox[3], bbox[0]:bbox[0]+bbox[2]] = fg_mask[bbox[1]:bbox[1]+bbox[3], bbox[0]:bbox[0]+bbox[2]]
    return fg_bbox

def calc_speed(mhimage, fg_bbox, tmhi):
    timestamp = 1
    mhimage[fg_bbox > 0] = timestamp
    mhimage[mhimage > 0] += 1
    mhimage[mhimage >= tmhi] = 0
    return mhimage

def is_fall_detected(mhimage):
    # Implement your fall detection logic here
    # This is a placeholder for demonstration
    return True

async def send_coap_message(message):
    context = await Context.create_client_context()
    request = Message(code=Code.POST, payload=message.encode('utf-8'))
    request.set_request_uri('coap://localhost/input')
    await context.request(request).response

def save_frame(frame, filename):
    cv2.imwrite(filename, frame)

def fall_detection():
    vid = cv2.VideoCapture("C:/Users/lenovo/Documents/MATLAB/Indust/falling.mp4")

    fgbg = cv2.createBackgroundSubtractorMOG2(history=10, varThreshold=5, detectShadows=True)
    tmhi = 15
    strel_type = cv2.MORPH_RECT
    strel_size = 5
    mhimage = None

    frame_no = 0
    while vid.isOpened():
        ret, frame = vid.read()
        if not ret:
            break
        frame_no += 1

        if frame_no == 1:
            mhimage = np.zeros((frame.shape[0], frame.shape[1]), dtype=np.uint8)

        fg_mask = fgbg.apply(frame)
        fg_close = modify_mask(fg_mask, strel_type, strel_size)

        contours, _ = cv2.findContours(fg_close, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        areas = [cv2.contourArea(contour) for contour in contours]

        if areas:
            max_area_idx = np.argmax(areas)
            max_contour = contours[max_area_idx]
            x, y, w, h = cv2.boundingRect(max_contour)
            bbox = (x, y, w, h)

            fg_bbox = mask_inside_bbox(fg_close, bbox)
            mhimage = calc_speed(mhimage, fg_bbox, tmhi)

            save_frame(frame, f'frame_{frame_no}_original.png')
            save_frame(fg_mask, f'frame_{frame_no}_fgmask.png')
            save_frame((mhimage * 255 / tmhi).astype(np.uint8), f'frame_{frame_no}_mhimage.png')

            if is_fall_detected(mhimage):
                asyncio.run(send_coap_message("Random data from Python"))
        else:
            save_frame(frame, f'frame_{frame_no}_original.png')
            save_frame(fg_mask, f'frame_{frame_no}_fgmask.png')
            save_frame((mhimage * 255 / tmhi).astype(np.uint8), f'frame_{frame_no}_mhimage.png')

    vid.release()

if __name__ == "__main__":
    fall_detection()
