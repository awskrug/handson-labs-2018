서버리스 데이터레이크 - GIS

---

# 진행순서
1. 기본 설명
2. 개발환경 구축
3. geoserver 배포
4. datalake 구축
4.1. csv2shp 배포 및 geoserver를 통해 실습
4.2. shp2dynamodb 배포 및 geoserver를 통해 실습
4.3. shp2elasticsearch 배포 및 kibana로 직접 데이터 확인 및 간단한 자료 조회
4.4. firehouse2geojson 배포 및 geoserver를 통해 실습
4.5. shp2firehouse 배포 및 geoserver를 통해 실습
5. geojson을 아테네로 연결 및 쿼리 실습
6. geojson을 quicksight로 연결 및 시각화 실습

데이터레이크 배포는 단순히 3.datalake/templates/ 에 위치한 sls 템플릿 파일을
각 단계별로 3.datalake/serverless.yml에 덮어쓰기 하여 바로 패포를 하는 것이며
이때 추가되는 부분에 대한 설명 및 간략한 작동과정을 설명할 예정

## 할일

- [x] 데이터레이크 전체 플로우 도표 제작
- [ ] 시나리오 PPT 제작
- [x] 자료 수집 및 전처리 실습
- [x] geoserver 구현
- [ ] geoserver 업로드 s3 연동
- [ ] geoserver 배포 문서화
- [ ] csv2shp 구현
- [ ] csv2shp 배포 문서화
- [ ] shp2dynamodb 구현
- [ ] shp2dynamodb 배포 문서화
- [ ] shp2elasticsearch 구현
- [ ] shp2elasticsearch 배포 문서화
- [ ] firehouse2geojson 구현
- [ ] firehouse2geojson 배포 문서화
- [ ] shp2firehouse 구현
- [ ] shp2firehouse 배포 문서화
- [ ] geojson 아테네 실습 문서화
- [ ] geojson quicksight로 실습 문서화
