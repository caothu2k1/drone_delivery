import firebase_admin
from firebase_admin import credentials, db, storage
import datetime
import time
import urllib.request
import urllib.error
from retrying import retry

class FireBase:
    def __init__(self, path, URL):
        self.cred = credentials.Certificate(path)
        firebase_admin.initialize_app(self.cred, URL)
        self.bucket = storage.bucket()

    @retry(stop_max_attempt_number=3, wait_fixed=2000)
    def sendData(self, path, data):
        try:
            ref = db.reference(path)
            ref.set(data)
        except Exception as e:
            print(f"Error sending data to {path}: {e}")
            raise

    @retry(stop_max_attempt_number=3, wait_fixed=2000)
    def getData(self, path):
        try:
            ref = db.reference(path)
            return ref.get()
        except Exception as e:
            print(f"Error getting data from {path}: {e}")
            raise
    
    def uploadImg(self, image_bytes, path=None):
        filename = f'image_{time.time()}.jpg'
        blob = self.bucket.blob(filename)
        blob.upload_from_string(image_bytes, content_type='image/jpg')
        url = blob.generate_signed_url(datetime.timedelta(seconds=300), method='GET')
        if path:
            self.sendData(path, url)
        return url

    def Network(self):
        try:
            urllib.request.urlopen("http://google.com", timeout=5)
            return True
        except urllib.error.URLError as e:
            print(e)
            return False
        except ConnectionResetError:
            time.sleep(1)
            return self.Network()
