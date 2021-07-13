# image-cleaner
Periodically Delete old images in docker hub (Every 2 months)

<img width="1354" alt="스크린샷 2021-07-13 오전 10 57 14" src="https://user-images.githubusercontent.com/19552819/125378147-3611cd00-e3c9-11eb-88dc-8d2818d3a297.png">

## How to create CronJob

### 1. Encoding secret infomation
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
  username: <username>
  password: <password>
```

### 3. create configmap
```
kubectl create configmap image-cleaner-src --from-file=./src/
```

### 4. create secret & cronjob
```
kubectl create -f image_cleaner.yaml
```
