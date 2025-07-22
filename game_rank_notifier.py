import os
import time
import argparse
from datetime import datetime
from bs4 import BeautifulSoup
from google.cloud import translate_v2 as translate
import requests
import sys

# stdout 인코딩을 UTF-8로 설정
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Google Cloud 인증 키 경로 설정 (절대 경로 권장)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "my-gcp-key.json")  # 예: C:/Users/yourname/key.json

# Google 번역 함수 정의
def translate_text_google(text, source_lang, target_lang):
    try:
        client = translate.Client()
        result = client.translate(text, source_language=source_lang, target_language=target_lang)
        return result['translatedText']
    except Exception as e:
        print(f" Google 번역 오류 발생: {e}")
        return text  # 실패 시 원문 반환

# 게임 이름 번역 함수
def translate_game_name(game_name, country_code):
    if country_code == 'KR':
        return game_name, ""  # 한국어는 번역하지 않음, 원문은 비워둠

    try:
        lang_map = {'CN': 'zh-CN', 'JP': 'ja'}
        source_lang = lang_map.get(country_code, 'auto')

        translated_en = translate_text_google(game_name, source_lang, 'en')
        translated_ko = translate_text_google(translated_en, 'en', 'ko')

        return translated_ko if translated_ko else game_name, game_name
    except Exception as e:
        print(f"게임 이름 번역 중 오류 발생 ({game_name}, {country_code}): {e}")
        return game_name, game_name # 실패 시 원문과 원문 반환

