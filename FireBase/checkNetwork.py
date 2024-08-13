import time
import urllib
while True:
    try: urllib.request.urlopen("http://google.com")
    except urllib.error.URLError as e:
        print(e.reason)

    time.sleep(5)
    print("OK")