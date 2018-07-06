# 개발환경 구축

## ec2 + vscode 개발환경 구축
개발환경을 통일하기 위해서 ec2 인스턴스를 실행하고 vscode로 구축합니다. 
코드 수정은 vs code에서 진행하고 스크립트 실행은 ssh로 접속하여 실행합니다.

### EC2
1. Amazon Linux AMI 2018.03.0 (HVM), SSD Volume Type - t2.small 인스턴스를 하나 실행, 이름은 `petclinic-dev`
    
    원할한 실습을 위해서 키페어 이름은 petclinic으로 통일합니다.
    ![](./images/ec2-keypair.png)
    
1. java8 업그레이드, git 설치, node js, jq 설치
    ```bash
    # upgrade java8
    sudo yum install -y java-1.8.0-openjdk-devel.x86_64
    sudo /usr/sbin/alternatives --config java
    sudo yum remove java-1.7.0-openjdk
    javac -version  
 
    # install git
    sudo yum install git 
 
    #install nodejs
    curl --silent --location https://rpm.nodesource.com/setup_8.x | sudo bash -
    sudo yum -y install nodejs

    # install jq 
    sudo yum -y install jq
    ```
    
1. docker 설치
    ```bash
    sudo yum update -y
    sudo yum install -y docker
    sudo usermod -a -G docker $USER
    exit
    ```
    다시 ssh 접속
    ```bash
    sudo service docker start
    docker ps
    ```
 
1. ecs-cli 설치
    ```bash
    sudo curl -o /usr/local/bin/ecs-cli https://s3.amazonaws.com/amazon-ecs-cli/ecs-cli-linux-amd64-latest
    sudo chmod +x /usr/local/bin/ecs-cli
 
    ```
1. `petclinic ec2`에 `/home/ec2-user/workspace` 디렉토리 생성
1. `petclinic ec2`에서 루트권한으로 aws configure


### local pc
1. vscode 설치
1. vscode ftp-simple Extension 설치 ([참고 링크](http://investor-js.blogspot.com/2017/12/visual-studio-code-aws-ec2.html))
1. ftp-simple config
    ```json
    [
    	{
    		"name": "petclinic-dev",
    		"host": "${host.ip}",
    		"port": 22,
    		"type": "sftp",
    		"username": "ec2-user",
    		"path": "/home/ec2-user/workspace",
    		"autosave": true,
    		"confirm": false,
    		"privateKey": "/your/path/petclinic.pem"
    	}
    ]    
    ```

 



