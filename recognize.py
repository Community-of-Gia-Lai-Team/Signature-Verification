import cv2
import os
import vgg16
from align import convert, denormalize_cord, customize_boxes
from yolov7.detect import detect
from config import THRESHOLD, ALIGNED_PATH, SIGNATURE_PATH
import time

def cleaning(sig_path):
    if not os.path.isdir(sig_path):
        os.mkdir(sig_path)
    else:
        for item in os.listdir(sig_path):
            os.remove(os.path.join(sig_path, item))

def signature_recognize(yolo_model, img_path, features_vectors , model_vgg, thresh=THRESHOLD, aligned_path=ALIGNED_PATH, signature_path=SIGNATURE_PATH):
    
    """
        Parameters:
            yolo_model: loaded yolo model
            img_path [str]: Path of your image
            features_vectors [list]: list of features vectors
            thresh [float]: Threshold to decide the class of signature. 
            vector_path [str]: Path of vectors extracted
            aligned_path [str]: Path of folder which contains aligned image
            signature_path [str]: Path of folder which saves cropped signature
            ui [bool]: Check which api is called (UI or NoUI)
    """

    # start = time.time()
    img = cv2.imread(img_path)
    aligned_img, _ = convert(img, save_mode='binary')
    h, w, _ = aligned_img.shape
    pred = detect(yolo_model, os.path.join(aligned_path, 'aligned.png'))
    boxes = [customize_boxes(denormalize_cord(box[1:],w,h),w,h,30) for box in pred]

    if len(boxes) > 0:
        cleaning(signature_path)
        vectors = features_vectors
        results = []

        for idx, box in enumerate(boxes):
            x1,y1,x2,y2 = box
            copy_img = aligned_img.copy()
            cropped_img = copy_img[y1:y2,x1:x2]
            signature_name = f'signature_{idx}.png'
            cv2.imwrite(os.path.join(signature_path, signature_name), cropped_img)
            pred_class, class_prob = vgg16.predict(model_vgg, cropped_img, vectors)
            
            if class_prob >= thresh:
                # print(f"Signature of {pred_class} recognized! ({class_prob})")
                results.append({
                    'img_name': signature_name,
                    'class': pred_class,
                    'conf': round(class_prob*100,2),
                    'message': 'Signature recognized'
                })
            else:
                # print("New signature recognized!")
                results.append({
                    'img_name': signature_name,
                    'class': 'New class', # New signature
                    'conf': round(class_prob*100,2),
                    'message': 'New signature recognized'
                })
        return {
                'signature_found': True,
                'data': results
        }
    else:
        # print("No signature found!")
        return {
                'signature_found': False,
        }

    # print(f'Time taken: {round(time.time()- start,2)}s')
