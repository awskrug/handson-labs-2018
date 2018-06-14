# ECS

동물병원 서비스를 ECS를 이용해서 배포해본다.

- backend repository : https://github.com/voyagerwoo/petclinic-rest
- frontend repository : https://github.com/voyagerwoo/petclinic-front
- config repository : https://github.com/voyagerwoo/petclinic-config-repo
- config server repository : https://github.com/voyagerwoo/petclinic-configserver


## Index

1. Prerequisites
1. EC2 + S3로 서비스 배포하기
1. ECS web console을 이용하여 배포 + CI/CD
1. ECS cli를 이용하여 배포하기 + CI/CD
1. spring config server 배포하기

## Prerequisites
실습전에 준비해야할 사항

1. `github` 계정, `aws` 계정
1. 개발환경 설정 : [Cloud9_Environment.md](Cloud9_Environment.md)
###  :warning: ***중요*** 싱가포르 리전 사용
cloud9으로 원활한 실습을 위해서 싱가포르(ap-southeast-1)에 배포합니다!

## EC2에 배포하기
[Deploy_EC2.md](Deploy_EC2.md)

## ECS web console을 이용하여 백앤드 배포하기
[Deploy_ECS_web_console.md](Deploy_ECS_web_console.md)

## ECS CLI를 이용하여 백앤드 배포하기
[Deploy_ECS_CLI.md](Deploy_ECS_CLI.md)

## Spring config server ECS로 배포하기
[Deploy_spring_config.md](Deploy_spring_config.md)