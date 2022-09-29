import cv2
import os
import pickle
import vgg16
from align import convert, denormalize_cord, customize_boxes
from yolov7.detect import detect
import time

def signature_recognize(img_path, GENUINE_THRESHOLD=0.9, FORGED_THRESHOLD=0.8, vector_path='data/vectors.pkl', aligned_path='aligned'):
    
    """
        Parameters:
            img_path [str]: path of your image
            GENUINE_THRESHOLD [float]: In order to recognize a signature is genuine, similarity value must greater than GENUINE_THRESHOLD. 
            FORGED_THRESHOLD [float]: In order to recognize a signature is forged, similarity value must in [FORGED_THRESHOLD, GENUINE_THRESHOLD)
            vector_path [str]: Path of vectors extracted
            aligned_path [str]: Path of folder which contains aligned image
    """

    model_vgg = vgg16.init_model()
    start = time.time()
    img = cv2.imread(img_path)
    aligned_img, _ = convert(img, save_mode='binary')
    h, w, _ = aligned_img.shape
    pred = detect(os.path.join(aligned_path, 'aligned.png'))
    boxes = [customize_boxes(denormalize_cord(box[1:],w,h),w,h,30) for box in pred]

    if len(boxes) > 0:
        vectors = pickle.load(open(vector_path, 'rb'))
        results = []
        for box in boxes:
            x1,y1,x2,y2 = box
            copy_img = aligned_img.copy()
            cropped_img = copy_img[y1:y2,x1:x2]
            pred_class, class_prob = vgg16.predict(model_vgg, cropped_img, vectors)
            if FORGED_THRESHOLD <= class_prob < GENUINE_THRESHOLD:
                # print(f"Forged signature of {pred_class} recognized! ({class_prob})")
                results.append({
                    'class': pred_class,
                    'message': 'Forged signature recognized'
                })
            elif class_prob >= GENUINE_THRESHOLD:
                # print(f"Signature of {pred_class} recognized! ({class_prob})")
                results.append({
                    'class': pred_class,
                    'message': 'Genuine signature recognized'
                })
            elif class_prob < FORGED_THRESHOLD:
                # print("New signature recognized!")
                results.append({
                    'class': 'New class', # New signature
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
