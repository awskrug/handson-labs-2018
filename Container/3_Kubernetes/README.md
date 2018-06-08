# Kubernetes Hands-on

* See: https://github.com/nalbam/docs/blob/master/201806/Kubernetes/README.md

---

## Index

<!-- TOC depthFrom:2 depthTo:6 withLinks:1 updateOnSave:1 orderedList:0 -->

* [Topic](#topic)
* [Prerequisites](#prerequisites)
* [Kubernetes Cluster](#kubernetes-cluster)
* [Addons](#addons)
* [Pipeline](#pipeline)

<!-- /TOC -->

---

## Topic

* Kubernetes
* Kops
* Jenkins X
* Helm

---

### Basic Knowledge

* Kubernetes 를 들어봤다.
* AWS 에 인스턴스를 만들어 봤다.
* SSH 로 접속을 할수 있다.
* 필요 계정 : AWS, Github

---

### Kubernetes
- 컨테이너 작업을 자동화하는 오픈소스 플랫폼
- Container Orchestration
- Cluster 는 Master 와 Node 로 구성 

<img src="images/kubernetes.png" height="300">

---

### Kops
- Kubernetes cluster up and running
- AWS is officially supported
- GCE is beta supported
- 1 Master, 2 Nodes

<img src="images/kops.png" height="300">

---

### Jenkins X
- Jenkins Pipeline Tool
- Jenkins + Kubernetes Plugins + CLI
- Jenkins 를 제외한 UI 는 제공되지 않음

<img src="images/jenkins-x.png" height="300">

---

### Helm
- Kubernetes Package Manager
- Used in Jenkins X

Note:
- Jenkins X 에서 빌드된 이미지의 버전 관리를 위하여 사용 됩니다.
- 우리가 직접 하용하지는 않지만 우선 설치 해 줍니다.

---

## Prerequisites

* AWS IAM - Access keys
* AWS EC2 - Key Pairs
* AWS EC2 - Ubuntu Instance

---

### AWS IAM - Access keys
* https://console.aws.amazon.com/iam/home?region=ap-northeast-2#/home

Note:
- CLI 를 이용하여 AWS 객체들을 사용하기 위하여 발급 받습니다.
- 발급 받은 키는 유출되지 않도록 잘 관리 해야 합니다.

---

### AWS EC2 - Key Pairs
```bash
# create key-pair
ssh-keygen -q -f ~/.ssh/hands-on -C 'hands-on' -N ''

# import key-pair
aws ec2 import-key-pair \
    --key-name 'hands-on' \
    --public-key-material file://~/.ssh/hands-on.pub
```
* https://ap-northeast-2.console.aws.amazon.com/ec2/v2/home?region=ap-northeast-2#KeyPairs

Note:
- 생성된 Instance 에 접속하기 위하여 필요 합니다.
- 쉘이 가능하신 분은 위의 명령어로 만들수 있습니다.

---

### AWS EC2 - Ubuntu Instance
```bash
aws ec2 create-security-group --group-name 'ssh' --description 'hands-on'

aws ec2 authorize-security-group-ingress --group-name 'ssh' --protocol tcp --port 22 --cidr 0.0.0.0/0

# create Ubuntu Server 16.04 LTS
aws ec2 run-instances \
    --image-id 'ami-f030989e' \
    --instance-type 't2.micro' \
    --key-name 'hands-on' \
    --security-groups 'ssh' 'default'
```
* https://ap-northeast-2.console.aws.amazon.com/ec2/v2/home?region=ap-northeast-2#Instances

Note:
- 모두가 같은 환경에서 진행 할수 있도록 우분투 인스턴스를 생성 합니다.
- 쉘이 가능하신 분은 위의 명령어로 만들수 있습니다.

---

### OSX (5m)
```bash
brew tap jenkins-x/jx
brew install awscli kubectl kops jx jq
```
* https://brew.sh/index_ko

Note:
- 맥 이라면 홈브루를 이용하여 쉽게 설치/실행 할수 있으나, 우리는 우분투에서 진행 하기로 합니다.

---

### Ubuntu (5m)
```bash
# connect
export BASTION=$(aws ec2 describe-instances | jq '.Reservations[].Instances[] | select(.KeyName == "hands-on")' | grep PublicIpAddress | cut -d'"' -f4)
ssh -i ~/.ssh/hands-on ubuntu@${BASTION}

# kubectl (1m)
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
cat <<EOF > kubernetes.list
deb http://apt.kubernetes.io/ kubernetes-xenial main
EOF
sudo mv kubernetes.list /etc/apt/sources.list.d/kubernetes.list
sudo apt update && sudo apt install -y kubectl

# kops (2m)
export VERSION=$(curl -s https://api.github.com/repos/kubernetes/kops/releases/latest | grep tag_name | cut -d'"' -f4)
curl -LO https://github.com/kubernetes/kops/releases/download/${VERSION}/kops-linux-amd64
chmod +x kops-linux-amd64 && sudo mv kops-linux-amd64 /usr/local/bin/kops

# helm (1m)
export VERSION=$(curl -s https://api.github.com/repos/kubernetes/helm/releases/latest | grep tag_name | cut -d'"' -f4)
curl -L https://storage.googleapis.com/kubernetes-helm/helm-${VERSION}-linux-amd64.tar.gz | tar xzv
sudo mv linux-amd64/helm /usr/local/bin/helm

# jenkins-x (1m)
export VERSION=$(curl -s https://api.github.com/repos/jenkins-x/jx/releases/latest | grep tag_name | cut -d'"' -f4)
curl -L https://github.com/jenkins-x/jx/releases/download/${VERSION}/jx-linux-amd64.tar.gz | tar xzv 
sudo mv jx /usr/local/bin/jx

# awscli (1m)
sudo apt install -y awscli jq
```

Note:
- 생성한 우분투에 접속 합니다.
- kubectl, kops, helm, jenkins-x, awscli 를 설치 합니다.
- 추가적으로 jq 를 설치 합니다. json 을 쉽게 파싱 할수 있도록 도와 줍니다.

---

### Access Keys
```bash
# ssh key
ssh-keygen -q -f ~/.ssh/id_rsa -N ''

# aws region
aws configure set default.region ap-northeast-2

# aws credentials
cat <<EOF > ~/.aws/credentials
[default]
aws_access_key_id=
aws_secret_access_key=
EOF

# aws ec2 list
aws ec2 describe-instances | jq '.Reservations[].Instances[] | select(.State.Name == "running") | {Id: .InstanceId, Ip: .PublicIpAddress, Type: .InstanceType}'

# aws elb list
aws elb describe-load-balancers | jq '.LoadBalancerDescriptions[] | {DNSName: .DNSName, Count: .Instances | length}'
```

Note:
- ssh 키를 생성합니다. 클러스터 내에서 서로 접속 하기 위하여 필요 합니다.
- aws cli 를 사용하여 리전을 서울로 설정 합니다.
- 그리고 위에서 발급된 access key 를 넣어줍니다.
- 아래 두개의 쉘은 인스턴스 목록과 ELB 목록을 조회 하여 필요한 정보만 보여줍니다.

---

## Kubernetes Cluster
```bash
export KOPS_CLUSTER_NAME=hands-on.k8s.local
export KOPS_STATE_STORE=s3://terraform-awskrug-nalbam-seoul

# aws s3 bucket for state store
aws s3 mb ${KOPS_STATE_STORE} --region ap-northeast-2

# create cluster
kops create cluster \
    --cloud=aws \
    --name=${KOPS_CLUSTER_NAME} \
    --state=${KOPS_STATE_STORE} \
    --master-size=m4.large \
    --node-size=m4.xlarge \
    --node-count=2 \
    --zones=ap-northeast-2a,ap-northeast-2c \
    --network-cidr=10.10.0.0/16 \
    --networking=calico
```

Note:
- 클러스터 이름을 세팅하고, 클러스터 상태를 저장할 S3 Bucket 을 만들어 줍니다.
- 마스터 1대, 노드 2대로 구성된 클러스터를 생성합니다.
- 위 명령을 실행하면 실제 클러스터는 만들어지지 않습니다.

---

## Kubernetes Cluster
```bash
kops get cluster --name=${KOPS_CLUSTER_NAME}

kops edit cluster --name=${KOPS_CLUSTER_NAME}
```

Note:
- 클러스터 정보를 조회 합니다.
- 나중에 사용할 Jenkins X 를 위하여 설정을 수정 합니다.

---

### Modify for Jenkins-x
```yaml
spec:
  docker:
    insecureRegistry: 100.64.0.0/10
    logDriver: ""
```

Note:
- Jenkins X 에서 사용할 내부 Docker Registry 를 허용하도록 보안설정을 입력합니다.

---

## Create Cluster
```bash
kops update cluster --name=${KOPS_CLUSTER_NAME} --yes

kops validate cluster --name=${KOPS_CLUSTER_NAME}

kops delete cluster --name=${KOPS_CLUSTER_NAME} --yes
```

Note:
- update 명력에 --yes 를 하면 실제 클러스터가 생성 됩니다.
- validate 로 생성이 완료 되었는지 확인 할수 있습니다.
- 클러스터 생성까지 대략 10여분이 소요 됩니다.

---

### kubectl
```bash
# kubectl config
kubectl config view

# kubectl get
kubectl get deploy,pod,svc,job --all-namespaces
kubectl get deploy,pod,svc,job -n kube-system
kubectl get deploy,pod,svc,job -n default
```

Note:
- 클러스터 정보와 만들어진 객체들을 조회 할수 있습니다.
- -w 옵션으로 2초마다 리로드 하도록 할수 있습니다.

---

### sample
```bash
# get source
git clone https://github.com/awskrug/handson-labs-2018

# install
kubectl apply -f handson-labs-2018/3_Kubernetes/sample-web.yml

# delete
kubectl delete -f handson-labs-2018/3_Kubernetes/sample-web.yml
```
* https://ap-northeast-2.console.aws.amazon.com/ec2/v2/home?region=ap-northeast-2#LoadBalancers

Note:
- 샘플 깃을 클론하고, 샘플 웹을 하나 생성해 봅니다.
- Pod 와 Service 가 만들어졌고, AWS 에서 만들었으므로 ELB 도 생겼습니다.

---

## Addons

* Dashboard
* Heapster

---

### Dashboard
Kubernetes Dashboard is a general purpose, web-based UI for Kubernetes clusters.
```bash
# install
kubectl apply -f handson-labs-2018/3_Kubernetes/dashboard.yml

# get dashboard token
kubectl describe secret -n kube-system $(kubectl get secret -n kube-system | grep kubernetes-dashboard-token | awk '{print $1}')

# create role binding for kube-system:kubernetes-dashboard
kubectl create clusterrolebinding cluster-admin:kube-system:kubernetes-dashboard --clusterrole=cluster-admin --serviceaccount=kube-system:kubernetes-dashboard
kubectl get clusterrolebindings | grep cluster-admin

# delete
kubectl delete -f handson-labs-2018/3_Kubernetes/dashboard.yml
```
* https://github.com/kubernetes/dashboard/

Note:
- 대시보드를 생성합니다. 생성된 ELB 로 접속 할수 있습니다.
- 로그인을 위해 Secret 에서 토큰을 조회 해서 붙여 넣습니다.
- 접속해보면 권한 때문에 정상적으로 보이지 않을 겁니다. 권한 부여를 합니다.

---

### Heapster
Heapster enables Container Cluster Monitoring and Performance Analysis for Kubernetes - DEPRECATED
```bash
# install
kubectl apply -f handson-labs-2018/3_Kubernetes/heapster.yml

# monitoring
kubectl top pod --all-namespaces
kubectl top pod -n kube-system

# delete
kubectl delete -f handson-labs-2018/3_Kubernetes/heapster.yml
```
* https://github.com/kubernetes/heapster/

Note:
- 대시보드 로는 충분한 정보를 볼수 잆습니다. 예를 들면 CPU, Memory 사용량 같은것들...
- 힙스터를 설치하고 잠시 기다리면 정보가 수집되고, 대시보드에 보여집니다.
- 참고로 힙스터는 현재 DEPRECATED 되었습니다.

---

## Pipeline

* Jenkins X

---

### Jenkins X
```bash
jx install --provider=aws

jx console

jx import
jx create spring -d web -d actuator

jx get applications
jx get pipelines

jx get activity -f jx-demo -w
jx get build logs nalbam/jx-demo/master
jx get build logs nalbam/jx-demo/dev

jx promote jx-demo --env production
```
* https://jenkins-x.io/

---

## Thank You
