# ECS CLI와 AWS CLI를 이용하여 백앤드 배포하기


### 개발환경에 접속하기
```bash
ssh -i petclinic.pem petclinic-dev-ip
cd /home/ec2-user/workspace/petclinic-rest
```


### 환경 변수 설정
```bash
export AWS_ACCESS_KEY_ID=`aws configure get aws_access_key_id`
export AWS_SECRET_ACCESS_KEY=`aws configure get aws_secret_access_key`
export CLUSTER_NAME=petclinic-rest

export VPC_ID=`aws ec2 describe-vpcs | jq -r '.Vpcs[0].VpcId'`
export SUBNET_ID_1=`aws ec2 describe-subnets | jq -r '.Subnets[0].SubnetId'`
export SUBNET_ID_2=`aws ec2 describe-subnets | jq -r '.Subnets[1].SubnetId'`

echo "VPC_ID : ${VPC_ID}"
echo "SUBNET_ID_1 : ${SUBNET_ID_1}"
echo "SUBNET_ID_2 : ${SUBNET_ID_2}"
```

## ECS 인프라 만들고 배포하기


### ECR 만들고 이미지 푸시하기
```bash
./1_create_and_push_ecr.sh
```

```bash
#!/usr/bin/env bash

IMAGE_NAME="petclinic-rest"

if aws ecr create-repository --repository-name ${IMAGE_NAME}; then
    echo "[INFO] REPOSITORY IS CREATED."
else
    echo "[INFO] REPOSITORY ALREADY EXISTS."
fi

ACCOUNT_ID=`aws sts get-caller-identity | jq -r ".Account"`

export DOCKER_REGISTRY_HOST="${ACCOUNT_ID}.dkr.ecr.ap-northeast-2.amazonaws.com"
echo "[INFO] DOCKER_REGISTRY_HOST : ${DOCKER_REGISTRY_HOST}"

if ./mvnw clean package docker:build -Dmaven.test.skip=true; then
    DOCKER_LOGIN=`aws ecr get-login --no-include-email`
    ${DOCKER_LOGIN}
    docker push ${DOCKER_REGISTRY_HOST}/${IMAGE_NAME}:latest
else
    echo "[ERROR] MAVEN BUILD FAIL"
fi
```


### Application Load Balancer 보안그룹  & ECS Instance 보안그룹 생성
```bash
./2_create_security_groups.sh
```

```bash
#!/usr/bin/env bash

# create alb security group
ALB_SG_NAME=petclinic-alb-sg
aws ec2 create-security-group --group-name ${ALB_SG_NAME} \
  --description "${ALB_SG_NAME}" --vpc-id ${VPC_ID}
aws ec2 authorize-security-group-ingress --group-name ${ALB_SG_NAME} \
  --protocol tcp --port 80 --cidr 0.0.0.0/0


# create ecs instance security group
ECS_SG_NAME=petclinic-ecs-sg
ALB_SG_ID=`aws ec2 describe-security-groups --group-names ${ALB_SG_NAME}| jq -r '.SecurityGroups[0].GroupId'`

aws ec2 create-security-group --group-name ${ECS_SG_NAME} \
  --description "petclinic-ecs-sg" --vpc-id ${VPC_ID}
aws ec2 authorize-security-group-ingress --group-name ${ECS_SG_NAME} \
  --protocol tcp --port 32768-65535 --source-group ${ALB_SG_ID}
aws ec2 authorize-security-group-ingress --group-name ${ECS_SG_NAME} \
  --protocol tcp --port 22 --cidr 0.0.0.0/0

ECS_SG_ID=`aws ec2 describe-security-groups --group-names ${ECS_SG_NAME}| jq -r '.SecurityGroups[0].GroupId'`


echo "ALB SECURITY GROUP : ${ALB_SG_NAME} ${ALB_SG_ID}"
echo "ECS SECURITY GROUP : ${ECS_SG_NAME} ${ECS_SG_ID}"
```

### Application Load Balancer 생성
```bash
./3_create_alb.sh
```

