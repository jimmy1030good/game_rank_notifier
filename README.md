# 게임 순위 알리미

중국, 한국, 일본의 iOS 게임 순위(무료/매출)를 자동으로 수집하여 Microsoft Outlook으로 전송하는 프로그램입니다.

## 사전 준비

1.  **Python 설치**: Python 3.x 버전이 설치되어 있어야 합니다.
2.  **Google Chrome 설치**: 스크래핑을 위해 Google Chrome 브라우저가 필요합니다.
3.  **Outlook 설치**: 이메일 전송을 위해 Microsoft Outlook 프로그램이 설치 및 설정되어 있어야 합니다.

## 설치 방법

1.  **프로젝트 다운로드**: `game_rank_notifier.py`, `requirements.txt`, `README.md` 파일을 `C:\Users\jimmy90\game_rank_project` 와 같이 한글이 없는 경로에 저장합니다.

2.  **ChromeDriver 다운로드**:
    *   Chrome 브라우저를 열고 주소창에 `chrome://version`을 입력하여 버전을 확인합니다. (예: `138.0.7204.158`)
    *   [Chrome for Testing 다운로드 페이지](https://googlechromelabs.github.io/chrome-for-testing/)로 이동하여, 확인한 버전에 맞는 `chromedriver` -> `win64` 의 URL을 복사합니다.
    *   다운로드한 `chromedriver-win64.zip` 파일의 압축을 해제하고, `chromedriver-win64` 폴더를 프로젝트 폴더(`C:\Users\jimmy90\game_rank_project`) 안에 위치시킵니다.

3.  **필요한 패키지 설치**:
    *   명령 프롬프트(cmd)를 열고 프로젝트 폴더로 이동합니다.
      ```bash
      cd C:\Users\jimmy90\game_rank_project
      ```
    *   다음 명령어를 실행하여 필요한 라이브러리를 설치합니다.
      ```bash
      pip install -r requirements.txt
      ```

## 사용 방법

명령 프롬프트에서 다음 명령어를 실행합니다. `--email` 옵션으로 결과를 수신할 이메일 주소를 입력합니다.

```bash
python game_rank_notifier.py --email your_email@example.com
```

스크립트가 실행되면, 자동으로 크롬 브라우저가 열리면서 각 국가의 순위를 수집한 후, 지정된 이메일 주소로 결과를 발송하고 종료됩니다.

## 문제 해결

-   **오류 발생 시**: 스크립트 실행 중 오류가 발생하면, 대부분 로컬 PC의 보안 프로그램(안티바이러스, 방화벽 등)이 `chromedriver.exe`의 실행을 차단하기 때문일 수 있습니다. 관련 프로그램을 잠시 비활성화하고 다시 시도해 보세요.
-   **SensorTower 웹사이트 변경**: SensorTower 웹사이트의 구조가 변경되면 스크립트가 정상적으로 작동하지 않을 수 있습니다. 이 경우, `game_rank_notifier.py` 파일의 HTML 선택자(CSS Selector) 부분을 수정해야 합니다.
