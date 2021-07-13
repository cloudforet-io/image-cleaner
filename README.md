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
### 2. Edit secret data
```
apiVersion: v1
kind: Secret
metadata:
  name: image-cleaner-secret
data:
  username: <username> <- here
  password: <password> <- here
```

### 3. create configmap
```
kubectl create configmap image-cleaner-conf --from-file=./conf/
```

### 4. create secret & cronjob
```
kubectl create -f image_cleaner.yaml
```
