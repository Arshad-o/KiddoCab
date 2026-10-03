import urllib.request
import json
import ssl
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
req = urllib.request.Request('https://api.github.com/repos/Arshad-o/KiddoCab/actions/runs?per_page=20')
req.add_header('Accept', 'application/vnd.github.v3+json')
with urllib.request.urlopen(req, context=ctx) as response:
    runs = json.loads(response.read().decode())['workflow_runs']
for r in runs:
    print(f"{r['head_commit']['message'][:40]} : {r['conclusion']}")
