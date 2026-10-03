import urllib.request
import zipfile
import io
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://github.com/Arshad-o/KiddoCab/actions/runs/37133799600/logs"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, context=ctx) as response:
        content = response.read()
        
    with zipfile.ZipFile(io.BytesIO(content)) as z:
        for filename in z.namelist():
            if "Build APK" in filename or "build" in filename.lower():
                with z.open(filename) as f:
                    log_data = f.read().decode('utf-8')
                    print(f"=== {filename} ===")
                    print(log_data[-2000:])
                    break
except Exception as e:
    print(f"Error: {e}")
