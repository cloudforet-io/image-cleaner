from datetime import datetime, timedelta, timezone
from abc import ABC, abstractmethod
import fnmatch
import operator
import re
import sys

class BaseConnetor(ABC):

    def __init__(self, config):
        self.config = config
        self.current_time = datetime.now(tz=timezone.utc)
        self._check_credential_type()

    @abstractmethod
    def login(self):
        pass

    @abstractmethod
    def list_images(self):
        pass

    @abstractmethod
    def list_old_tags(self, image):
        pass

    @abstractmethod
    def delete(self, image, tag):
        pass

    def _check_credential_type(self):
        credentials = list(self.config['options']['credentials'].keys())
        if self.config['repository_type'] == "ECR":
            if "username" in credentials or "password" in credentials:
                print('ECR type requires access_key_id and secret_access_key')
                print(f'Curruent credential is {credentials}')
                sys.exit(1)

        if self.config['repository_type'] == "DOCKER_HUB":
            if "access_key_id" in credentials or "secret_access_key" in credentials:
                print('DOCKER_HUB type requires username and password')
                print(f'Curruent credential is {credentials}')
                sys.exit(1)

    def _filter(self, image_name, tags):
        image_rules = self.config['options']['images']

        image_policy = self._get_image_policy(image_name, image_rules)
        if image_policy is None:
            return []

        tags_by_policy = self._get_tags_by_policy(image_policy,tags)

        return tags_by_policy

    def _get_image_policy(self, image_name, image_rules):
        for rule in image_rules:
            if is_negative_match := re.match('^!',rule['name']):
                negative_match_pattern = is_negative_match.string[1:]
                if negative_match_pattern not in image_name:
                    return rule['policy']
            else:
                if fnmatch.fnmatch(image_name,rule['name']):
                    return rule['policy']

        return None

    def _get_tags_by_policy(self, image_policy, tags):
        age_policy = image_policy.get('age')
        version_policy = image_policy.get('version')
        ops = {
            "=": operator.eq,
            ">": operator.gt,
            "<": operator.lt,
            ">=": operator.ge,
            "<=": operator.le,
        }

        result = []
        for tag in tags:
            tag_version = tag.get('name')
            tag_last_pushed = tag.get('tag_last_pushed')
            flags = []
            if tag_version == "latest":
                continue

            if version_policy:
                if not re.fullmatch('^(=|>|<)=?\s[\d.]+',version_policy):
                    raise Exception("Invalid version policy format")

                version_policy_operator = version_policy.split(" ")[0]
                version_policy_number = version_policy.split(" ")[1]
                if not ops.get(version_policy_operator):
                    raise Exception("Unsupported operator")

                version_filtering_flag = ops[version_policy_operator](tag_version, version_policy_number)
                flags.append(version_filtering_flag)

            if age_policy:
                if not re.fullmatch('^(=|>|<)=?\s\d+(d|h|m|s)',age_policy):
                    raise Exception("Invalid age policy format")

                age_policy_operator = age_policy.split(" ")[0]
                age_policy_date = age_policy.split(" ")[1]
                age_policy_date_variable = age_policy_date[-1]
                age_policy_date_coefficient = int(age_policy_date[:-1])

                if age_policy_date_variable == 'd':     # day
                    coefficient = age_policy_date_coefficient * 1440
                elif  age_policy_date_variable == 'h':  # hour
                    coefficient = age_policy_date_coefficient * 60
                elif age_policy_date_variable == 's':   # second
                    coefficient = age_policy_date_coefficient / 60
                else:
                    raise Exception("Unsupported date format")

                policy_date = datetime.now(tz=timezone.utc) - timedelta(minutes=coefficient)
                if isinstance(tag_last_pushed, str):
                    tag_last_pushed = datetime.strptime(tag_last_pushed, '%Y-%m-%dT%H:%M:%S.%f%z')
                age_filtering_flag = ops[age_policy_operator](tag_last_pushed,policy_date)
                flags.append(age_filtering_flag)

            if False not in flags:
                result.append(tag_version)

        return result

