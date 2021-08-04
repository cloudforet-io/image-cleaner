from . import BaseConnetor
import requests
import json


class DockerHubConnector(BaseConnetor):

    def __init__(self, config):
        super().__init__(config)
        self.base_url = self.config['options']['url']
        self.organization = self.config['options']['organization']
        self.login()

    def login(self):
        self.username = self.config['options']['credentials']['username']
        self.password = self.config['options']['credentials']['password']

        url = f'{self.base_url}/v2/users/login'
        payload = {
            'username': self.username,
            'password': self.password
        }

        try:
            response = requests.post(url, data=payload).json()
        except requests.exceptions.ConnectionError as e:
            raise Exception(f'Connection Error {e.response}')
        except requests.exceptions.HTTPError as e:
            raise Exception(f'HTTP Error {e.response}')
        except json.JSONDecodeError as e:
            raise Exception(f'Json Decode Error {e}')

        if response.get('token'):
            self.token = response['token']
        else:
            raise Exception(f'Response does not have a key "token" : {response}')

    def list_images(self):
        url = f'{self.base_url}/v2/repositories/{self.organization}/?page_size=100'
        headers = {
            'Authorization': 'JWT ' + self.token
        }

        try:
            response = requests.get(url, headers=headers).json()
        except requests.exceptions.ConnectionError as e:
            raise Exception(f'Connection Error {e.response}')
        except requests.exceptions.HTTPError as e:
            raise Exception(f'HTTP Error {e.response}')
        except json.JSONDecodeError as e:
            raise Exception(f'Json Decode Error {e}')

        if response.get('results'):
            results = response['results']
        else:
            raise Exception(f'Response does not have a key "results" : {response}')

        images = []
        for result in results:
            images.append(result['name'])

        return images

    def list_old_tags(self, image):
        url = f'{self.base_url}/v2/repositories/{self.organization}/{image}/tags/?page_size=200'
        headers = {
            'Authorization': 'JWT ' + self.token
        }

        try:
            response = requests.get(url, headers=headers).json()
        except requests.exceptions.ConnectionError as e:
            raise Exception(f'Connection Error {e.response}')
        except requests.exceptions.HTTPError as e:
            raise Exception(f'HTTP Error {e.response}')
        except json.JSONDecodeError as e:
            raise Exception(f'Json Decode Error {e}')

        if response.get('results'):
            results = response['results']
        else:
            return []

        tags = self._filter(image,results)
        if tags:
            print(f"old tags : {image}:{tags}")

        return tags

    def delete(self, image, tag):
        url = f'{self.base_url}/v2/repositories/{self.organization}/{image}/tags/{tag}/'
        headers = {
            'Authorization': 'JWT ' + self.token
        }

        try:
            response = requests.delete(url, headers=headers)
        except requests.exceptions.ConnectionError as e:
            raise Exception(f'Connection Error {e.response}')
        except requests.exceptions.HTTPError as e:
            raise Exception(f'HTTP Error {e.response}')

        if response.status_code == 204:
            print(f'[{image}:{tag}] Successfully Deleted {response.status_code}')
        else:
            print(f'[{image}:{tag}] Something Wrong {response.status_code} {response.reason}')




