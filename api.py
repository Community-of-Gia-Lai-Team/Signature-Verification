from fastapi import FastAPI, Request
import uvicorn
import os
from recognize import signature_recognize

app = FastAPI()

@app.post('/recognize')
async def recognize_signature(request: Request):
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

    results = signature_recognize(img_path)

    if not results['signature_found']:
        return {
            'code': 200,
            'message': 'Not found signature'
        }

    return {
            'code': 200,
            'signature': results['data']
        }
    
if __name__ == "__main__":
    uvicorn.run("api:app", host='0.0.0.0', port=8080, reload=True, debug=True)


