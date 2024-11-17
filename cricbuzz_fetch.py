import http.client

conn = http.client.HTTPSConnection("cricbuzz-cricket.p.rapidapi.com")

headers = {
    'x-rapidapi-key': "58be1a722dmsh13b696c13b663cep1e5bd7jsn3e4cb3355566",
    'x-rapidapi-host': "cricbuzz-cricket.p.rapidapi.com"
}

conn.request("GET", "/matches/v1/recent", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))