```bash
#!/usr/bin/env bash

ALB_SG_NAME=petclinic-alb-sg
ALB_SG_ID=`aws ec2 describe-security-groups --group-names ${ALB_SG_NAME}| jq -r '.SecurityGroups[0].GroupId'`

echo "ALB SECURITY GROUP : ${ALB_SG_NAME} ${ALB_SG_ID}"



aws elbv2 create-load-balancer --name petclinic-alb \
  --subnets ${SUBNET_ID_1} ${SUBNET_ID_2} --security-groups ${ALB_SG_ID}

aws elbv2 create-target-group --name petclinic-targets --protocol HTTP --port 80 --vpc-id ${VPC_ID} \
  --health-check-protocol HTTP \
  --health-check-path /actuator/health \
  --target-type instance

ALB_ARN=`aws elbv2 describe-load-balancers --names petclinic-alb | jq -r '.LoadBalancers[0].LoadBalancerArn'`
TARGET_ARN=`aws elbv2 describe-target-groups --names petclinic-targets | jq -r '.TargetGroups[0].TargetGroupArn'`

aws elbv2 create-listener --load-balancer-arn ${ALB_ARN} \
  --protocol HTTP --port 80 --default-actions Type=forward,TargetGroupArn=${TARGET_ARN}
```

### 작업 정의
```yaml
version: '2'
services:
  petclinic-rest:
    image: 957582603404.dkr.ecr.ap-northeast-2.amazonaws.com/petclinic-rest:latest
    mem_limit: 1024m
    mem_reservation: 512m
    ports:
      - "0:9460"
    logging:
      driver: awslogs
      options:
        awslogs-group: petclinic-rest
        awslogs-region: ap-northeast-2
        awslogs-stream-prefix: petclinic
```

### 클러스터 생성
```bash
./4_create_cluster.sh
```

```bash
# configure
ecs-cli configure --cluster ${CLUSTER_NAME} \
  --region ap-northeast-2 \
  --default-launch-type EC2 \
  --config-name ${CLUSTER_NAME}

ecs-cli configure profile \
  --access-key ${AWS_ACCESS_KEY_ID} \
  --secret-key ${AWS_SECRET_ACCESS_KEY} \
  --profile-name  ${CLUSTER_NAME}


ECS_SG_NAME=petclinic-ecs-sg
ECS_SG_ID=`aws ec2 describe-security-groups --group-names ${ECS_SG_NAME}| jq -r '.SecurityGroups[0].GroupId'`

echo "ECS SECURITY GROUP : ${ECS_SG_NAME} ${ECS_SG_ID}"

# generate cluster
ecs-cli up --keypair voyager.woo \
  --security-group ${ECS_SG_ID} \
  --cluster ${CLUSTER_NAME} \
  --vpc ${VPC_ID} \
  --subnets ${SUBNET_ID_1},${SUBNET_ID_2} \
  --capability-iam --size 2 \
  --instance-type t2.micro

```
### 서비스 생성 및 배포

```bash
./5_create_and_run_service.sh
```


```bash
TARGET_ARN=`aws elbv2 describe-target-groups --names petclinic-targets | jq -r '.TargetGroups[0].TargetGroupArn'`

# 서비스 생성
ecs-cli compose --file ecs_task.yml \
  --project-name ${CLUSTER_NAME} \
    service \
  create --cluster ${CLUSTER_NAME} \
  --deployment-max-percent 100 \
  --deployment-min-healthy-percent 50 \
  --target-group-arn ${TARGET_ARN} \
  --health-check-grace-period 60 \
  --container-name ${CLUSTER_NAME} \
  --container-port 9460 \
  --create-log-groups

ecs-cli compose --file ecs_task.yml \
  --project-name ${CLUSTER_NAME} service up \
  --cluster ${CLUSTER_NAME}

ecs-cli compose --file ecs_task.yml \
  --project-name ${CLUSTER_NAME} service scale 2 \
  --cluster ${CLUSTER_NAME}

```

### 서비스 업데이트

```bash
./6_update_servcie.sh
```

```bash
bash ./1_push_to_ecr.sh


export AWS_ACCESS_KEY_ID=`aws configure get aws_access_key_id`
export AWS_SECRET_ACCESS_KEY=`aws configure get aws_secret_access_key`
export CLUSTER_NAME=petclinic-rest

ecs-cli compose --file ecs_task.yml \
  --project-name ${CLUSTER_NAME} service up \
  --cluster ${CLUSTER_NAME} --force-deployment
```

### Frontend 연결
