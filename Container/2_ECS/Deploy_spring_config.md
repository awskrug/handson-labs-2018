# Spring config server ECS로 배포하기


## Fork and Clone github repositories

- https://github.com/voyagerwoo/petclinic-configserver
- https://github.com/voyagerwoo/petclinic-config-repo


## configserver 코드 수정

petclinic-configserver > src/main/resources/application.yml
```yaml
spring:
  cloud:
    config:
      server:
        git:
          uri: https://github.com/{github-username}/petclinic-config-repo 
```


## ECS CLI deploy
ECS CLI를 이용하여 배포하기

petclinic-configserver

```bash
./1_create_and_push_ecr.sh
./2_create_security_groups.sh
./3_create_alb.sh
./4_create_cluster.sh
./5_create_and_run_service.sh
./6_update_service.sh
```

## rest server 코드 수정
petclinic-rest > src/main/resouces/bootstrap.yml

```yaml
cloud:
    config:
      uri: {your-petclinic-configserver-alb-domain}
```

## rest server update 

petclinic-rest

```bash
./6_update_server.sh
```

## 확인

병원 이름 확인

```
curl http://{your-petclinic-rest-alb-domain}/petclinic/name
```

## config 수정 및 커밋 푸시
petclinic-config-repo > petclinic.yml

```yaml
petclinic:
  name: {your-petclinic-name}
```

## config refresh

```bash
curl -X POST {your-petclinic-rest-alb-domain}/actuator/refresh
```

## 다시 확인

병원 이름 다시 확인 확인

```bash
curl http://{your-petclinic-rest-alb-domain}/petclinic/name
```