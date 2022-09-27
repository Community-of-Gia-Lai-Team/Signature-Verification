import cv2
import pickle
import vgg16
from align import convert, denormalize_cord, customize_boxes
from yolov7.detect import detect
import time

GENUINE_THRESHOLD = 0.9
FORGED_THRESHOLD = 0.8
img_path = 'test/test2.png'

model_vgg = vgg16.init_model()
start = time.time()
img = cv2.imread(img_path)
aligned_img, is_success = convert(img, save_mode='binary')
h, w, _ = aligned_img.shape
pred = detect('aligned/aligned.png')
boxes = [customize_boxes(denormalize_cord(box[1:],w,h),w,h,30) for box in pred]

if len(boxes) > 0:
    vectors = pickle.load(open('data/vectors.pkl', 'rb'))
    for box in boxes:
        x1,y1,x2,y2 = box
        copy_img = aligned_img.copy()
        cropped_img = copy_img[y1:y2,x1:x2]
        pred_class, class_prob = vgg16.predict(model_vgg, cropped_img, vectors)
        if FORGED_THRESHOLD <= class_prob < GENUINE_THRESHOLD:
            print(f"Forged signature of {pred_class} recognized! ({class_prob})")
        elif class_prob >= GENUINE_THRESHOLD:
            print(f"Signature of {pred_class} recognized! ({class_prob})")
        elif class_prob < FORGED_THRESHOLD:
            print("New signature recognized!")
else:
    print("No signature found!")

print(f'Time taken: {round(time.time()- start,2)}s')
