import cv2
import torch
import os
from ultralytics import YOLO
from PIL import Image
from preprocess_food_barcode import run_preprocess
from pyzbar.pyzbar import decode


model_path = "D:\\Projects\\Food Barcode Object Detection\\Models\\Final Model and Dataset Selection Version 2\\yolov9s_barcode_detection_model\\weights\\yolov9s_barcode_detection.pt"
MODEL = YOLO(model_path)
class_name = ["Barcode"]
barcode_categories = {"0": "Barcode", "1": "Error Barcode"}

def decode_barcode(image, detection):
    barcodes = []
    
    x_min, y_min, x_max, y_max = map(int, detection["bbox"][0])
    barcode_region = image[y_min:y_max, x_min:x_max]
    # cv2.imwrite("D:\\Projects\\Food Barcode Object Detection\\Tests\\before_black_white_7.jpg", barcode_region)
    # gray = cv2.cvtColor(barcode_region, cv2.COLOR_BGR2GRAY)

    # Convert colored barcode to black
    # _, binary = cv2.threshold(gray, 149, 255, cv2.THRESH_BINARY)
    # _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)

    
    # cv2.imwrite("D:\\Projects\\Food Barcode Object Detection\\Tests\\after_black_white_7.jpg", binary)
    
    barcode_data = decode(barcode_region)
    for barcode in barcode_data:
        barcodes.append(barcode.data.decode("utf-8"))
        
    return barcodes


def preprocess_img(img):
    pre_proc_image = run_preprocess(img)
    return pre_proc_image
 
 
def detect_objects(image, img_name):
    results = MODEL(image)
    detections = []
    for result in results:
        for box in result.boxes:
            class_id = int(box.cls.item())  
            class_name = result.names[class_id]  
            detections.append({
                'img_name': img_name,
                'class': class_name,
                'confidence': box.conf.item(),  
                'bbox': box.xyxy.tolist()  
            })
    return detections


def draw_yolo_bboxes(image, all_detections):


    for detection in all_detections:
                
        label = detection["class"]
        
        x_min, y_min, x_max, y_max = map(int, detection["bbox"][0])

        color = (0, 255, 0) if label == "Barcode" else (0, 0, 255)  
        cv2.rectangle(image, (x_min, y_min), (x_max, y_max), color, 3)
        cv2.putText(image, label, (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    return image

 
def run_detect(image, raw_image, img_name):

    all_barcode_detections = []
    # all_error_barcode_detections = []
    
    detections = detect_objects(image, img_name)
    
    for detection in detections:
        if detection["class"] == "Barcode":
            
            all_barcode_detections.extend(decode_barcode(image, detection))
        
        if detection["class"] == "Error Barcode":
            error_barcode_values = decode_barcode(raw_image, detection)
            # all_error_barcode_detections.append(error_barcode_values)
            pass
    
    food_barcode_image = draw_yolo_bboxes(raw_image, detections)
    barcode_text = "\n".join(all_barcode_detections) if all_barcode_detections else "No Barcode Detected"
    return food_barcode_image, f"The number of Barcode Detections: {len(all_barcode_detections)} \n\n The Barcode number:{barcode_text}", barcode_text


def get_img(image, img_name): 
    preproc_image = preprocess_img(image)
    food_barcode_image, barcode_detection_text, barcode_text = run_detect(preproc_image, image, img_name)
    return food_barcode_image, barcode_detection_text, barcode_text


def real_time_detection(frame_resized, frame, expected_barcode_count=2):
    decode_barcodes = set()
    results = MODEL(frame_resized)
    for r in results:
        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0].int().tolist()
            cv2.rectangle(frame, (x1, y1), (x2, y2), (245, 0, 0), 1)
            confidence = torch.ceil(box.conf[0] * 100) / 100
            cls = str(box.cls[0].int().item())
            
            if barcode_categories[cls] == "Barcode":
                barcode_values = decode_barcode(frame, {"bbox": [x1, x2, y1, y2]})
                decode_barcodes.update(barcode_values)
                
            if len(decode_barcodes) >= expected_barcode_count:
                return frame
            
            org = (x1, y1 - 10)  
            font = cv2.FONT_HERSHEY_SIMPLEX
            fontScale = 0.3  
            color = (255, 0, 0)
            thickness = 1  
            cv2.putText(frame, f"{barcode_categories[cls]} {confidence}", org, font, fontScale, color, thickness)
            
    return frame


def run_ui(img, img_name):
    barcode_img, barcode_txt, bar_txt = get_img(img, img_name)
    return barcode_img, barcode_txt, bar_txt



