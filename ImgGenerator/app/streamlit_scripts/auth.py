import requests

def check_auth(username, password, server_url):
    response = requests.post(f'{server_url}/auth/login/', data={'username': username, 'password': password})
    data = response.json()
    if data.get('status') == 'success':
        return True, response.cookies["sessionid"]
    else:
        return False, None
    
