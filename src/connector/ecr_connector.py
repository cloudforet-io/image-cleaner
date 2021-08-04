from . import BaseConnetor
import boto3

class EcrConnector(BaseConnetor):

    def __init__(self, config):
        super().__init__(config)
        self.host = self.config['options']['url']
        self.region = self.host.split(".")[3]
        self.organization = self.config['options']['organization']
        self.login()

    def login(self):
        self.access_key_id = self.config['options']['credentials']['username']
        self.secret_access_key = self.config['options']['credentials']['password']

        try:
            sess = boto3.Session(
                aws_access_key_id=self.access_key_id,
                aws_secret_access_key=self.secret_access_key
            )
        except Exception as e:
            raise e

        self.client = sess.client('ecr', region_name=self.region)

    def list_images(self):
        try:
            response = self.client.describe_repositories()
        except Exception as e:
            raise e

        images = []
        for repository in response["repositories"]:
            organization_name = repository['repositoryName'].split("/")[0]
            image_name = repository['repositoryName'].split("/")[1]
            if organization_name == self.organization:
                images.append(image_name)

        return images

    def list_old_tags(self, image):
        try:
            response = self.client.describe_images(
                repositoryName=f'{self.organization}/{image}'
            )
        except Exception as e:
            raise e

        image_details = response.get('imageDetails')
        if not image_details:
            return []

        tags = []
        for image_detail in image_details:
            tag = {}
            tag['name'] = image_detail['imageTags'][0]
            tag['tag_last_pushed'] = image_detail['imagePushedAt']
            tags.append(tag)

        list_tags = self._filter(image,tags)
        if list_tags:
            print(f"old tags : {image}:{list_tags}")

        return list_tags

    def delete(self, image, tag):
        try:
            self.client.batch_delete_image(
                repositoryName=f'{self.organization}/{image}',
                imageIds = [
                    {
                        'imageTag' : tag
                    }
                ]
            )
        except Exception as e:
            print(f'[{image}:{tag}] Something Wrong {e}')
            raise e

        print(f'[{image}:{tag}] Successfully Deleted')
