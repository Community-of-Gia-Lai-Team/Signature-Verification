from fastapi import FastAPI, Request, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List
import uvicorn
import os
import pickle
from recognize import signature_recognize
from config import HOST, PORT, UPLOAD_PATH, SIGNATURE_PATH, FEATURES_PATH, REGISTER_PATH
import vgg16
from gan_files.test import load_gan_model
from yolov7.detect import load_model

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="views/templates")

@app.on_event("startup")
async def init_data():
    global FEATURES_VECTORS, MODEL_VGG, YOLO_MODEL, GAN_MODEL
    FEATURES_VECTORS = pickle.load(open(FEATURES_PATH, 'rb'))
    MODEL_VGG = vgg16.init_model()
    YOLO_MODEL = load_model()
    GAN_MODEL = load_gan_model()

@app.get('/')
async def homepage(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get('/register')
async def homepage(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post('/recognize')
def recognize_signature(image: UploadFile = File(...)):
    # If upload dir not exist -> Create
    if not os.path.isdir(UPLOAD_PATH):
        os.mkdir(UPLOAD_PATH)
    
    # Cleaning the folder before starting a new session
    for item in os.listdir(UPLOAD_PATH):
        os.remove(os.path.join(UPLOAD_PATH, item))
    
    # Get image from request
    file_location = f"./{UPLOAD_PATH}/{image.filename}"
    contents = image.file.read()
    with open(file_location, 'wb') as f:
        f.write(contents)
    
    # Detect and Recognize signatures
    results = signature_recognize(YOLO_MODEL, file_location, FEATURES_VECTORS, MODEL_VGG, GAN_MODEL)
    
    if results['signature_found']:
        return {
            'code': 200,
            'data': [(os.path.join(SIGNATURE_PATH,list(res.values())[0]), list(res.values())[1], list(res.values())[2]) for res in results['data']]
        }
    else:
        return {
            'code': 404
        }
    
@app.post('/noui/recognize')
async def recognize_signature_noui(request: Request):
    data = await request.json()
    img_path = data.get('img_path', False)
    
    if not img_path:
        return {
            'code': 404,
            'message': 'Request missing img_path'
        }

    if not os.path.isfile(img_path):
        return {
            'code': 404,
            'message': 'Not found image'
    }

    results = signature_recognize(YOLO_MODEL, img_path, FEATURES_VECTORS, MODEL_VGG, GAN_MODEL)

    if not results['signature_found']:
        return {
            'code': 200,
            'message': 'Not found signature'
        }

    return {
            'code': 200,
            'signature': results['data']
        }

@app.post('signature/register')
async def register_signature(name : str = Form(...), images: List[UploadFile] = File(...)):
    # If upload dir not exist -> Create
    if not os.path.isdir(REGISTER_PATH):
        os.mkdir(REGISTER_PATH)
    
    # Cleaning the folder before starting a new session
    for item in os.listdir(REGISTER_PATH):
        os.remove(os.path.join(REGISTER_PATH, item))

    for image in images:
        file_location = f"./{REGISTER_PATH}/{image.filename}"
        contents = await image.read()
        with open(file_location, 'wb') as f:
            f.write(contents)
    
    name = name.upper()

    for image in os.listdir(REGISTER_PATH):
        feature = vgg16.extract_vector(MODEL_VGG, os.path.join(REGISTER_PATH, image))
        FEATURES_VECTORS.append([feature, name])

    pickle.dump(FEATURES_VECTORS, open(FEATURES_PATH, 'wb'))
    
    return {
        'code': 200
    }

if __name__ == "__main__":
    uvicorn.run("api:app", host=HOST, port=PORT, reload=True, debug=True)

