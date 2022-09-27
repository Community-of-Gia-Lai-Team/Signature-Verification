from keras.applications.vgg16 import VGG16, preprocess_input
from scipy.spatial import distance
from keras.models import Model
import cv2
import numpy as np

def init_model():
    vgg16_model = VGG16(weights="imagenet")
    extract_model = Model(inputs=vgg16_model.inputs, outputs = vgg16_model.get_layer("fc1").output)
    return extract_model

def image_preprocess(img):
    img = cv2.resize(img, (224,224))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3,3), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    img = cv2.bitwise_not(thresh)
    img = cv2.merge([img,img,img])
    x = np.expand_dims(img, axis=0)
    x = preprocess_input(x)
    return x

def extract_vector(model, img):
    img_tensor = image_preprocess(img)
    vector = model.predict(img_tensor)[0]
    vector = vector / np.linalg.norm(vector)
    return vector

def predict(model, img, loaded_vectors):
    loaded_vectors = np.array(loaded_vectors)
    db_vectors = loaded_vectors[:,0]
    labels = loaded_vectors[:,1]
    query_vector = extract_vector(model, img)
    similarity_lst = [1 - distance.cosine(query_vector, vector) for vector in db_vectors]
    idx = np.argmax(similarity_lst)
    pred_class = labels[idx]
    similarity_percent = similarity_lst[idx]
    return pred_class, similarity_percent