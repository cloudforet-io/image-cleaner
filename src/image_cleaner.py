from datetime import datetime, timedelta, timezone
from configparser import ConfigParser
import os
import requests
import sys
import json

config = ConfigParser()
config.read('./conf/config.ini')

BASE_URL = config['COMMON']['base_url']
DATE_TWO_MONTHS_AGO = datetime.now(tz=timezone.utc) - timedelta(days=60)

def get_login_info():
    username = os.environ.get('username')
    password = os.environ.get('password')

    if username is None or password is None:
        print('Key Error : username or password does not exist in os.env')
        sys.exit(1)

    return username,password

def create_authentication_token(username, password):
    url = f'{BASE_URL}/v2/users/login'
    payload = {
        'username': username,
        'password': password
    }

    try:
        response = requests.post(url, data=payload).json()
    except requests.exceptions.ConnectionError as e:
        print(f'Connection Error {e.response}')
    except requests.exceptions.HTTPError as e:
        print(f'HTTP Error {e.response}')
    except json.JSONDecodeError as e:
        print(f'Json Decode Error {e}')

    if response.get('token'):
        return response['token']
    else:
        raise Exception(f'response message : {response}')

def get_image_name(token, repository):
    url = f'{BASE_URL}/v2/repositories/{repository}/?page_size=100'
    headers = {
        'Authorization': 'JWT ' + token
    }

    try:
        response = requests.get(url,headers=headers).json()
    except requests.exceptions.ConnectionError as e:
        print(f'Connection Error {e.response}')
    except requests.exceptions.HTTPError as e:
        print(f'HTTP Error {e.response}')
    except json.JSONDecodeError as e:
        print(f'Json Decode Error {e}')

    if response.get('results'):
        results = response['results']
    else:
        raise Exception(f'response message : {response}')

    image_names = []
    for result in results:
        image_names.append(result['name'])

    return image_names

def get_old_tag(token, repository, image):
    #TODO: Page Sequential Search
    url = f'{BASE_URL}/v2/repositories/{repository}/{image}/tags/?page_size=200'
    headers = {
        'Authorization': 'JWT ' + token
    }

    try:
        response = requests.get(url, headers=headers).json()
    except requests.exceptions.ConnectionError as e:
        print(f'Connection Error {e.response}')
    except requests.exceptions.HTTPError as e:
        print(f'HTTP Error {e.response}')
    except json.JSONDecodeError as e:
        print(f'Json Decode Error {e}')

    if response.get('results'):
        results = response['results']
    else:
        raise Exception(f'response message : {response}')

    image_tags = []
    for result in results:
        last_updated_str = result['tag_last_pushed']
        last_updated = datetime.strptime(last_updated_str, '%Y-%m-%dT%H:%M:%S.%f%z')
        if DATE_TWO_MONTHS_AGO > last_updated:
            print(f"old tags : {image}:{result['name']}")
            image_tags.append(result['name'])

    return image_tags

def delete_image(token, repository, image, tag):
    url = f'{BASE_URL}/v2/repositories/{repository}/{image}/tags/{tag}/'
    headers = {
        'Authorization': 'JWT ' + token
    }

    try:
        response = requests.delete(url,headers=headers)
    except requests.exceptions.ConnectionError as e:
        print(f'Connection Error {e.response}')
    except requests.exceptions.HTTPError as e:
        print(f'HTTP Error {e.response}')

    if response.status_code == 204:
        print(f'[{image}:{tag}] Successfully Deleted {response.status_code}')
    else:
        print(f'[{image}:{tag}] Something Wrong {response.status_code} {response.reason}')

if __name__ == "__main__":
    username, password = get_login_info()

    authentication_token = create_authentication_token(username, password)
    image_names = get_image_name(authentication_token, username)

    old_tags_by_image = {}
    for image_name in image_names:
        old_tags_by_image[image_name] = get_old_tag(authentication_token, username, image_name)

    for image_name in old_tags_by_image:
        if old_tags_by_image[image_name]:
            for tag in old_tags_by_image[image_name]:
                delete_image(authentication_token,username,image_name,tag)
        else:
            print(f'[{image_name}] has nothing to delete.')