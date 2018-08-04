# geoserver 배포 및 구경해보기

1. geoserver 배포(장고)
먼저 zappa_settings.json 에서 s3_bucket 이름을 "zappa-9vlx0h8hd" 에서 "zappa-<aws 어카운트번호>"로 변경해주세요.
이후 `zappa deploy dev`로 서버를 배포해주세요