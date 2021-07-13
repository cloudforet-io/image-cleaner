# image-cleaner
Periodically Delete old images in docker hub (Every day)

<img width="1339" alt="스크린샷 2021-07-13 오후 5 48 41" src="https://user-images.githubusercontent.com/19552819/125421659-217dfac2-d056-42ef-bf7a-e61b76a3acd2.png">

## How to create CronJob

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

### 3. create configmap & secret & cronjob
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
