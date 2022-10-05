import cv2
import os
import vgg16
from align import convert, denormalize_cord, customize_boxes
from cvtools import gan_preprocessing
from yolov7.detect import detect
from gan_files.test import remove_noise
from config import GAN_SOURCE_PATH, THRESHOLD, ALIGNED_PATH, SIGNATURE_PATH, GAN_OUTPUT_PATH
import time

def cleaning(path):
    if type(path) == str:
        if not os.path.exists(path):
            os.makedirs(path)
        else:
            for item in os.listdir(path):
                os.remove(os.path.join(path, item))
    elif type(path) == list:
        for p in path:
            if not os.path.exists(p):
                os.makedirs(p)
            else:
                for item in os.listdir(p):
                    os.remove(os.path.join(p, item))

def signature_recognize(yolo_model, img_path, features_vectors , model_vgg, gan_model ,thresh=THRESHOLD, aligned_path=ALIGNED_PATH, signature_path=SIGNATURE_PATH, gan_source_path = GAN_SOURCE_PATH, gan_output_path=GAN_OUTPUT_PATH):
    
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
        cleaning([signature_path, gan_output_path, gan_source_path])
        vectors = features_vectors
        model, opt, webpage = gan_model
        results = []

        for idx, box in enumerate(boxes):
            x1,y1,x2,y2 = box
            copy_img = aligned_img.copy()
            cropped_img = copy_img[y1:y2,x1:x2]
            signature_name = f'signature_{idx}.png'
            cv2.imwrite(os.path.join(signature_path, signature_name), cropped_img)
            gan_preprocessing(signature_name, cropped_img)

        remove_noise(model, opt, webpage)
        
        for idx, _ in enumerate(boxes):
            new_signature_name = f'signature_{idx}_fake.png'
            pred_class, class_prob = vgg16.predict(model_vgg, os.path.join(gan_output_path, new_signature_name), vectors)
            if class_prob >= thresh:
                # print(f"Signature of {pred_class} recognized! ({class_prob})")
                results.append({
                    'img_name': new_signature_name[:-9] + '.png',
                    'class': pred_class,
                    'conf': round(class_prob*100,2),
                    'message': 'Signature recognized'
                })
            else:
                # print("New signature recognized!")
                results.append({
                    'img_name': new_signature_name[:-9] + '.png',
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
