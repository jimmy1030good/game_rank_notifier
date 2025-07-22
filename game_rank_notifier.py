import os
import time
import argparse
from datetime import datetime
from bs4 import BeautifulSoup
from google.cloud import translate_v2 as translate

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
    # Try Google Play Store first
    play_query = f"{game_name} Google Play Store"
    play_results = default_api.google_web_search(query=play_query)
    play_link = ""
    if play_results and play_results.get('search_results'):
        for result in play_results['search_results']:
            if "play.google.com" in result.get('link', ''):
                play_link = result['link']
                print(f"Found Google Play link: {play_link}")
                return play_link

    # If not found, try Apple App Store
    app_query = f"{game_name} Apple App Store"
    app_results = default_api.google_web_search(query=app_query)
    app_link = ""
    if app_results and app_results.get('search_results'):
        for result in app_results['search_results']:
            if "apps.apple.com" in result.get('link', ''):
                app_link = result['link']
                print(f"Found Apple App Store link: {app_link}")
                return app_link
    print(f"No store link found for: {game_name}")
    return ""
# 새 함수 추가 끝
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
        print(f"{country_code} 스크래핑 중 오류 발생: {e}")
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

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email_smtp(content, recipient_email, sender_email, sender_password, smtp_server, smtp_port):
    """SMTP를 사용하여 HTML 이메일을 보냅니다."""
    if not recipient_email or not sender_email or not sender_password:
        print("이메일 발송에 필요한 정보(수신자, 발신자, 비밀번호)가 부족합니다.")
        return

    try:
        msg = MIMEMultipart("alternative")
        msg['Subject'] = f'iOS 게임 순위 알림 - {datetime.now().strftime("%Y-%m-%d")}'
        msg['From'] = sender_email
        msg['To'] = recipient_email

        part1 = MIMEText(content, 'html')
        msg.attach(part1)

        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        print(f"SMTP 이메일을 {recipient_email}로 성공적으로 전송했습니다.")
    except Exception as e:
        print(f"SMTP 이메일 전송 실패: {e}")

def main():
    parser = argparse.ArgumentParser(description='Sensor Tower 게임 순위 크롤러')
    parser.add_argument('--email', type=str, required=True, help='결과를 받을 이메일 주소.')
    parser.add_argument('--sender_email', type=str, required=True, help='발신자 이메일 주소.')
    parser.add_argument('--sender_password', type=str, required=True, help='발신자 이메일 비밀번호 (또는 앱 비밀번호).')
    parser.add_argument('--smtp_server', type=str, default='smtp.gmail.com', help='SMTP 서버 주소.')
    parser.add_argument('--smtp_port', type=int, default=465, help='SMTP 서버 포트.')
    args = parser.parse_args()

    countries = ['KR', 'CN', 'JP']
    all_rankings = {}
    for country in countries:
        all_rankings[country] = get_game_rankings(country)

    final_content = format_rankings_for_email(all_rankings)

    print("\n--- 최종 리포트 ---")
    # Save the report to a file to avoid terminal encoding issues
    report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "game_rank_report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(final_content)
    print(f"리포트가 {report_path}에 저장되었습니다.")

    send_email_smtp(final_content, args.email, args.sender_email, args.sender_password, args.smtp_server, args.smtp_port)

if __name__ == '__main__':
    main()
