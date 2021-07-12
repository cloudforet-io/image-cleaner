# image-cleaner
Periodically Delete old images in docker hub (Every 2 months)

## How to create CronJob

[Docker hub: Managing access tokens](https://docs.docker.com/docker-hub/access-tokens/)

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
  personal_access_token: <personal_access_token>
```

### 3. create configmap
```
kubectl create configmap image-cleaner-src --from-file=./src/
```

### 4. create secret & cronjob
```
kubectl create -f image_cleaner.yaml
```
