# KUBECTL='kubectl --dry-run=client'
KUBECTL='kubectl'

AWS_ACCOUNT_ID='<>'
AWS_ECR_REPOSITORY_REGION='<>'
SECRET_NAME='image-cleaner-secret-ecr'

EXISTS=$($KUBECTL get secret "$SECRET_NAME" | tail -n 1 | cut -d ' ' -f 1)
if [ "$EXISTS" = "$SECRET_NAME" ]; then
  echo "Secret exists, deleting"
  $KUBECTL delete secrets "$SECRET_NAME"
fi

PASS=$(aws ecr get-login-password --region $AWS_ECR_REPOSITORY_REGION)
$KUBECTL create secret docker-registry $SECRET_NAME \
    --docker-server=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_ECR_REPOSITORY_REGION.amazonaws.com \
    --docker-username=AWS \
    --docker-password=$PASS \
    --docker-email=foo@bar.com