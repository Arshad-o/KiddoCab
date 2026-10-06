import re

def update_api_key():
    filepath = 'android/app/src/main/AndroidManifest.xml'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    old_key = "AIzaSyDsWdJ_AOzgNt-_SQk2AbTaxv1r6pShx-A"
    new_key = "AIzaSyBNle_4M8ztZ2sPaJym6CNLUQP-aaIGl7w"
    
    content = content.replace(old_key, new_key)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
        
update_api_key()
