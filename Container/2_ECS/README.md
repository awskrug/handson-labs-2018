# ECS

동물병원 서비스를 ECS를 이용해서 배포해봅니다.

- backend repository : https://github.com/voyagerwoo/petclinic-rest
- frontend repository : https://github.com/voyagerwoo/petclinic-front


## Index

1. EC2 배포하기
1. 프론트앤드 S3에 배포하기
1. ecs web console을 이용하여 배포하기
1. ecs cli를 이용하여 배포하기
1. CI / CD 파이프라인 구축하기
1. spring config server 배포하기

## Prerequisites
실습전에 준비해야할 사항들입니다. 아래 링크에서 꼭 확인해주세요!

[링크](./prerequisites.md)

## 실습 시작

우선 개발환경에 fork한 petclinic-rest, petclinic-front를 clone한다. 

### EC2 배포하기
TBL

### 프론트앤드 S3에 배포하기
working dir : petclinic-front 

1. 배포스크립트 수정

    package.json에 deploy:s3 스크립트에서 bucket 명을 자신의 버켓명으로 수정한다.
1. api host 수정
    src/services/restService.js 에서 서비스 호스트를 배포된 호스트로 변경한다.
    ```js
    const serviceHost = 'http://13.12.1.42:9460'
    ```
1. npm install
1. npm run deploy:s3
1. http://{버켓명}.s3-website.ap-northeast-2.amazonaws.com 에 들어가서 확인한다.

### ecs cli를 이용하여 배포하기
working dir : petclinic-rest

1. create and push ecr

    ```bash
    ./1_create_and_push_ecr.sh
    ```
1. create cluster
    ```bash
    ./2_create_cluster.sh 
    ```
    
1. create alb
    ```bash
    ./3_create_alb.sh 
    ```
    
1. create and run service
    ```bash
    ./4_create_and_run_service.sh 
    ```
    
    여기 까지 하면 서비스가 반영된다.
    
1. update service
    ```bash
    ./5_update_service.sh 
    ```
    코드를 수정하고 이 스크립트롤 실행하면 반영된다.
    

반영되고 petclinic-front에서 api host를 변경하고 다시 배포해본다. 

### CI / CD 파이프라인 구축하기

1. code builder 설정

1. code pipeline 설정


### spring config server 배포하기
