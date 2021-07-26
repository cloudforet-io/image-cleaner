# image-cleaner
Periodically Delete old images in docker hub (Every day)

<img width="1337" alt="스크린샷 2021-07-14 오후 9 24 10" src="https://user-images.githubusercontent.com/19552819/125621539-382e58aa-0c16-4c4a-9e49-01a79b651c48.png">

## How to create

### 1. Encoding secret infomation
- username : docker hub username
- password : docker hub password
```
echo -n <username> | base64 
echo -n <password> | base64
```
### 2. Edit image_cleaner_secret.yaml
```
apiVersion: v1
kind: Secret
metadata:
  name: image-cleaner-secret
data:
  username: <username> <- here
  password: <password> <- here
```

### 3. Create imagePullSecrets for Login into ECR 

- Edit the ecr token generation script (./helper/credential-ecr.sh)
```
# KUBECTL='kubectl --dry-run=client'
KUBECTL='kubectl'

AWS_ACCOUNT_ID='<YOUR AWS ACCOUNT ID>'
AWS_DEFAULT_REGION='<ECR REPOSITORY REGION>'
SECRET_NAME='image-cleaner-secret-erc'
...
```
- Run script to Create imagePullSecrets
```
sh ./helper/credential-ecr.sh
```

### 4. create configmap & secret & cronjob
- configmap
```
kubectl create configmap image-cleaner-conf --from-file=./conf/
```
- secret
```
kubectl create -f image_cleaner_secret.yaml
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
- secret
```
kubectl replace -f image_cleaner_secret.yaml
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
