###### AWSKRUG 2nd hands-on!

# ECS를 이용하여 자바 웹서비스 배포하기 

### 우 여 명 <small>( matholic )</small>

---

## 목차
1. 발표자 소개
1. 대상 독자
1. petclinic 소개
    - 기술 스택
    - 아키텍처
1. 용어 소개
2. 실습 시작

---

## 발표자 소개 

- [우 여 명](https://voyagerwoo.github.io)
- [Matholic](https://www.matholic.com), [Pocketmath](https://www.pocketmath.co.kr) 개발자 
- AWSKRUG container 소모임 운영

`spring` `groovy` `AWS` `docker` 
`data engineering`
`full cycle developer`

<!-- 
만 4년이 넘은 개발자입니다. 
매쓰홀릭이라는 수학 교육 솔루션 회사에서 일하고 있습니다.
첫 회사에서 인프라를 만질 기회가 없어서 그게 한이 되었는지 배포 자동화, 인프라 구성에 관심이 좀 있습니다.
소프트웨어 생명주기 전체를 알고 운영하는 full cycle developer를 목표로 일하고 공부하고 있습니다.
오늘 할 실습도 이와 관련이 있죠.
-->

---

## 대상 독자

- 도커 컨테이너의 개념을 알고 직접 이미지를 만들어본 개발자
- 웹서비스를 개발하고 배포해본 경험이 있는 개발자

--- 

## petclinic 소개

<small>

> https://github.com/spring-projects/spring-petclinic
> https://github.com/aws-samples/amazon-ecs-java-microservices

</small>

- 위 두 프로젝트에 큰 영향을 받아서 만든 실습 과정
- 간단한 동물병원 웹서비스
