# Kubernetes Hands-on

<!-- TOC depthFrom:2 depthTo:6 withLinks:1 updateOnSave:1 orderedList:0 -->

**Index**

* [Info](#info)
* [Prerequisites](#prerequisites)
* [Kubernetes Cluster](#kubernetes-cluster)
* [Addons](#addons)
* [Pipeline](#pipeline)

<!-- /TOC -->

## Info

### Kubernetes
- 컨테이너 작업을 자동화하는 오픈소스 플랫폼 (컨테이너 오케스트레이션)
- Cluster 는 Master 와 Nodes 로 구성 

<img src="https://kubernetesbootcamp.github.io/kubernetes-bootcamp/public/images/module_01_cluster.svg" width="500">

### Kops
- Kubernetes Cluster 를 쉽게 설치/운영 할수 있도록 도와주는 툴
- AWS, GCE, DigitalOcean 을 지원
- 기본 설정으로 AWS 에서 1 Master, 2 Nodes 로 구성

<img src="https://images.contentstack.io/v3/assets/blt300387d93dabf50e/bltec54ae56e6302d11/5a21ccde473ff3867b91653f/download" width="500">

### Helm
- Kubernetes 패키지 매니저
- 핸즈온에서 직접적으로 사용 하지는 않지만, Jenkins X 에서 패키지를 배포 하기 위하여 사용

### Jenkins X
- Kubernetes 에서 Application 을 쉽게 빌드/배포 할수 있도록 도와주는 툴
- Jenkins 에 Kubernetes 관련 플러그인을 설치하여 사용
- Jenkins 를 제외한 UI 는 제공되지 않음
- cli 를 통하여 실행 

<img src="https://jenkins-x.io/images/overview.png" width="500">

## Prerequisites

### Amazon AccessKey
* https://console.aws.amazon.com/iam/home?region=ap-northeast-2#/home

### Amazon KeyPairs
* https://ap-northeast-2.console.aws.amazon.com/ec2/v2/home?region=ap-northeast-2#KeyPairs:sort=keyName

### OSX (5m)
```bash
brew tap jenkins-x/jx
brew install awscli kubectl kops jx jq
```
* https://brew.sh/index_ko

### Ubuntu (5m)
```bash
# connect
BASTION=
ssh -i ~/.ssh/hands-on.pem ubuntu@${BASTION}

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
* https://ap-northeast-2.console.aws.amazon.com/ec2/v2/home?region=ap-northeast-2#Instances:search=running;sort=tag:Name

### Amazon AccessKeys
```bash
# ssh key
pushd ~/.ssh
ssh-keygen -f id_rsa -N ''
popd

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

## Kubernetes Cluster
```bash
export KOPS_STATE_STORE=s3://kops-state-store-nalbam-seoul
export KOPS_CLUSTER_NAME=awskrug-handson.k8s.local

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

kops get cluster --name=${KOPS_CLUSTER_NAME}

kops edit cluster --name=${KOPS_CLUSTER_NAME}

kops update cluster --name=${KOPS_CLUSTER_NAME} --yes

kops validate cluster --name=${KOPS_CLUSTER_NAME}

kops delete cluster --name=${KOPS_CLUSTER_NAME} --yes
```

### Modify for Jenkins-x
```yaml
spec:
  docker:
    insecureRegistry: 100.64.0.0/10
    logDriver: ""
```

### kubectl
```bash
# kubectl config
kubectl config view

# kubectl get
kubectl get deploy,pod,svc,job --all-namespaces
kubectl get deploy,pod,svc,job -n kube-system
kubectl get deploy,pod,svc,job -n default
```

### sample
```bash
git clone https://github.com/awskrug/handson-labs-2018

kubectl apply -f handson-labs-2018/3_Kubernetes/sample-node.yml
kubectl apply -f handson-labs-2018/3_Kubernetes/sample-spring.yml
kubectl apply -f handson-labs-2018/3_Kubernetes/sample-web.yml

kubectl delete -f handson-labs-2018/3_Kubernetes/sample-node.yml
kubectl delete -f handson-labs-2018/3_Kubernetes/sample-spring.yml
kubectl delete -f handson-labs-2018/3_Kubernetes/sample-web.yml
```
* https://ap-northeast-2.console.aws.amazon.com/ec2/v2/home?region=ap-northeast-2#LoadBalancers:sort=loadBalancerName

## Addons

### Dashboard
Kubernetes Dashboard is a general purpose, web-based UI for Kubernetes clusters.
```bash
kubectl apply -f handson-labs-2018/3_Kubernetes/dashboard.yml

# create role binding for kube-system:kubernetes-dashboard
kubectl create clusterrolebinding cluster-admin:kube-system:kubernetes-dashboard --clusterrole=cluster-admin --serviceaccount=kube-system:kubernetes-dashboard
kubectl get clusterrolebindings | grep cluster-admin

# get dashboard token
kubectl describe secret -n kube-system $(kubectl get secret -n kube-system | grep kubernetes-dashboard-token | awk '{print $1}')

kubectl delete -f handson-labs-2018/3_Kubernetes/dashboard.yml
```
* https://github.com/kubernetes/dashboard/
* https://github.com/kubernetes/kops/blob/master/docs/addons.md
* https://github.com/kubernetes/kops/tree/master/addons/kubernetes-dashboard

### Heapster
Heapster enables Container Cluster Monitoring and Performance Analysis for Kubernetes - DEPRECATED
```bash
kubectl apply -f handson-labs-2018/3_Kubernetes/heapster.yml

kubectl top pod --all-namespaces
kubectl top pod -n kube-system

kubectl delete -f handson-labs-2018/3_Kubernetes/heapster.yml
```
* https://github.com/kubernetes/heapster/
* https://github.com/kubernetes/kops/blob/master/docs/addons.md
* https://github.com/kubernetes/kops/blob/master/addons/monitoring-standalone/

## Pipeline

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
* https://github.com/jenkins-x/jx
