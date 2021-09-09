from datetime import datetime, timedelta, timezone
from abc import ABC, abstractmethod
from packaging.version import Version, InvalidVersion
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

        tags_by_policy = self._get_tags_by_policy(image_policy, tags)

        return tags_by_policy

    def _get_image_policy(self, image_name, image_rules):
        for rule in image_rules:
            if self._check_image_policy(image_name, rule):
                return rule['policy']

        return None

    def _check_image_policy(self, image_name, rule):
        if rule['name'][:1] == "!":
            return not fnmatch.fnmatch(image_name, rule['name'][1:])
        else:
            return fnmatch.fnmatch(image_name, rule['name'])

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
            if tag_version == "latest":
                continue

            if self._check_version_policy(version_policy, tag_version, ops) and self._check_age_policy(age_policy, tag_last_pushed, ops):
                result.append(tag_version)

        return result

    def _check_version_policy(self, version_policy, tag_version, ops):
        if not version_policy:
            return True

        p = r'(?P<operator>^(=|>|<|>=|<=))' \
            r' (?P<number>\d+(?:\.\d+){1,2})'
        rule = re.compile(p)
        policy = rule.match(version_policy)

        if policy:
            version_policy_operator = policy['operator']
            version_policy_number = policy['number']
        else:
            raise Exception("Invalid version policy format")

        p = '\d+(?:\.\d+){1,2}'
        rule = re.compile(p)
        split_tag_version = rule.match(tag_version)

        if split_tag_version:
            tag_version = split_tag_version.group()
        else:
            return False

        tag_version = Version(tag_version)
        version_policy_number = Version(version_policy_number)

        return ops[version_policy_operator](tag_version, version_policy_number)

    def _check_age_policy(self, age_policy, tag_last_pushed, ops):
        if not age_policy:
            return True

        p = r'(?P<operator>(=|>|<|>=|<=))' \
            r' (?P<date_number>\d+)' \
            r'(?P<date_unit>(d|h|m|s)+)'
        rule = re.compile(p)
        policy = rule.match(age_policy)

        if policy:
            age_policy_operator = policy['operator']
            age_policy_date_unit = policy['date_unit']
            age_policy_date_number = int(policy['date_number'])
        else:
            raise Exception("Invalid age policy format")

        if age_policy_date_unit == 'd':  # day
            age_policy_date_number = age_policy_date_number * 1440
        elif age_policy_date_unit == 'h':  # hour
            age_policy_date_number = age_policy_date_number * 60
        elif age_policy_date_unit == 's':  # second
            age_policy_date_number = age_policy_date_number / 60

        policy_date = datetime.now(tz=timezone.utc) - timedelta(minutes=age_policy_date_number)

        return ops[age_policy_operator](tag_last_pushed, policy_date)
