import json
import sys
import urllib.request

url = "https://huggingface.co/api/spaces/YOSHIMITSU-777/orbitune-api"
response = urllib.request.urlopen(url).read()
d = json.loads(response)
rt = d.get('runtime', {})
print('Stage:', rt.get('stage'))
e = rt.get('errorMessage')
print('Error:', e[:200] if e else 'None')
print('Last modified:', d.get('lastModified'))