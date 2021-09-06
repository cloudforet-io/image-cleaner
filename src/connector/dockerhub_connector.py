from . import BaseConnetor
from datetime import datetime
import requests
import json
import math

class DockerHubConnector(BaseConnetor):

    def __init__(self, config):
        super().__init__(config)
        self.base_url = self.config['options']['url']
        self.organization = self.config['options']['organization']
        self.login()

    def _http_requests(self, url, *, method, payload=None, headers=None):
         if method == 'post' and payload is None:
              raise Exception('post method requires a payload')

         if method in ['get', 'delete'] and headers is None:
              raise Exception(f'{method} method requires a headers')

         try:
              if method == "post":
                   response = requests.post(url, data=payload).json()
              elif method == "get":
                   response = requests.get(url, headers=headers).json()
              elif method == "delete":
                   response = requests.delete(url, headers=headers)
         except requests.exceptions.ConnectionError as e:
              raise Exception(f'Connection Error {e.response}')
         except requests.exceptions.HTTPError as e:
              raise Exception(f'HTTP Error {e.response}')
         except json.JSONDecodeError as e:
              raise Exception(f'Json Decode Error {e}')

         return response

    def login(self):
        self.username = self.config['options']['credentials']['username']
        self.password = self.config['options']['credentials']['password']

        url = f'{self.base_url}/v2/users/login'
        payload = {
            'username': self.username,
            'password': self.password
        }
        response = self._http_requests(url, method='post', payload=payload)

        if response.get('token'):
            self.token = response['token']
        else:
            raise Exception(f'Response does not have a key "token" : {response}')

    def list_images(self):
        url = f'{self.base_url}/v2/repositories/{self.organization}/?page_size=100'
        headers = {
            'Authorization': 'JWT ' + self.token
        }
        response = self._http_requests(url, method='get', headers=headers)

        if response.get('results'):
            results = response['results']
        else:
            raise Exception(f'Response does not have a key "results" : {response}')

        images = []
        for result in results:
            images.append(result['name'])

        return images

    def _get_image_tags(self, image, page=1, page_size=100):
        url = f'{self.base_url}/v2/repositories/{self.organization}/{image}/tags/?page_size={page_size}&page={page}'
        headers = {
            'Authorization': 'JWT ' + self.token
        }
        response = self._http_requests(url, method='get', headers=headers)

        tags = []
        if response.get('results'):
            for result in response['results']:
                tag = {}
                tag['name'] = result['name']
                tag['tag_last_pushed'] = datetime.strptime(result['tag_last_pushed'], '%Y-%m-%dT%H:%M:%S.%f%z')
                tags.append(tag)
        
        return tags

    def list_old_tags(self, image):
        url = f'{self.base_url}/v2/repositories/{self.organization}/{image}/tags/?page_size=1'
        headers = {
            'Authorization': 'JWT ' + self.token
        }
        response = self._http_requests(url, method='get', headers=headers)
        tag_count = response.get('count')
        if tag_count < 1:
            return []

        pages = math.ceil(tag_count / 100)
        tags = []
        for page in range(1, pages + 1):
            tags += self._get_image_tags(image,page)

        if not tags:
            return []

        old_tags = self._filter(image, tags)
        if old_tags:
            print(f"old tags : {image}:{old_tags}")

        return old_tags

    def delete(self, image, tag):
        url = f'{self.base_url}/v2/repositories/{self.organization}/{image}/tags/{tag}/'
        headers = {
            'Authorization': 'JWT ' + self.token
        }
        response = self._http_requests(url, method='delete', headers=headers)

        if response.status_code == 204:
            print(f'[{image}:{tag}] Successfully Deleted {response.status_code}')
        else:
            print(f'[{image}:{tag}] Something Wrong {response.status_code} {response.reason}')