# 새 함수 추가 시작
def search_game_store_link(game_name):
    print(f"Searching for store link for: {game_name}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Try Google Play Store first
    play_query = f"{game_name} Google Play Store"
    play_url = f"https://www.google.com/search?q={play_query}"
    try:
        play_response = requests.get(play_url, headers=headers, timeout=10)
        play_response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        play_soup = BeautifulSoup(play_response.content, 'html.parser', from_encoding='utf-8')
        for link in play_soup.find_all('a'):
            href = link.get('href')
            if href and "play.google.com" in href and "/store/apps/details" in href:
                print(f"Found Google Play link: {href}")
                return href
    except requests.exceptions.RequestException as e:
        print(f"Google Play search error: {str(e).encode('utf-8', 'replace').decode('utf-8')}")

    # If not found, try Apple App Store
    app_query = f"{game_name} Apple App Store"
    app_url = f"https://www.google.com/search?q={app_query}"
    try:
        app_response = requests.get(app_url, headers=headers, timeout=10)
        app_response.raise_for_status()
        app_soup = BeautifulSoup(app_response.content, 'html.parser', from_encoding='utf-8')
        for link in app_soup.find_all('a'):
            href = link.get('href')
            if href and "apps.apple.com" in href and "/app/" in href:
                print(f"Found Apple App Store link: {href}")
                return href
    except requests.exceptions.RequestException as e:
        print(f"Apple App Store search error: {str(e).encode('utf-8', 'replace').decode('utf-8')}")

    print(f"No store link found for: {game_name}")
    return ""
# 새 함수 추가 끝
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_driver():
    """로컬 chromedriver와 스크립트 전용 프로필을 사용하여 Selenium WebDriver를 설정합니다."""
    print("WebDriver 설정 중...")
    chrome_options = Options()
    # chrome_options.add_argument('--headless')  # 브라우저를 보려면 이 줄을 주석 처리
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')

    # 스크립트 전용 크롬 프로필 사용 (메인 브라우저와 충돌 방지)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    selenium_profile_path = os.path.join(script_dir, 'selenium_profile')
    if not os.path.exists(selenium_profile_path):
        os.makedirs(selenium_profile_path)
    print(f"스크립트 전용 크롬 프로필을 사용합니다: {selenium_profile_path}")
    chrome_options.add_argument(f"--user-data-dir={selenium_profile_path}")
    chrome_options.add_argument("--profile-directory=Default") # 이 프로필 내의 기본 사용자

    # Chrome 실행 파일 경로 명시적 지정 (일반적인 설치 경로)
    chrome_binary_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    if not os.path.exists(chrome_binary_path):
        print(f"오류: Chrome 실행 파일이 {chrome_binary_path}에서 발견되지 않았습니다.")
        print("Chrome이 다른 위치에 설치되어 있다면 이 경로를 수정해야 합니다.")
        return None
    chrome_options.binary_location = chrome_binary_path

    chromedriver_path = os.path.join(script_dir, 'chromedriver-win64', 'chromedriver.exe')

    if not os.path.exists(chromedriver_path):
        print(f"오류: {chromedriver_path}에서 chromedriver.exe를 찾을 수 없습니다.")
        return None

    try:
        service = Service(executable_path=chromedriver_path)
        # 드라이버 시작 전 짧은 지연 시간 추가
        time.sleep(2)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("WebDriver 설정 완료.")
        return driver
    except Exception as e:
        print(f"WebDriver 설정 오류: {e}")
        print("오류의 일반적인 원인은 실행 중인 다른 Chrome 창 때문입니다. 모든 Chrome 창을 닫고 다시 시도해 주세요.")
        return None

def get_game_rankings(country_code):
    """Sensor Tower에서 특정 국가의 게임 순위를 스크래핑합니다."""
    date_str = datetime.now().strftime("%Y-%m-%d")
    url = f'https://app.sensortower.com/top-charts?category=6014&country={country_code}&date={date_str}&device=iphone&os=ios'
    print(f"{country_code} 순위 가져오는 중: {url}")

    driver = setup_driver()
    if not driver:
        return {'free': [], 'paid': []}

    try:
        driver.get(url)
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.MuiTableContainer-root table tbody tr"))
        )
        time.sleep(10) # 대기 시간 증가

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        rankings = {'free': [], 'paid': []}
        
        app_rows = soup.select('div.MuiTableContainer-root table tbody tr')

        for idx, row in enumerate(app_rows):
            # 공통 순위 (td:nth-child(1))
            rank_element = row.select_one('td.MuiTableCell-root.MuiTableCell-body.MuiTableCell-sizeMedium.TopChartsInfiniteList-module__rowNumber--bd04e')
            rank = rank_element.text.strip() if rank_element else str(idx + 1)

            # 무료 게임 데이터 추출 (td:nth-child(2))
            free_game_td = row.select_one('td:nth-child(2)')
            if free_game_td:
                name_element = free_game_td.select_one('span > div > div > div[class*="MuiStack-root"] > div > div:nth-child(1)')
                publisher_element = free_game_td.select_one('span > div > div > div[class*="MuiStack-root"] > div > div:nth-child(2)')
                rank_change_element = free_game_td.select_one('div.MuiStack-root.css-dywvnu > a')
                
                icon_element = free_game_td.select_one('a[class*="TopChartsAppCard-module__appIconLink"] > span > img')
                icon_url = icon_element['src'] if icon_element and 'src' in icon_element.attrs else ""
                
                name = name_element.text.strip() if name_element else "N/A"
                publisher = publisher_element.text.strip() if publisher_element else "N/A"
                rank_change = rank_change_element.text.strip() if rank_change_element else ""


                if name != "N/A" and len(rankings['free']) < 10: # 이름이 있고, 무료 게임이 10개 미만일 경우에만 추가
                    official_website_url = search_game_store_link(name) # 게임 링크 검색
                    rankings['free'].append({
                        'rank': rank,
                        'name': name,
                        'publisher': publisher,
                        'rank_change': rank_change,
                        'icon_url': icon_url,
                        'official_website_url': official_website_url
                    })

            # 매출 게임 데이터 추출 (td:nth-child(4))
            paid_game_td = row.select_one('td:nth-child(4)')
            if paid_game_td:
                name_element = paid_game_td.select_one('span > div > div > div[class*="MuiStack-root"] > div > div:nth-child(1)')
                publisher_element = paid_game_td.select_one('span > div > div > div[class*="MuiStack-root"] > div > div:nth-child(2)')
                rank_change_element = paid_game_td.select_one('div.MuiStack-root.css-dywvnu > a')

                icon_element = paid_game_td.select_one('a[class*="TopChartsAppCard-module__appIconLink"] > span > img')
                icon_url = icon_element['src'] if icon_element and 'src' in icon_element.attrs else ""

                name = name_element.text.strip() if name_element else "N/A"
                publisher = publisher_element.text.strip() if publisher_element else "N/A"
                rank_change = rank_change_element.text.strip() if rank_change_element else ""


                if name != "N/A" and len(rankings['paid']) < 10: # 이름이 있고, 매출 게임이 10개 미만일 경우에만 추가
                    official_website_url = search_game_store_link(name) # 게임 링크 검색
                    rankings['paid'].append({
                        'rank': rank,
                        'name': name,
                        'publisher': publisher,
                        'rank_change': rank_change,
                        'icon_url': icon_url,
                        'official_website_url': official_website_url
                    })
            
            # 무료/매출 각각 10개씩 수집되면 중단
            if len(rankings['free']) >= 10 and len(rankings['paid']) >= 10:
                break

        return rankings
    except Exception as e:
        print(f"{country_code} 스크래핑 중 오류 발생: {str(e).encode('utf-8', 'replace').decode('utf-8')}")
        return {'free': [], 'paid': []}
    finally:
        if driver:
            driver.quit()


