import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

req = urllib.request.Request("https://api.github.com/repos/Arshad-o/KiddoCab/actions/runs")
req.add_header('Accept', 'application/vnd.github.v3+json')
with urllib.request.urlopen(req, context=ctx) as response:
    data = json.loads(response.read().decode())
    
latest_run = data['workflow_runs'][0]
print(f"Run ID: {latest_run['id']}")

jobs_url = latest_run['jobs_url']
with urllib.request.urlopen(urllib.request.Request(jobs_url, headers={'Accept': 'application/vnd.github.v3+json'}), context=ctx) as response:
    jobs_data = json.loads(response.read().decode())

job = jobs_data['jobs'][0]
print(f"Job ID: {job['id']}")
print(f"HTML URL: {job['html_url']}")
