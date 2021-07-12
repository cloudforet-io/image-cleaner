from datetime import datetime, timedelta, timezone
import json
import os
import requests

baseurl = "https://hub.docker.com"
date_two_months_ago = datetime.now(tz=timezone.utc) - timedelta(days=60)

def create_authentication_token(username, password):
    url = f'{baseurl}/v2/users/login'
    payload = {
        'username': username,
        'password': password
    }

    response = requests.post(url, data=payload).json()

    return response['token']

def get_image_name(token, repository):
    url = f'{baseurl}/v2/repositories/{repository}/?page_size=100'
    headers = {
        'Authorization': 'JWT ' + token
    }

    response = requests.get(url,headers=headers).json()
    results = response['results']

    image_names = []
    for result in results:
        image_names.append(result['name'])

    return image_names

def get_old_tag(token, repository, image):
    url = f'{baseurl}/v2/repositories/{repository}/{image}/tags/?page_size=100'
    headers = {
        'Authorization': 'JWT ' + token
    }

    response = requests.get(url, headers=headers).json()
    results = response['results']

    image_tag_list = []
    for result in results:
        last_updated_str = result['tag_last_pushed']
        last_updated_date = datetime.strptime(last_updated_str, '%Y-%m-%dT%H:%M:%S.%f%z')
        if date_two_months_ago > last_updated_date:
            print(f"old tags : {image}:{result['name']}")
            image_tag_list.append(result['name'])

    return image_tag_list

def delete_image(token, repository, image, tag):
    url = f'{baseurl}/v2/repositories/{repository}/{image}/tags/{tag}/'
    headers = {
        'Authorization': 'JWT ' + token
    }

    response = requests.delete(url,headers=headers)

    if response.status_code == 204:
        print(f'[{image}:{tag}] Successfully Deleted {response.status_code}')
    else:
        print(f'[{image}:{tag}] Something Wrong {response.status_code} {response.reason}')

if __name__ == "__main__":
    username = os.environ['username']
    password = os.environ['password']

    authentication_token = create_authentication_token(username, password)
    image_name_list = get_image_name(authentication_token, username)

    old_tags_by_image = {}
    for image_name in image_name_list:
        old_tags_by_image[image_name] = get_old_tag(authentication_token, username, image_name)

    for image_name in old_tags_by_image:
        if old_tags_by_image[image_name]:
            for tag in old_tags_by_image[image_name]:
                delete_image(authentication_token,username,image_name,tag)
        else:
            print(f'[{image_name}] has nothing to delete.')