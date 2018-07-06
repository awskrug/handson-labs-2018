# ECS

동물병원 서비스를 ECS를 이용해서 배포해본다.

- backend repository : https://github.com/voyagerwoo/petclinic-rest
- frontend repository : https://github.com/voyagerwoo/petclinic-front
- config repository : https://github.com/voyagerwoo/petclinic-config-repo
- config server repository : https://github.com/voyagerwoo/petclinic-configserver


## Index
1. Introduction
1. Prerequisites
1. EC2 + S3로 서비스 배포하기
1. ECS web console을 이용하여 배포 + CodeBuild & CodePipeline
1. ECS cli를 이용하여 배포하기
1. spring config server 배포하기

## Introduction
[Introduction.md](Introduction.md)

## Prerequisites
실습전에 준비해야할 사항

1. `github` 계정, `aws` 계정
1. 개발환경 설정 : [Cloud9_Environment.md](Cloud9_Environment.md)

###  :warning: ***중요*** 확인 사항
1. 싱가포르 리전 사용 : cloud9으로 원활한 실습을 위해서 싱가포르(ap-southeast-1)에 배포합니다!
1. 루트 권한의 개인 계정 사용 

## EC2에 배포하기
[Deploy_EC2.md](Deploy_EC2.md)

## ECS web console을 이용하여 백앤드 배포하기
[Deploy_ECS_web_console.md](Deploy_ECS_web_console.md)

## ECS CLI를 이용하여 백앤드 배포하기
[Deploy_ECS_CLI.md](Deploy_ECS_CLI.md)

## Spring config server ECS로 배포하기
[Deploy_spring_config.md](Deploy_spring_config.md)


### :warning: 실습이 끝나면 서비스들을 모두 삭제해 주세요
1. CodePipeline 삭제
1. CodeBuild 삭제
1. ECS cluster 삭제
1. ECR 삭제
1. (CloudFormation 의 스택이 지워지지 않았다면 삭제)
1. Load Balancer 삭제
1. Target Group 삭제
1. Security Group 삭제
