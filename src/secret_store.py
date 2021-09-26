import json
def get_bucket_secret():
    # JSON file
    f = open ('/Users/jayclifford/Documents/repos/IoT_Plant_Demo/plant-buddy/src/secret/token.json', "r")
    dict = json.loads(f.read())

    return dict["token"]
