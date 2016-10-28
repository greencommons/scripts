import requests, json

# get all docs
# loop through adding ids to delete objects
# post qwiht requests

search_url = 'our cs search end point'
params = {'q': '-dogasfda', 'return': 'identifier', 'size': 1000}

r = requests.get(search_url, params=params)

docs = json.loads(r.text)

to_delete = []
for doc in docs['hits']['hit']:
	to_delete.append({'id': doc['id'], 'type': 'delete'})


print to_delete

url = 'our cloudsearch batch endpoint'
r = requests.post(url, json=to_delete)
print r.status_code
print r.text