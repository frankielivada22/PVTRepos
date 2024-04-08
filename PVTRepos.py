import requests
import base64
import json

GITHUB_USER = "username here"
GITHUB_TOKEN = "github token here (make sure it has access to repos and admin)"
REPOS_VISIBILITY_TYPE = "public" 
error_endpoints = [] 

def call_api(endpoint, method_type, has_post_params=False, post_params=None):
    headers = {
        "Authorization": f"Basic {b64_authentication()}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "request"
    }
    try:
        if has_post_params and post_params:
            response = requests.request(method_type, endpoint, headers=headers, json=post_params)
        else:
            response = requests.request(method_type, endpoint, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.exceptions.HTTPError as err:
        if err.response.status_code == 422:
            error_endpoints.append(endpoint)
        print(f"Error: {err}")
        return ""

def b64_authentication():
    auth_bytes = f"{GITHUB_USER}:{GITHUB_TOKEN}".encode("ascii")
    return base64.b64encode(auth_bytes).decode("ascii")

def convert_json(json_str):
    return json.loads(json_str)

def set_repo_to_private(endpoint):
    post_params = {"private": REPOS_VISIBILITY_TYPE == "public"}
    return call_api(endpoint, "PATCH", has_post_params=True, post_params=post_params)

def handle_json_for_private(json_data):
    for obj in json_data:
        print(f"endpoint: {obj['url']}")
        endpoint = obj['url']
        resp = set_repo_to_private(endpoint)
        if resp:
            resp_json = convert_json(resp)
            print(f"private = {resp_json.get('private')}")

def get_repos(page_no):
    endpoint = f"https://api.github.com/user/repos?visibility={REPOS_VISIBILITY_TYPE}&page={page_no}"
    return call_api(endpoint, "GET")

def repos_to_private():
    page_no = 1
    while True:
        json_str = get_repos(page_no)
        if not json_str:
            break
        json_data = convert_json(json_str)
        if not json_data:
            break
        handle_json_for_private(json_data)
        page_no += 1

if __name__ == "__main__":
    repos_to_private()
    if error_endpoints:
        print("Encountered errors with the following endpoints:")
        for endpoint in error_endpoints:
            print(endpoint)
