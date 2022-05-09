import json

with open("max2pd.json") as json_file:
    data = json.load(json_file)

print(data['udpreceive'])