# Kubernetes on AWS : AWSKRUG Container hands-on #3

## Index

<!-- TOC depthFrom:2 depthTo:6 withLinks:1 updateOnSave:1 orderedList:0 -->

* [Bastion](#bastion)
* [Cluster](#cluster)
* [Ingress](#ingress-controller)
* [Sample](#sample-application)
* [Dashboard](#dashboard)
* [Heapster](#heapster)
* [Autoscaler](#autoscaler)

<!-- /TOC -->

## Synopsis

* KOPS를 이용하여 Kubernetes Cluster 생성
* ingress-nginx 설치 후 Sample Application과 도메인 연결
* dashboard, heapster 로 대시보드를 구성하고 모니터링 추가
* HorizontalPodAutoscaler, cluster-autoscaler 로 pod 과 node 를 스케일링
* `클러스터 제거` `(중요!!)` - 이 핸즈온 내용은 무료제공(free tier)를 벗어납니다!

## Requirement

* 공통
  * AWS 계정: <https://aws.amazon.com/ko/>
* 윈도우 사용자
  * Git Bash: <https://git-scm.com/download/win>
  * FireFox: <https://www.mozilla.org/ko/firefox/new/>

## Bastion

### AWS IAM - Access keys

* AWS 객체들을 관리하기 위하여 Access Key 를 발급 받습니다.
* <https://console.aws.amazon.com/iam/home?region=ap-northeast-2> 를 브라우저에서 엽니다.
* 좌측 메뉴에서 `Users` 를 선택합니다.
* `Add user` 버튼으로 새 사용자를 만듭니다.

![Add user](images/iam-01.png)

* User name 에 `awskrug` 를 입력합니다.
* `Programmatic access` 를 체크합니다.
* `Next: Permissions` 버튼을 눌러 다음 화면으로 이동합니다.

![Add user](images/iam-02.png)

* `Attach existing policies directly` 를 선택합니다.
* `AdministratorAccess` 를 검색하여 선택합니다.
* `Next: Review` 버튼을 눌러 다음 화면으로 이동합니다.
* `Create user` 버튼을 눌러 새 유저를 만듭니다.
* 생성된 Access key ID와 Secret access key 는 실습에 사용하므로 메모장에 복사해둡니다.

Note:

* `발급 받은 키는 유출되지 않도록 잘 관리 해야 합니다.`
* `Administrator` 는 너무 많은 권한을 가지고 있고, 이를 가진 유저 생성은 추천하지 않습니다.
* IAM 의 권한은 다음만 주셔도 됩니다.
  * AmazonEC2FullAccess
  * AmazonRoute53FullAccess
  * AmazonS3FullAccess
  * IAMFullAccess
  * AmazonVPCFullAccess

### AWS EC2 - Key Pairs

* 생성할 Instance 에 접속하기 위하여 프라이빗 키를 발급 받습니다.
* <https://ap-northeast-2.console.aws.amazon.com/ec2/v2/home> 를 브라우저에서 엽니다.
* 좌측 메뉴에서 `Key Pairs` 를 선택합니다.

![Key Pairs](images/key-01.png)

* `Create Key Pair` 버튼으로 새 키페어를 생성합니다.
* 이름은 `awskrug` 로 하겠습니다.
* 프라이빗 키 파일을 잘 저장해 둡니다.

Note:

* 파일명은 `awskrug.pem` 일 것 입니다.

### AWS EC2 - Instance

* 빠른 진행을 위하여 필요한 툴이 미리 설치된 AMI 로 부터 인스턴스를 생성 합니다.
* <https://ap-northeast-2.console.aws.amazon.com/ec2/v2/home> 를 브라우저에서 엽니다.

![AMIs](images/ami-01.png)

* 좌측 메뉴에서 `AMIs` 를 선택합니다.
* `Owned by me` 를 `Public images` 로 변경합니다.
* Add filter 에서 `AMI ID:` 를 선택 하고 `ami-0fade7d6d32c285f4` 를 입력합니다.
* 검색된 이미지로 `Launch` 를 선택 합니다.
* 기본 값인 `t2.micro` 를 사용 하겠습니다.
* `Next`와 `Review and Launch` 버튼을 눌러 다음 화면으로 이동합니다.
* `Launch` 버튼을 눌러 인스턴스를 생성합니다.
* Select a key pair 에 `awskrug` 가 선택 되었는지 확인합니다.
* 체크 박스를 체크 하고, `Launch Instances` 버튼으로 인스턴스를 생성합니다.

Note:

* 쉽게 찾는 링크
  * <https://ap-northeast-2.console.aws.amazon.com/ec2/v2/home?region=ap-northeast-2#Images:visibility=public-images;imageId=ami-0fade7d6d32c285f4>
* AMI 에 설치된 서비스
  * awscli, kops, kubectl, helm, docker, jenkins-x, openjdk8, maven, nodejs
* CentOS 혹은 Amazon Linux 에서 다음 쉘로 설치 가능 합니다.
  * `curl -sL toast.sh/helper/bastion.sh | bash`

### AWS EC2 - 접속 (Windows 사용자 - Git Bash)

* <https://ap-northeast-2.console.aws.amazon.com/ec2/v2/home> 를 브라우저에서 엽니다.
* 좌측 메뉴에서 `Instances` 를 선택합니다.
* 방금 만들었던 인스턴스를 선택 합니다.
* `IPv4 Public IP` 에 생성된 `IP` 를 확인 합니다.

* <https://git-scm.com/download/win> 를 브라우저에서 엽니다.
  * 다운로드 되는 파일을 설치 합니다.

![Git Bash](images/access-01.png)

* `Git Bash` 로 인스턴스에 접속 할 수 있습니다.
  * `PEM_PATH` 를 다운받은 `awskrug.pem` 파일 경로로 변경 합니다.
  * `PUBLIC_IP` 를 위에서 확인한 `IP` 로 변경하여 접속 합니다.

```bash
chmod 600 PEM_PATH/awskrug.pem
ssh -i PEM_PATH/awskrug.pem ec2-user@PUBLIC_IP
```

### AWS EC2 - 접속 (Windows 사용자 - PuTTY)

* <https://ap-northeast-2.console.aws.amazon.com/ec2/v2/home> 를 브라우저에서 엽니다.
* 좌측 메뉴에서 `Instances` 를 선택합니다.
* 방금 만들었던 인스턴스를 선택 합니다.
* `IPv4 Public IP` 에 생성된 `IP` 를 확인 합니다.

* <https://the.earth.li/~sgtatham/putty/latest/w64/putty-64bit-0.70-installer.msi> 를 다운로드 하여 설치 합니다.

* `PuTTYgen` 으로 프라이빗 키를 변환 해야 합니다.
  * `PuTTYgen` 을 시작합니다.
  * `Type of key to generate` 에서 `RSA` 를 선택합니다.
  * `Load` 를 선택합니다. `.pem` 파일을 찾으려면 모든 유형의 파일을 표시하는 옵션을 선택합니다.
  * `awskrug.pem` 을 선택합니다.
  * `Save private key` 버튼을 눌러 저장 합니다.
  * `awskrug.ppk` 가 만들어 졌습니다.

* `PuTTY` 로 인스턴스에 접속 할 수 있습니다.
  * `PuTTY` 를 시작합니다.
  * `Category` 창에서 `Session` 을 선택하고 다음 필드를 작성합니다.
  * `Host Name` 에 `ec2-user@` 과 위에서 확인한 `IP` 를 입력 합니다.
  * `Category` 창에서 `Connection` `SSH` 를 확장하고, `Auth` 를 선택 합니다.
  * `Browse` 버튼을 눌러 `awskrug.ppk` 파일을 찾아 선택 합니다.
  * `Open` 버튼을 눌러 접속 합니다.

Note:

* <https://docs.aws.amazon.com/ko_kr/AWSEC2/latest/UserGuide/putty.html>

### AWS EC2 - 접속 (Mac 사용자)

* <https://ap-northeast-2.console.aws.amazon.com/ec2/v2/home> 를 브라우저에서 엽니다.
* 좌측 메뉴에서 `Instances` 를 선택합니다.
* 방금 만들었던 인스턴스를 선택 합니다.
* `IPv4 Public IP` 에 생성된 `IP` 를 확인 합니다.

* `Terminal` 로 인스턴스에 접속 할 수 있습니다.
  * `PEM_PATH` 를 다운받은 `awskrug.pem` 파일 경로로 변경 합니다.
  * `PUBLIC_IP` 를 위에서 확인한 `IP` 로 변경하여 접속 합니다.

```bash
chmod 600 PEM_PATH/awskrug.pem
ssh -i PEM_PATH/awskrug.pem ec2-user@PUBLIC_IP
```

### SSH Key Gen

![ssh-key](images/bastion-01.png)

* 클러스터를 관리할 `ssh-key` 를 생성 합니다.

```bash
ssh-keygen -q -f ~/.ssh/id_rsa -N ''
```

Note:

* 클러스터 내에서 서로 접속 하기 위하여 필요 합니다.

### AWS Credentials

![Credentials](images/bastion-02.png)

* IAM 으로 생성하여 메모장에 복사해둔 `Access key ID` 와 `Secret access key` 를 등록합니다.

```bash
aws configure
```

Note:

* AWS 에 객체를 생성하기 위하여 필요 합니다.

## Cluster

![Cluster](images/bastion-03.png)

* 클러스터 이름을 설정 합니다.
* 클러스터 상태를 저장할 S3 Bucket 을 만들어 줍니다.
* `MY_UNIQUE_ID` 에는 본인의 이름을 넣어 만들어 주세요.

```bash
export KOPS_CLUSTER_NAME=awskrug.k8s.local
export KOPS_STATE_STORE=s3://kops-awskrug-MY_UNIQUE_ID

aws s3 mb ${KOPS_STATE_STORE} --region ap-northeast-2
```

### Create Cluster

![Create Cluster](images/bastion-04.png)

* Cloud 는 `AWS` 를 사용 하겠습니다.
* Master Node 는 `t2.medium` 1대로 하겠습니다.
* Worker Node 는 `t2.medium` 2대로 하겠습니다.

```bash
kops create cluster \
    --cloud=aws \
    --name=${KOPS_CLUSTER_NAME} \
    --state=${KOPS_STATE_STORE} \
    --master-size=t2.medium \
    --node-size=t2.medium \
    --node-count=2 \
    --zones=ap-northeast-2a,ap-northeast-2c \
    --network-cidr=10.10.0.0/16 \
    --networking=calico
```

```text
Must specify --yes to apply changes

Cluster configuration has been created.

Suggestions:
 * list clusters with: kops get cluster
 * edit this cluster with: kops edit cluster awskrug.k8s.local
 * edit your node instance group: kops edit ig --name=awskrug.k8s.local nodes
 * edit your master instance group: kops edit ig --name=awskrug.k8s.local master-ap-northeast-2a
```

Note:

* 위 명령을 실행해도 아직 클러스터는 만들어지지 않습니다.

### Edit Cluster

* 클러스터를 실제 생성하기 전, 클러스터를 조회 할 수 있습니다.

```bash
kops get cluster
```

```text
Cluster
NAME                 CLOUD    ZONES
cluster.k8s.local    aws      ap-northeast-2a,ap-northeast-2c

Instance Groups
NAME                      ROLE      MACHINETYPE    MIN    MAX    ZONES
master-ap-northeast-2a    Master    t2.medium      1      1      ap-northeast-2a
nodes                     Node      t2.medium      2      1      ap-northeast-2a,ap-northeast-2c
```

* 클러스터를 수정 할 수 있습니다.

```bash
kops edit cluster
```

* Cluster Autoscalier 에서 node 를 늘려 줄 수 있도록 `node maxSize` 를 변경 합니다.

```bash
kops edit instancegroup nodes
```

```yaml
spec:
  image: kope.io/k8s-1.9-debian-jessie-amd64-hvm-ebs-2018-03-11
  machineType: t2.medium
  maxSize: 12
  minSize: 2
```

### Update Cluster

* `kops update` 명령에 `--yes` 옵션으로 실제 클러스터가 생성 됩니다.

```bash
kops update cluster --name=${KOPS_CLUSTER_NAME} --yes
```

```text
Cluster is starting.  It should be ready in a few minutes.

Suggestions:
 * validate cluster: kops validate cluster
 * list nodes: kubectl get nodes --show-labels
 * ssh to the master: ssh -i ~/.ssh/id_rsa admin@api.awskrug.k8s.local
```

Note:

* VPC, Instance, ELB, Auto Scaling Group 에 관련 객체들이 생성됩니다.
* 클러스터 생성 완료까지 `10분` 정도 소요 됩니다.

### Validate Cluster

* `kops validate` 명령으로 생성이 완료 되었는지 확인 할 수 있습니다.

```bash
kops validate cluster --name=${KOPS_CLUSTER_NAME}
```

```text
Validating cluster awskrug.k8s.local

INSTANCE GROUPS
NAME                   ROLE   MACHINETYPE MIN MAX SUBNETS
master-ap-northeast-2a Master t2.medium   1   1   ap-northeast-2a
nodes                  Node   t2.medium   2   2   ap-northeast-2a,ap-northeast-2c

NODE STATUS
NAME                                           ROLE   READY
ip-10-10-10-10.ap-northeast-2.compute.internal master True
ip-10-10-10-11.ap-northeast-2.compute.internal node   True
ip-10-10-10-12.ap-northeast-2.compute.internal node   True

Your cluster awskrug.k8s.local is ready
```

### kubectl

* 생성이 완료 되었으면, 다음 명령으로 정보를 조회 할 수 있습니다.

```bash
kubectl get node

kubectl get deploy,pod,service --all-namespaces

kubectl get deploy,pod,service -n kube-system
kubectl get deploy,pod,service -n default
```

Note:

* 모든 네임스페이스 혹은 지정한 네임스페이스 객체를 조회 할 수 있습니다.
* <https://kubernetes.io/docs/tasks/>

## Addons

### Ingress Controller

* Ingress Controller 로 도메인을 내부 서비스로 연결해 줍니다.

```bash
curl -LO https://raw.githubusercontent.com/nalbam/kubernetes/master/addons/ingress-nginx-v1.6.0.yml

kubectl apply -f ingress-nginx-v1.6.0.yml
```

```text
namespace/kube-ingress created
serviceaccount/nginx-ingress-controller created
clusterrole.rbac.authorization.k8s.io/nginx-ingress-controller created
role.rbac.authorization.k8s.io/nginx-ingress-controller created
clusterrolebinding.rbac.authorization.k8s.io/nginx-ingress-controller created
rolebinding.rbac.authorization.k8s.io/nginx-ingress-controller created
service/nginx-default-backend created
deployment.extensions/nginx-default-backend created
configmap/ingress-nginx created
service/ingress-nginx created
deployment.extensions/ingress-nginx created
```

* Ingress-nginx 의 ELB 에서 얻은 IP 로 nip.io 도메인을 만듭니다.

```bash
# ELB 도메인을 획득 합니다.
kubectl get service -o wide -n kube-ingress

# ELB 도메인으로 ip 를 획득 합니다.
dig +short $(kubectl get service -o wide -n kube-ingress | grep ingress-nginx | awk '{print $4}' | head -n 1)
```

Note:

* 도메인이 있다면, ELB Domain 을 Route53 등을 이용하여 CNAME 으로 연결 해주면 됩니다.
* 도메인이 없는 상황을 가정하므로, ELB 에서 IP 를 얻어 nip.io 서비스를 이용했습니다.
  * <http://nip.io> 는 여러분의 IP 를 도메인처럼 동작 하도록 해주는 서비스 입니다.
  * IP 와 nip.io 조합의 도메인 앞에 어떤 문자든 IP 로 연결시켜 줍니다.
* 참고: <https://github.com/kubernetes/ingress-nginx>
* 참고: <https://github.com/kubernetes/kops/tree/master/addons/ingress-nginx>

### Sample Application

* 샘플 어플리케이션 yaml 파일을 다운 받아 vi 로 편집 합니다.
* 파일 하단의 nalbam.com 부분을 위의 ELB IP 를 넣어 `0.0.0.0.nip.io` 로 바꿔줍니다.

```bash
curl -LO https://raw.githubusercontent.com/nalbam/kubernetes/master/sample/sample-spring-ing.yml

vi sample-spring-ing.yml
```

```yaml
spec:
  rules:
  - host: sample-spring.apps.0.0.0.0.nip.io
    http:
      paths:
      - path: /
        backend:
          serviceName: sample-spring
          servicePort: 80
```

* 샘플 어플리케이션을 생성해 봅니다.

```bash
kubectl apply -f sample-spring-ing.yml
```

```text
deployment.apps/sample-spring created
service/sample-spring created
ingress.extensions/sample-spring created
horizontalpodautoscaler.autoscaling/sample-spring created
```

* Pod 와 Service 가 만들어졌습니다.

```bash
kubectl get deploy,pod,service -n default
```

* Ingress 설정에 의하여 각 도메인이 Ingress Controller 와 연결 되었습니다.

```bash
kubectl get ingress -o wide -n default
```

```text
NAME            HOSTS                               ADDRESS                                                 PORTS     AGE
sample-spring   sample-spring.apps.0.0.0.0.nip.io   a2aed74f77e8b-129875.ap-northeast-2.elb.amazonaws.com   80        43m
```

### Dashboard

* 웹 UI 를 통하여 정보와 상태를 볼수 있도록 Dashboard 를 올려 보겠습니다.

```bash
curl -LO https://raw.githubusercontent.com/nalbam/kubernetes/master/addons/dashboard-v1.8.3.yml

kubectl apply -f dashboard-v1.8.3.yml
```

```text
secret "kubernetes-dashboard-certs" created
serviceaccount "kubernetes-dashboard" created
role.rbac.authorization.k8s.io "kubernetes-dashboard-minimal" created
rolebinding.rbac.authorization.k8s.io "kubernetes-dashboard-minimal" created
deployment.apps "kubernetes-dashboard" created
service "kubernetes-dashboard" created
```

* dashboard 에 접속 하기 위해 `ServiceAccount` 와 `Role` 이 필요 합니다.
* `kube-system` 네임스페이스에 `admin` 유저를 만들겠습니다.

```bash
kubectl create serviceaccount admin -n kube-system
```

```text
serviceaccount "admin" created
```

* `admin` 유저에 `cluster-admin` 권한을 부여 하겠습니다.

```bash
kubectl create clusterrolebinding cluster-admin:kube-system:admin --clusterrole=cluster-admin --serviceaccount=kube-system:admin
```

```text
clusterrolebinding.rbac.authorization.k8s.io "cluster-admin:kube-system:admin" created
```

* 로그인은 `Token` 을 사용 하겠습니다.
* `Secret` 에서 `admin-token` 을 조회 해서 붙여 넣습니다.

```bash
kubectl describe secret $(kubectl get secret -n kube-system | grep admin-token | awk '{print $1}') -n kube-system
```

* Dashboard 는 Ingress 설정을 빼고, Service type 을 LoadBalancer 로 지정했습니다.
* 접속은 ELB 도메인을 조회 해서, `https://` 를 붙여 접속 하도록 하겠습니다.

```bash
kubectl get service -o wide -n kube-system | grep kubernetes-dashboard
```

Note:

* 참고: <https://github.com/kubernetes/dashboard/>
* 참고: <https://github.com/kubernetes/kops/tree/master/addons/kubernetes-dashboard>

### Heapster

* 대시보드 만 으로는 충분한 정보를 볼수 없습니다. 예를 들면 CPU, Memory 사용량 같은 것들...
* 힙스터를 설치하고 잠시 기다리면 정보가 수집되고, 대시보드에 보여집니다.

```bash
curl -LO https://raw.githubusercontent.com/nalbam/kubernetes/master/addons/heapster-v1.7.0.yml

kubectl apply -f heapster-v1.7.0.yml
```

```text
deployment.extensions "heapster" created
service "heapster" created
serviceaccount "heapster" created
clusterrolebinding.rbac.authorization.k8s.io "heapster" created
role.rbac.authorization.k8s.io "system:pod-nanny" created
rolebinding.rbac.authorization.k8s.io "heapster-binding" created
```

* 잠시 후 Heapster 가 정보를 수집하면 Dashboard 에 관련 정보를 추가로 볼 수 있습니다.
* 또한, CLI 로도 조회가 가능 합니다.

```bash
kubectl top pod --all-namespaces

kubectl top pod -n kube-system
kubectl top pod -n default
```

Note:

* 힙스터는 현재 `DEPRECATED` 되었습니다.
* 모니터링을 위해 `metrics-server` 또는 `Prometheus` 를 고려해 보시기 바랍니다.
* 참고: <https://github.com/kubernetes/heapster/>
* 참고: <https://github.com/kubernetes/kops/tree/master/addons/monitoring-standalone>

### Pod Autoscaler

* 사용량이 늘어남에 따라 pod 를 늘어나고, 사용량이 줄어듦에 따라 pod 가 줄어드는 매직을 부려 봅니다.
* 이미 `sample-spring` 에는 `HorizontalPodAutoscaler` 가 선언 되어있습니다.
* CPU 사용량을 얻기 위하여 `metrics-server` 를 설치 합니다.

```bash
git clone https://github.com/kubernetes-incubator/metrics-server

kubectl apply -f metrics-server/deploy/1.8+/
```

* `Deployment` 의 `replicas: 2` 인데, pod 를 조회 해보면. `1` 로 줄어들어 있습니다.
* `HorizontalPodAutoscaler` 설정에 따라 사용량이 없어서 `1` 로 줄였기 때문 입니다.

```bash
kubectl get hpa
```

```text
NAME            REFERENCE                  TARGETS   MINPODS   MAXPODS   REPLICAS
sample-spring   Deployment/sample-spring   0%/50%    1         100       1
```

* 아파치 (httpd) 를 설치하면 ab (apache benchmark) 가 설치 됩니다.

* 동시 `1`개 (concurrency, -c) 에서 `1,000,000`개 (requests, -n) 의 요청을 보내 봅시다.
  * 이 명령은 새창으로 해봅시다.

```bash
ab -n 1000000 -c 1 http://sample-spring.apps.0.0.0.0.nip.io/stress
```

* pod 가 늘어나면서, `TARGETS` 을 `50%` 이하로 맞추려고 노력 할 것 입니다.

```bash
kubectl get hpa -w
```

```text
NAME            REFERENCE                  TARGETS   MINPODS   MAXPODS   REPLICAS
sample-spring   Deployment/sample-spring   0%/50%    1         100       1
sample-spring   Deployment/sample-spring   0%/50%    1         100       2
sample-spring   Deployment/sample-spring   66%/50%   1         100       2
sample-spring   Deployment/sample-spring   82%/50%   1         100       2
sample-spring   Deployment/sample-spring   68%/50%   1         100       4
sample-spring   Deployment/sample-spring   42%/50%   1         100       4
sample-spring   Deployment/sample-spring   34%/50%   1         100       4
sample-spring   Deployment/sample-spring   36%/50%   1         100       4
```

Note:

* `4` 정도는 무리 없이 감당하는 군요.
* 참고: <https://github.com/kubernetes-incubator/metrics-server>
* 참고: <https://github.com/kubernetes/kops/tree/master/addons/metrics-server>

### Cluster Autoscaler

* 이번에는 동시 `3`개 (concurrency, -c) 에서 `1,000,000`개 (requests, -n) 의 요청을 보내 봅시다.
  * 이 명령은 새창으로 해봅시다.

```bash
ab -n 1000000 -c 3 http://sample-spring.apps.0.0.0.0.nip.io/stress
```

```bash
kubectl get hpa -w
```

```text
NAME            REFERENCE                  TARGETS    MINPODS   MAXPODS   REPLICAS
sample-spring   Deployment/sample-spring   77%/50%    1         100       7
sample-spring   Deployment/sample-spring   65%/50%    1         100       7
sample-spring   Deployment/sample-spring   64%/50%    1         100       7
sample-spring   Deployment/sample-spring   63%/50%    1         100       7
```

* `Pod` 상태를 확인해 봅시다.

```bash
kubectl get pod -n default
```

```text
NAME                            READY     STATUS    RESTARTS   AGE
sample-spring-6566df5db-4c7p6   1/1       Running   0          13m
sample-spring-6566df5db-7sbdq   0/1       Pending   0          58s
sample-spring-6566df5db-jjzlv   1/1       Running   0          4m
sample-spring-6566df5db-9b6wb   1/1       Running   0          19m
sample-spring-6566df5db-b5pb8   1/1       Running   0          58s
sample-spring-6566df5db-dgp2v   0/1       Pending   0          58s
sample-spring-6566df5db-wltj6   1/1       Running   0          10m
```

* `Dashboard` 를 통해서도 확인해 봅시다.

```text
0/3 nodes are available: 1 PodToleratesNodeTaints, 2 Insufficient cpu.
```

* 사용량이 더 늘어나면, 현재의 Cluster 공간보다 더 많은 Application 을 띄우려 시도 할것 입니다.
* 하지만 `CPU` 자원이 부족하여 더이상 pod 가 생성되지 않고 에러가 발생하고 있습니다.

* 그래서 `Cluster Autoscaler` 설치해 봅니다.

```bash
export ADDON="cluster-autoscaler-v1.8.0.yml"

curl -LO https://raw.githubusercontent.com/nalbam/kubernetes/master/addons/${ADDON}

MIN_NODES=2
MAX_NODES=8
AWS_REGION=ap-northeast-2
GROUP_NAME="nodes.${KOPS_CLUSTER_NAME}"

sed -i -e "s@{{MIN_NODES}}@${MIN_NODES}@g" "${ADDON}"
sed -i -e "s@{{MAX_NODES}}@${MAX_NODES}@g" "${ADDON}"
sed -i -e "s@{{GROUP_NAME}}@${GROUP_NAME}@g" "${ADDON}"
sed -i -e "s@{{AWS_REGION}}@${AWS_REGION}@g" "${ADDON}"

kubectl apply -f ${ADDON}
```

```text
serviceaccount/cluster-autoscaler created
clusterrole.rbac.authorization.k8s.io/cluster-autoscaler created
role.rbac.authorization.k8s.io/cluster-autoscaler created
clusterrolebinding.rbac.authorization.k8s.io/cluster-autoscaler created
rolebinding.rbac.authorization.k8s.io/cluster-autoscaler created
deployment.extensions/cluster-autoscaler created
```

* 로그 조회도 해 봅시다.

```bash
kubectl logs $(kubectl get pod -n kube-system | grep cluster-autoscaler | awk '{print $1}') -n kube-system -f
```

* `Node` 가 `1`개가 늘어나 `3`개가 되었습니다.

```bash
kubectl get node
```

```text
NAME                                              STATUS    ROLES     AGE       VERSION
ip-10-10-10-10.ap-northeast-2.compute.internal    Ready     master    41m       v1.9.6
ip-10-10-10-11.ap-northeast-2.compute.internal    Ready     node      39m       v1.9.6
ip-10-10-10-12.ap-northeast-2.compute.internal    Ready     node      39m       v1.9.6
ip-10-10-10-13.ap-northeast-2.compute.internal    Ready     node      12m       v1.9.6
```

* pod 도 이제 `8` 에서 안정화 되었습니다.

```bash
kubectl get hpa -w
```

```text
NAME            REFERENCE                  TARGETS    MINPODS   MAXPODS   REPLICAS
sample-spring   Deployment/sample-spring   64%/50%    1         100       7
sample-spring   Deployment/sample-spring   63%/50%    1         100       7
sample-spring   Deployment/sample-spring   56%/50%    1         100       7
sample-spring   Deployment/sample-spring   56%/50%    1         100       8
sample-spring   Deployment/sample-spring   44%/50%    1         100       8
sample-spring   Deployment/sample-spring   44%/50%    1         100       8
```

Note:

* 참고: <https://github.com/kubernetes/kops/tree/master/addons/cluster-autoscaler>

## Clean Up

* Kubernetes Cluster 를 지웁니다.

```bash
kops delete cluster --name=${KOPS_CLUSTER_NAME} --yes
```

* EC2 Instance (bastion) 를 지웁니다.
  * <https://ap-northeast-2.console.aws.amazon.com/ec2/v2/home?region=ap-northeast-2#Instances>

* EC2 Key Pair 를 지웁니다.
  * <https://ap-northeast-2.console.aws.amazon.com/ec2/v2/home?region=ap-northeast-2#KeyPairs>

* IAM User 를 지웁니다.
  * <https://console.aws.amazon.com/iam/home?region=ap-northeast-2#/users>

## Thank You
