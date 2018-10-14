## 3 단계 : 워크 플로우에 병렬 처리 추가

메타 데이터를 추출하고 확인한 후 이제 상태 머신에 몇 가지 단계를 추가할 준비가 되었습니다. 섬네일 이미지 만들기, 이미지 인식 및 메타 데이터 저장/인덱싱을 합니다. 섬네일 생성 및 이미지 인식은 서로 의존하지 않기 때문에 [병렬 상태](https://docs.aws.amazon.com/step-functions/latest/dg/amazon-states-language-parallel-state.html)를 활용해서 동시에 실행 시킬 수 있습니다.

<img src="images/3-state-machine-parallel.png" width="60%">

### 3A 단계 : 상태 머신 정의 업데이트

이제 상태 머신에 단계를 점진적으로 추가, 배포 및 테스트하고 상태 머신에 병렬 단계를 추가하는 몇가지 경험을 얻었습니다. (마지막 상태의 최종 JSON에서 내보내거나 가져 오는 것을 잊지 마세요.) 상태 머신을 사용하여 섬네일 이미지와 이미지 인식을 동시에 수행 할 수 있습니다.

구문에 대한 도움이 필요하면 다음 설명서를 살펴보세요.

- [병렬 상태](https://docs.aws.amazon.com/step-functions/latest/dg/amazon-states-language-parallel-state.html)
- [작업 상태](https://docs.aws.amazon.com/step-functions/latest/dg/amazon-states-language-task-state.html)
- [Amazon States Language Spec](https://states-language.net/spec.html)

위에서 언급 한 문서에 대한 링크를 쉽게 따라갈 수 있도록 JSON을 직접 편집하는 것이 좋습니다.

<details>
<summary><strong> 힌트를 얻기 위해 확장 </strong></summary><p>

- 첫번째 단계는 *Parallel State* 의 유형을 **Pass** 에서 **Parallel** 로 변경하세요.

- **Parallel State** 내의 병렬 작업은 상태 머신 객체의 배열로 입력됩니다.

	```JSON
	"Parallel": {
	  "Type": "Parallel",
	  "Branches": [<STATE_MACHINE_OBJECT>, ..., <STATE_MACHINE_OBJECT>],
	  "End": true
	}
	```

- 각 분기에 대해 해당 람다 함수를 트리거하는 **Task** 상태가 있는 상태 머신 개체를 만드세요.

	- ``sfn-workshop-setup-DetectLabel``은 딥러닝 기반 이미지 분석 [Amazon Rekognition](https://aws.amazon.com/rekognition/) 서비스 및 특히 [DetectLabels API](http://docs.aws.amazon.com/rekognition/latest/dg/API_DetectLabels.html)를 활용하여 처리 된 이미지에 어떤 개체와 개념이 표시되는지에 대한 메타 데이터를 얻습니다.

    - ``sfn-workshop-setup-Thumbnail``은 섬네일 이미지를 생성을 위해 [GraphicsMagick for node.js](http://aheckmann.github.io/gm/docs.html) 라이브러리를 사용합니다.

</details>

이제 단계 1D를 기억해 두었습니다. 상태 입력을 출력과 병합하는 방법을 배웠으므로 [AWS Step Functions](https://docs.aws.amazon.com/step-functions/latest/dg/awl-ref-paths.html) 기능을 사용하여 두 줄을 모두 사용할 수 있게되었습니다.

특히 *Parallel State* 에서 **ResultPath**를 사용하여 병렬 상태 머신 출력의 배열을 다운 스트림 상태에서 사용할 수 있게하세요. `parallelResults` 속성을 사용하세요.

<details>
<summary><strong> 힌트를 얻기 위해 확장 </strong></summary><p>

```JSON
"Parallel": {
  "Type": "Parallel",
  "Branches": [<STATE_MACHINE_OBJECT>, ..., <STATE_MACHINE_OBJECT>],
  "ResultPath": "$.parallelResults",
  "End": true
}
```
</details>


이제 원하는 이미지로 상태 머신을 테스트하세요!

- Amazon Rekognition에서 감지한 레이블과 섬네일 이미지의 S3 위치가 모두 출력에서 ​​사용 가능한지 확인하세요.

	<img src="images/3-state-machine-parallel-with-output.png" width="90%">

- 섬네일 이미지가 **Thumbnail** 폴더 아래의 S3 버킷에 있는지 확인하세요.


### 최종 JSON
<details>
<summary><strong> JSON 정의를 확장합니다. </strong></summary><p>

```JSON
{
  "StartAt": "ExtractImageMetadata",
  "Comment": "Image Processing State Machine - step 3 final",
  "States": {
    "ExtractImageMetadata": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-west-2:012345678901:function:sfn-workshop-setup-ExtractMetadata",
      "Catch": [
        {
          "ErrorEquals": [
            "ImageIdentifyError"
          ],
          "ResultPath": "$.error",
          "Next": "NotSupportedImageType"
        }
      ],
      "ResultPath": "$.extractedMetadata",
      "Next": "ImageTypeCheck"
    },
    "ImageTypeCheck": {
      "Type": "Choice",
      "Choices": [
        {
          "Or": [
            {
              "Variable": "$.extractedMetadata.format",
              "StringEquals": "JPEG"
            },
            {
              "Variable": "$.extractedMetadata.format",
              "StringEquals": "PNG"
            }
          ],
          "Next": "Parallel"
        }
      ],
      "Default": "NotSupportedImageType"
    },
    "NotSupportedImageType": {
      "Type": "Fail",
      "Cause": "Image type not supported!",
      "Error": "FileTypeNotSupported"
    },
    "Parallel": {
      "Type": "Parallel",
      "Branches": [
        {
          "StartAt": "DetectLabelsRekognition",
          "States": {
            "DetectLabelsRekognition": {
              "Type": "Task",
              "Resource": "arn:aws:lambda:us-west-2:012345678901:function:sfn-workshop-setup-DetectLabel",
              "End": true
            }
          }
        },
        {
          "StartAt": "Thumbnail",
          "States": {
            "Thumbnail": {
              "Type": "Task",
              "Resource": "arn:aws:lambda:us-west-2:012345678901:function:sfn-workshop-setup-Thumbnail",
              "End": true
            }
          }
        }
      ],
      "ResultPath": "$.parallelResults",
      "End": true
    }
  }
}

```
</details>

### 다음 단계
이제 [4 단계](step-4.md)로 이동할 준비가 되었습니다!

