from datetime import datetime, timedelta, timezone
import urllib.request, urllib.parse, urllib.error
import json
import os
import boto3

baseurl = "https://hub.docker.com"
date_two_months_ago = datetime.now(tz=timezone.utc) - timedelta(days=60)

def lambda_handler(event, context):
    username              = os.environ['username']
    personal_access_token = os.environ['personal_access_token']

    authentication_token = create_authentication_token(username, personal_access_token)
    image_name_list = get_image_name(authentication_token, username)

    old_tags_by_image = {}
    for image_name in image_name_list:
        old_tags_by_image[image_name] = get_old_tag(authentication_token, username, image_name)

    for image_name in old_tags_by_image:
        for tag in old_tags_by_image[image_name]:
            print(f'delete_image({authentication_token}, {username}, {image_name}, {tag})')


# def get_login_info_from_ssm():
#     client = boto3.client('ssm')

#     response = client.get_parameters(
#         Names=[
#             'username',
#             'personal_access_token'
#         ],
#         WithDecryption=False
#     )
    
#     for index in response['Parameters']:
#         if index['Name'] == 'username':
#             username = index['Value']

#         if index['Name'] == 'personal_access_token':
#             personal_access_token = index['Value']

#     return username, personal_access_token


def create_authentication_token(username, personal_access_token):
    url = f'{baseurl}/v2/users/login'
    payload = {
        'username': username,
        'password': personal_access_token
    }
    payload = urllib.parse.urlencode(payload).encode('utf-8')

    with urllib.request.urlopen(url, payload) as response:
        return json.loads(response.read().decode('utf-8'))['token']


def get_image_name(token, repository):
    url = f'{baseurl}/v2/repositories/{repository}/?page_size=100'

    request = urllib.request.Request(url)
    request.add_header('Authorization', 'JWT ' + token)

    with urllib.request.urlopen(request) as response:
        results = json.loads(response.read().decode('utf-8'))['results']

    image_names = []
    for result in results:
        image_names.append(result['name'])

    return image_names


def get_old_tag(token, repository, image):
    url = f'{baseurl}/v2/repositories/{repository}/{image}/tags/?page_size=100'

    request = urllib.request.Request(url)
    request.add_header('Authorization', 'JWT ' + token)

    with urllib.request.urlopen(request) as response:
        results = json.loads(response.read().decode('utf-8'))['results']

    image_tag_list = []
    for result in results:
        last_updated_str = result['last_updated']
        last_updated_date = datetime.strptime(last_updated_str, '%Y-%m-%dT%H:%M:%S.%f%z')
        if date_two_months_ago > last_updated_date:
            print(f"old tags : {image}:{result['name']}")
            image_tag_list.append(result['name'])

    return image_tag_list


def delete_image(token, repository, image, tag):
    url = f'{baseurl}/v2/repositories/{repository}/{image}/tags/{tag}/'

    request = urllib.request.Request(url, method="DELETE")
    request.add_header('Authorization', 'JWT ' + token)

    try:
        response = urllib.request.urlopen(url)
    except urllib.error.HTTPError as e:
        print(f'[{image}:{tag}] HTTP Error code : {e.code}')
    except urllib.error.URLError as e:
        print(f'[{image}:{tag}] URL Error reason : {e.reason}')
    else:
        print(f'[{image}:{tag}] {response.getcode()}')