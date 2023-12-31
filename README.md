<div><img src="https://capsule-render.vercel.app/api?type=waving&color=0:99cc99,100:009630&height=200&section=header&text=Moin&fontSize=90" /></div>

[![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2FLikeLion-at-DGU%2Fmoin_backend&count_bg=%236E79C9&title_bg=%23828282&icon=&icon_color=%23E7E7E7&title=%EB%AA%A8%EC%9D%B8+%EB%B0%B1%EC%97%94%EB%93%9C&edge_flat=false)](https://hits.seeyoufarm.com)

모두의 인공지능, 모인 백엔드 Repo입니다 :--)

# 👋 팀원 소개

## Moin Back-End 팀

| 이름                                         | 전공           | Email                |
| -------------------------------------------- | --------------  | -------------------- |
| 박영신      | 컴퓨터공학전공  | 2022110233@dgu.ac.kr |
| 차은호 | 컴퓨터공학전공      | eunho2002@dgu.ac.kr |

### Infra 담당 
| 이름                                         | 전공           | Email                |
| -------------------------------------------- | --------------  | -------------------- |
| 서희찬 | 컴퓨터공학전공      | gmlcks0513@dgu.ac.kr |


# 🛠️ Tech

## FrameWork
DRF
<br/>
DB : Postgresql
<br/>
Infra : Naver Cloud Server


## 1. 프로젝트 명

모두의 인공지능, 모인 
<br/>
<img width="432" alt="Screenshot 2023-07-27 at 6 23 38 PM" src="https://github.com/LikeLion-at-DGU/moin_frontend/assets/78739194/999527ec-36ca-4d8a-9f4c-91f6137c6c17">


## 2. 프로젝트 소개
> 요즘 인공지능 서비스가 많이 생겼는데..
직군별로 인기있는 인공지능 서비스는 뭘까?
그리고 옆집 디자이너는 디자인할 때 인공지능 쓰는 게 있던데..
디자인 관련된 인공지능이 너무 많네..?

뭘 써야 하지??😵‍💫

이런 인공지능들을 특징 및 직군별로 인기있는
서비스들을 한눈에 확인하고 후기 및 특징까지 정리되어 있는 모음 사이트 없나???
라는 생각에 등장한 서비스 **모인** 입니다:)


## 3. 프로젝트 실행 방법(자세한 건 노션에서 보자)
### 3-1. 가상환경 만들기
##### 최초 1회 실행
    python -m venv {가상 환경 이름}

    * 가상 환경 이름은 venv로 통일

#### 아래서부터는 반복
### 3-2. 가상환경 실행
    source venv/Scripts/activate

### 3-3. 라이브러리 설치
    pip install -r requirements.txt

    * 추가됐으면 추가한 사람이 'pip freeze > requirements.txt' 꼭 해주기
    * 작업하는 사람은 작업 전 pull 받고 'pip install -r requirements.txt' 꼭 해주기

### 3-4. db 마이그레이션 진행
    * manage.py 파일이 있는 위치로 이동 후
    python manage.py makemigrations
    python manage.py migrate

### 3-5. 서버 실행
    python manage.py runserver


## 💻 Folder
```
📦 moin_backend/        # (1) repositroy_root	
├─ .github
│    └─ ISSUE_TEMPLATE
│       └─ 모인의-이슈-템플릿.md
├─ .gitignore
├─ LICENSE
├─ manage.py
├─ README.md
├─ requirements.txt
└─ moin			        # (2) project_root
   ├─ __init__.py
   ├─ asgi.py
   ├─ settings.py
   ├─ urls.py
   └─ wsgi.py



```


## 🎯 Commit Convention

-   feat : 새로운 기능 추가
-   fix : 버그 수정
-   docs : 문서 수정
-   style : 코드 포맷팅, 세미콜론 누락, 코드 변경이 없는 경우
-   refactor: 코드 리펙토링
-   test: 테스트 코드, 리펙토링 테스트 코드 추가
-   chore : 빌드 업무 수정, 패키지 매니저 수정


## 💡 PR Convetion

| 아이콘 | 코드                       | 설명                     |
| ------ | -------------------------- | ------------------------ |
| 🎨     | :art                       | 코드의 구조/형태 개선    |
| ⚡️    | :zap                       | 성능 개선                |
| 🔥     | :fire                      | 코드/파일 삭제           |
| 🐛     | :bug                       | 버그 수정                |
| 🚑     | :ambulance                 | 긴급 수정                |
| ✨     | :sparkles                  | 새 기능                  |
| 💄     | :lipstick                  | UI/스타일 파일 추가/수정 |
| ⏪     | :rewind                    | 변경 내용 되돌리기       |
| 🔀     | :twisted_rightwards_arrows | 브랜치 합병              |
| 💡     | :bulb                      | 주석 추가/수정           |
| 🗃      | :card_file_box             | 데이버베이스 관련 수정   |
