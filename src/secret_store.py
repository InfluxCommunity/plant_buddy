import json
def get_bucket_secret():
    # JSON file
    f = open ('token.json', "r")
    dict = json.loads(f.read())

    return dict["token"]
