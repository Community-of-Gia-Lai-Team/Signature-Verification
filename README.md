# Signature Verification ✍️
## **Introduction**

A useful application verifying the signatures detected in paper document.

## **Installation**
``` bash
# Clone this repo
git clone https://github.com/ntvuongg/Signature-Verification.git
```
All requirement libraries are listed in **requirements.txt**. You can install it by using:
``` bash
# Virtual env recommended
pip install -r requirements.txt
```
or build through **[Docker](https://www.docker.com/)** by:
```
docker build -t <app_name> .
```

## **Usage**
``` python
python api.py
```
With Docker:
``` docker
docker run -p 8080:8080 <app_name>
```