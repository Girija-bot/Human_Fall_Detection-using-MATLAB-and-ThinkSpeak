from flask import Flask, render_template, jsonify
import cv2
import numpy as np
import asyncio
from aiocoap import Context, Message
from aiocoap.numbers.codes import Code
import threading

app = Flask(__name__)

# Global variable to store the fall detection status and frame number
fall_data = {
    'fall_detected': False,
    'frame_number': 0
}

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

def is_fall_detected(bbox_history):
    if len(bbox_history) < 2:
        return False

    x1, y1, w1, h1 = bbox_history[-2]
    x2, y2, w2, h2 = bbox_history[-1]

    aspect_ratio_change = (w2 / h2) - (w1 / h1)
    height_change = y2 - y1

    # Check for significant aspect ratio change and downward movement
    if aspect_ratio_change > 0.5 and height_change > 10:
        return True
    return False

async def send_coap_message(message):
    context = await Context.create_client_context()
    request = Message(code=Code.POST, payload=message.encode('utf-8'))
    request.set_request_uri('coap://localhost/input')
    await context.request(request).response

def fall_detection():
    vid = cv2.VideoCapture("C:/Users/lenovo/Documents/MATLAB/Indust/falling.mp4")

    fgbg = cv2.createBackgroundSubtractorMOG2(history=10, varThreshold=5, detectShadows=True)
    tmhi = 15
    strel_type = cv2.MORPH_RECT
    strel_size = 5
    mhimage = None

    frame_no = 0
    bbox_history = []

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
            bbox_history.append(bbox)

            fg_bbox = mask_inside_bbox(fg_close, bbox)
            mhimage = calc_speed(mhimage, fg_bbox, tmhi)

            if is_fall_detected(bbox_history):
                fall_data['fall_detected'] = True
                asyncio.run(send_coap_message("Fall detected"))
            else:
                fall_data['fall_detected'] = False
        else:
            fall_data['fall_detected'] = False

        fall_data['frame_number'] = frame_no

    vid.release()

@app.route('/')
def home():
    return render_template('index1.html')

@app.route('/status', methods=['GET'])
def status():
    return jsonify(fall_data)

def start_fall_detection():
    fall_detection_thread = threading.Thread(target=fall_detection)
    fall_detection_thread.start()

if __name__ == '__main__':
    start_fall_detection()
    app.run(debug=True)
