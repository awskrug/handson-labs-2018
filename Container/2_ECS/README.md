# ECS

동물병원 서비스를 ECS를 이용해서 배포해본다.

- backend repository : https://github.com/voyagerwoo/petclinic-rest
- frontend repository : https://github.com/voyagerwoo/petclinic-front


## Index

1. Prerequisites
1. EC2 + S3로 서비스 배포하기
1. ECS web console을 이용하여 배포 + CI/CD
1. ECS cli를 이용하여 배포하기 + CI/CD
1. spring config server 배포하기

## Prerequisites
실습전에 준비해야할 사항

1. `github` 계정, `aws` 계정
1. 개발환경 설정 : [Develop_Environment.md](Develop_Environment.md)
1. 우선 개발환경에 fork한 petclinic-rest, petclinic-front를 clone

## EC2에 배포하기
[Deploy_EC2.md](Deploy_EC2.md)

## ECS web console을 이용하여 백앤드 배포하기
[Deploy_ECS_web_console.md](Deploy_ECS_web_console.md)
