# 개발환경 구축

## 진행 순서
1. s3 생성
2. geoserver 배포
3. csv 업로드 해보기
4. csv 폴더 트리거 구성
5. shp 폴더 트리거 구성
6. json폴더 트리거 구성
5. 업로드 후 결과 확인
6. 초기화


### 참고
이후 모든 작업은 cloud9에서 진행하시면 됩니다.

1. S3 생성
`cd ~/handson-labs-2018/serverless_datalake/2.ingest_data`
`aws cloudformation create-stack --stack-name sls-datalake-s3 --template-body s3.yml`

2. geoserver 배포

3. csv 업로드 해보기

4. csv 트리거 구성

5. shp 트리거 구성

6. json 트리거 구성


3.


4. geoserver 배포(장고)
먼저 zappa_settings.json 에서 s3_bucket 이름을 "zappa-9vlx0h8hd" 에서 "zappa-aws" 어카운트 번호 로 변경해주세요.
이후 `zappa deploy dev`로 서버를 배포해주세요
