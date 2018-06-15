# Kubernetes Hands-on

## Index

<!-- TOC depthFrom:2 depthTo:6 withLinks:1 updateOnSave:1 orderedList:0 -->

* [Bastion](#bastion)
* [Cluster](#cluster)
* [Addons](#addons)
* [Pipeline](#pipeline)

<!-- /TOC -->

### Basic Knowledge

* Kubernetes 를 들어봤다.
* AWS 에 인스턴스를 만들어 봤다.
* SSH 로 접속을 할 수 있다.
* 필요 계정 : AWS
  * https://aws.amazon.com/ko/

## Bastion

### AWS IAM - Access keys

* https://console.aws.amazon.com/iam/home?region=ap-northeast-2#/users 를 브라우저에서 엽니다.
* `Add user` 버튼으로 새 사용자를 만듭니다.
* User name 에 `awskrug` 를 입력합니다.
* `Programmatic access` 를 체크합니다.
* `Next: Permissions` 버튼을 눌러 다음 화면으로 이동합니다.
* `Attach existing policies directly` 를 선택합니다.
* `AdministratorAccess` 를 검색하여 선택합니다.
* `Next: Review` 버튼을 눌러 다음 화면으로 이동합니다.
* `Create user` 버튼을 눌러 새 유저를 만듭니다.
* `Download .csv` 버튼을 눌러 파일을 저장합니다.

Note:
- AWS 객체들을 관리하기 위하여 Access Key 를 발급 받습니다.
- 발급 받은 키는 유출되지 않도록 잘 관리 해야 합니다.

### AWS EC2 - Key Pairs

* https://ap-northeast-2.console.aws.amazon.com/ec2/v2/home 를 브라우저에서 엽니다.
* 좌측 메뉴에서 `Key Pairs` 를 선택합니다.
* `Create Key Pair` 버튼으로 새 키페어를 생성합니다.
* 이름은 `awskrug` 로 하겠습니다.
* 프라이빗 키 파일을 잘 저장해 둡니다.

Note:
- 생성할 Instance 에 접속하기 위하여 프라이빗 키를 발급 받습니다.

### AWS EC2 - Instance

* https://ap-northeast-2.console.aws.amazon.com/ec2/v2/home 를 브라우저에서 엽니다.
* 좌측 메뉴에서 `AMIs` 를 선택합니다.
* `Owned by me` 를 `Public images 로 변경합니다.
* Add filter 에서 `AMI ID: 를 선택 하고 `ami-3949e357` 를 입력합니다.
* 검색된 이미지로 `Launch` 를 선택 합니다.
* 기본 값인 `t2.micro` 를 사용 하겠습니다.
* `Review and Launch` 버튼을 눌러 다음 화면으로 이동합니다.
* `Launch` 버튼을 눌러 인스턴스를 생성합니다.
* Select a key pair 에 `awskrug` 가 선택 되었는지 확인합니다.
* 체크 박스를 체크 하고, `Launch Instances` 버튼으로 인스턴스를 생섭합니다.

Note:
- 모두가 같은 환경에서 진행 할수 있도록 같은 AMI 로 부터 인스턴스를 생성 합니다.
- https://ap-northeast-2.console.aws.amazon.com/ec2/v2/home?region=ap-northeast-2#Images:visibility=public-images;imageId=ami-3949e357

### AWS EC2 - 접속 (Windows 사용자)

* Windows 사용자의 경우 PuTTY-gen 으로 프라이빗 키를 변환 해야 합니다.

Note:
- https://docs.aws.amazon.com/ko_kr/AWSEC2/latest/UserGuide/putty.html

### AWS EC2 - 접속 (Mac 사용자)

* https://ap-northeast-2.console.aws.amazon.com/ec2/v2/home 를 브라우저에서 엽니다.
* 좌측 메뉴에서 `Instances` 를 선택합니다.
* 방금 만들었던 인스턴스를 선택 합니다.
* `IPv4 Public IP` 에 생성된 IP 를 확인 합니다.
* `PEM_PATH` 를 다운받은 PEM 파일 경로로 변경 합니다.
* `PUBLIC_IP` 를 본인의 IP 로 변경하여 접속 합니다.

```bash
ssh -i PEM_PATH/awskrug.pem ec2-user@PUBLIC_IP
```

Note:
- https://ap-northeast-2.console.aws.amazon.com/ec2/v2/home?region=ap-northeast-2#Instances

## Bastion

### SSH Key Gen

* 클러스터를 관히할 ssh-key 를 생성 합니다.

```bash
ssh-keygen -q -f ~/.ssh/id_rsa -N ''
```

Note:
- 클러스터 내에서 서로 접속 하기 위하여 필요 합니다.

### AWS Credentials

* 다운 받았던 `awskrug.csv` 파일을 열어 Access Key 를 확인 합니다.
* `~/.aws/credentials` 파일에 Access Key 를 넣고 저장 합니다.

```bash
vi ~/.aws/credentials
```

```
[default]
aws_access_key_id=
aws_secret_access_key=
```

## Cluster

* 클러스터 이름을 설정 합니다.
* 클러스터 상태를 저장할 S3 Bucket 을 만들어 줍니다.
* `MY_UNIQUE_ID` 에 본인의 아이디를 넣어 만들어 주세요.

```bash
export KOPS_CLUSTER_NAME=awskrug.k8s.local
export KOPS_STATE_STORE=s3://terraform-awskrug-MY_UNIQUE_ID

# aws s3 bucket for state store
aws s3 mb ${KOPS_STATE_STORE} --region ap-northeast-2
```

Note:
- S3 Bucket 은 유니크 해야 합니다.

### Create Cluster

* 마스터 1대, 노드 2대로 구성된 클러스터를 생성합니다.

```bash
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
- 위 명령을 실행해도 아직 클러스터는 만들어지지 않습니다.

### Create Cluster

* `kops update` 명령에 `--yes` 를 하면 실제 클러스터가 생성 됩니다.

```bash
kops update cluster --name=${KOPS_CLUSTER_NAME} --yes
```

Note:
- VPC, ELB, Route53, Instance 에 객체들이 생성됩니다.
- 클러스터 생성까지 10여분이 소요 됩니다.

### Validate Cluster

* `kops validate` 명령으로 생성이 완료 되었는지 확인 할수 있습니다.

```bash
kops validate cluster --name=${KOPS_CLUSTER_NAME}
```

### kubectl

* 생성이 완료 되었으면, 다음 명령으로 정보를 조회 할수 있습니다.

```bash
# kubectl config
kubectl config view

# kubectl get
kubectl get node,deploy,pod,svc --all-namespaces
kubectl get node,deploy,pod,svc -n kube-system
kubectl get node,deploy,pod,svc -n default
```

Note:
- 모든 네임스페이스 혹은 지정한 네임스페이스 객체를 조회 할수 있습니다.

### Sample

* 샘플 웹을 하나 생성해 봅니다.

```bash
# apply
kubectl apply -f https://raw.githubusercontent.com/nalbam/docs/master/201806/Kubernetes/sample/sample-web.yml

# delete
kubectl delete -f https://raw.githubusercontent.com/nalbam/docs/master/201806/Kubernetes/sample/sample-web.yml
```

* Pod 와 Service 가 만들어졌고, AWS 에서 만들었으므로 ELB 도 생겼습니다.
  * https://ap-northeast-2.console.aws.amazon.com/ec2/v2/home?region=ap-northeast-2#LoadBalancers

## Addons

### Dashboard

* 웹 UI 를 통하여 정보와 상태를 볼수 있도록 Dashboard 를 올려 보겠습니다.

```bash
kubectl apply -f https://raw.githubusercontent.com/nalbam/docs/master/201806/Kubernetes/sample/dashboard-v1.8.3.yml
```

* 생성된 ELB 로 접속 할수 있습니다.
  * https://ap-northeast-2.console.aws.amazon.com/ec2/v2/home?region=ap-northeast-2#LoadBalancers
- 로그인을 위해 `Secret` 에서 토큰을 조회 해서 붙여 넣습니다.

```bash
kubectl describe secret -n kube-system $(kubectl get secret -n kube-system | grep kubernetes-dashboard-token | awk '{print $1}')
```

* 접속해보면 권한 때문에 정상적으로 보이지 않을 겁니다. 권한 부여를 합니다.

```bash
kubectl create clusterrolebinding cluster-admin:kube-system:kubernetes-dashboard --clusterrole=cluster-admin --serviceaccount=kube-system:kubernetes-dashboard
```

Note:
- https://github.com/kubernetes/dashboard/

---

### Heapster

* 대시보드 로는 충분한 정보를 볼수 잆습니다. 예를 들면 CPU, Memory 사용량 같은것들...
* 힙스터를 설치하고 잠시 기다리면 정보가 수집되고, 대시보드에 보여집니다.
* 참고로 힙스터는 현재 `DEPRECATED` 되었습니다.

```bash
kubectl apply -f https://raw.githubusercontent.com/nalbam/docs/master/201806/Kubernetes/sample/heapster-v1.7.0.yml
```

* 잠시후 Heapster 가 정보를 수집하면 Dashboard 에 관련 정보를 추가로 볼수 있습니다.

Note:
- https://github.com/kubernetes/heapster/

## Pipeline

* Jenkins X

---

### Jenkins X
```bash
jx install --provider=aws

jx console

jx get activity -f jx-demo -w
jx get build logs nalbam/jx-demo/master
jx get build logs nalbam/jx-demo/dev

```
* https://jenkins-x.io/

Note:
- ELB 의 도메인을 사용하겠냐는 질문에 `Y` 를 입력 합니다.
- ELB 의 IP 를 이용한 nio.io 에 `엔터` 를 입력 합니다.
- Github user name 에 본인의 계정을 입력합니다.
- API Token 입력을 위하여 제시된 주소로 갑니다. 토큰을 만들어서 붙여 넣습니다.
- `이때 토큰문자열 앞의 공백에 주의해서 붙여 넣어 주세요.`
- Jenkins 를 생성하고, Jenkins 주소가 나타날 것입니다.
- 아이디 `admin` 과 제시된 비밀번호를 입력해 주세요.
- Show API Token 버튼을 클릭하여 키를 붙여 넣습니다.
- `stageing` 과 `production` 관리 repo 를 저장할 계정을 선택 합니다.

---

### Create Project
```bash
jx create spring -d web -d actuator

jx get applications
jx get pipelines
```

Note:
- Spring Boot 프로젝트를 생성합니다.
- Github 에 프로젝트가 생성됩니다.

---

### Create Branch

---

### Pull Request

---

### Merge

---

### Production
```bash
jx promote jx-demo --env production
```

---

## Clean Up
```bash
jx uninstall
rm -rf ~/.jx

kops delete cluster --name=${KOPS_CLUSTER_NAME} --yes
```

Note:
- 지금까지 만들었던 클러스터를 지웁니다.
- 접속용으로 만들었던 인스턴스를 지웁니다.
- Access Key 를 지웁니다.
- Github 토큰을 지웁니다. https://github.com/settings/tokens

---

## Thank You
