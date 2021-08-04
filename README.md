# image-cleaner
Periodically Delete old images in docker hub (Every day)

![스크린샷 2021-08-04 오후 5 40 54](https://user-images.githubusercontent.com/19552819/128150603-50f4c0ff-84f8-4a79-8b72-50bb8139571a.png)


## prerequisite
Add aws credentials profile for ECR repo
```
# vim $HOME/.aws/credentials

...
[image_cleaner]
aws_access_key_id = <ECR repo user's aws_access_key_id>
aws_secret_access_key = <ECR repo user's aws_secret_access_key>
region = region
```

## How to create

### 1. Edit Configuration (conf/config.yaml)
```yaml
repositories:
  - name: ECR - exam1
    repository_type: ECR
    options:
      url: https://123123123123.dkr.ecr.ap-northeast-1.amazonaws.com
      organization: org_name
      images:
      - name: "*|image*|image-*|*image"
        policy:
          version: <= 0.1
          age: <= 10d (*1)
      credentials:
        username: username
        password: password
  - name: Docker Hub - examp2
    repository_type: DOCKER_HUB
    options:
      url: https://hub.docker.com
      organization: org_name
      images:
      - name: "*|image*|image-*|*image"
        policy:
          age: <= 60d
      credentials:
        username: username
        password: password
```
*1) d(day), h(hour), m(minute), s(second)

### 2. Create imagePullSecrets to Login into ECR repository(python scripts)

- Edit the ecr token generation script (helper/credential-ecr.sh)
```
# KUBECTL='kubectl --dry-run=client'
KUBECTL='kubectl'

AWS_ACCOUNT_ID='<AWS ACCOUNT ID>'
AWS_DEFAULT_REGION='<ECR REPOSITORY REGION>'
SECRET_NAME='image-cleaner-secret-erc'
...
```
- Run script to Create imagePullSecrets
```
sh ./helper/credential-ecr.sh
```

### 3. create configmap & secret & cronjob
- configmap
```
kubectl create configmap image-cleaner-conf --from-file=./conf/
```

- cronjob
```
kubectl create -f image_cleaner_cronjob.yaml
```

## Update API Objects
To Update object, You can use the command below.
- configmap
```
kubectl create configmap image-cleaner-conf --from-file=./conf/ -o yaml --dry-run=client | kubectl replace -f -
```
- cronjob
```
kubectl replace -f image_cleaner_cronjob.yaml
```

## If a new tag of the Docker image is uploaded to the repository
-  Edit tag of the Docker image in image_cleaner_cronjob.yaml
```
...
              valueFrom:
                secretKeyRef:
                  name: image-cleaner-secret
                  key: password
            image: image:<New tag>
            imagePullPolicy: IfNotPresent
...
```
- Recreate imagePullSecrets
```
sh ./helper/credential-ecr-sh
```
- Update cronjob object
```
kubectl replace -f image_cleaner_cronjob.yaml
```
