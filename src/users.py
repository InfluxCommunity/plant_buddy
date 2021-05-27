def authorize_and_get_user(request):
    return {"user_name": "rick"}

def notify_user(message):
    print(message)

def is_influx(request):
    return True