def format_rankings_for_email(all_rankings):
    """수집된 순위를 이메일용 HTML 문자열로 포맷합니다."""
    country_names = {'KR': '한국', 'CN': '중국', 'JP': '일본'}
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            .rank-up {{ color: green; font-weight: bold; }}
            .rank-down {{ color: red; font-weight: bold; }}
            .rank-no-change {{ color: gray; }}
        </style>
    </head>
    <body>
        <h2>iOS 게임 순위 알림 - {datetime.now().strftime("%Y-%m-%d")}</h2>
    """

    for country_code, ranks in all_rankings.items():
        html_content += f"<h3>--- {country_names.get(country_code, country_code)} 게임 순위 ---</h3>"
        
        # 매출 게임 순위
        html_content += "<h4>매출 게임 순위 (Top 10):</h4>"
        if ranks.get('paid'):
            html_content += "<table><tr><th>순위</th><th>아이콘</th><th>게임명 (개발사)</th><th>변동</th></tr>"
            for game in ranks['paid']:
                translated_name, original_name = translate_game_name(game['name'], country_code)
                original_name_str = f" ({original_name})" if original_name else ""
                rank_change_text = game.get('rank_change', '')
                rank_change_class = "rank-no-change"
                if "↑" in rank_change_text:
                    rank_change_class = "rank-up"
                elif "↓" in rank_change_text:
                    rank_change_class = "rank-down"
                
                game_name_with_link = f"{translated_name}{original_name_str}"
                if game.get('official_website_url'):
                    game_name_with_link = f"<a href=\"{game['official_website_url']}\" target=\"_blank\">{game_name_with_link}</a>"

                html_content += f"<tr><td>{game['rank']}</td><td><img src=\"{game['icon_url']}\" width=\"48\" height=\"48\"></td><td>{game_name_with_link} ({game['publisher']})</td><td class=\"{rank_change_class}\">{rank_change_text}</td></tr>"
            html_content += "</table>"
        else:
            html_content += "<p>데이터 없음</p>"

        # 무료 게임 순위
        html_content += "<h4>무료 게임 순위 (Top 10):</h4>"
        if ranks.get('free'):
            html_content += "<table><tr><th>순위</th><th>아이콘</th><th>게임명 (개발사)</th><th>변동</th></tr>"
            for game in ranks['free']:
                translated_name, original_name = translate_game_name(game['name'], country_code)
                original_name_str = f" ({original_name})" if original_name else ""
                rank_change_text = game.get('rank_change', '')
                rank_change_class = "rank-no-change"
                if "↑" in rank_change_text:
                    rank_change_class = "rank-up"
                elif "↓" in rank_change_text:
                    rank_change_class = "rank-down"

                game_name_with_link = f"{translated_name}{original_name_str}"
                if game.get('official_website_url'):
                    game_name_with_link = f"<a href=\"{game['official_website_url']}\" target=\"_blank\">{game_name_with_link}</a>"

                html_content += f"<tr><td>{game['rank']}</td><td><img src=\"{game['icon_url']}\" width=\"48\" height=\"48\"></td><td>{game_name_with_link} ({game['publisher']})</td><td class=\"{rank_change_class}\">{rank_change_text}</td></tr>"
            html_content += "</table>"
        else:
            html_content += "<p>데이터 없음</p>"

    html_content += "</body></html>"
    return html_content

import win32com.client as win32

def send_outlook_email(content, email_address):
    """로컬 Outlook 애플리케이션을 사용하여 HTML 이메일을 보냅니다."""
    if not email_address:
        print("이메일 주소가 제공되지 않았습니다.")
        return
    try:
        outlook = win32.Dispatch('Outlook.Application')
        mail = outlook.CreateItem(0)
        mail.Subject = f'iOS 게임 순위 알림 - {datetime.now().strftime("%Y-%m-%d")}'
        mail.HTMLBody = content  # HTML 형식으로 변경
        mail.To = email_address
        mail.Send()
        print(f"Outlook 이메일을 {email_address}로 성공적으로 전송했습니다.")
    except Exception as e:
        print(f"Outlook 이메일 전송 실패: {e}")

def main():
    parser = argparse.ArgumentParser(description='Sensor Tower 게임 순위 크롤러')
    parser.add_argument('--email', type=str, required=True, help='결과를 받을 이메일 주소.')
    args = parser.parse_args()

    countries = ['KR', 'CN', 'JP']
    all_rankings = {}
    for country in countries:
        all_rankings[country] = get_game_rankings(country)

    final_content = format_rankings_for_email(all_rankings)

    print("\n--- 최종 리포트 ---")
    report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "game_rank_report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(final_content)
    print(f"리포트가 {report_path}에 저장되었습니다.")

    send_outlook_email(final_content, args.email)

if __name__ == '__main__':
    main()
