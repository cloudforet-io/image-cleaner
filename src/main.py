from connector.dockerhub_connector import DockerHubConnector
from connector.ecr_connector import EcrConnector
import yaml
import sys

def main():
    try:
        with open("./conf/config.yaml", "r") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
            repository_statements = config['repositories']
    except FileNotFoundError as e:
        print(e)
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Invalid yaml format! {e}")
        sys.exit(1)

    for repository_statement in repository_statements:
        if repository_statement['repository_type'] == "DOCKER_HUB":
            connector = DockerHubConnector(repository_statement)
        elif repository_statement['repository_type'] == "ECR":
            connector = EcrConnector(repository_statement)
        else:
            print('Invalid Repository type. (DOCKER_HUB|ECR)')
            sys.exit(1)

        images = connector.list_images()
        old_tags_by_image = {}
        for image in images:
            old_tags_by_image[image] = connector.list_old_tags(image)

        for image in old_tags_by_image:
            if old_tags_by_image[image]:
                for tag in old_tags_by_image[image]:
                    connector.delete(image,tag)
                    
if __name__ == "__main__":
    main()
