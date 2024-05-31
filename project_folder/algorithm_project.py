import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from datetime import datetime
import os
# 사용자로부터 도시명 입력 받기
def get_city_name():
        city_name = input("도시명을 입력하세요(서울시 제외, 뒤로가기: ㅂ 입력): ")
        return city_name
# 도시 코드 조회 함수
def get_city_code(city_name):
    city_code = None
    city_type = None
    # 도시 유형 딕셔너리를 만듭니다.
    city_types = {
        "부산": "광역시",
        "인천": "광역시",
        "대구": "광역시",
        "대전": "광역시",
        "광주": "광역시",
        "울산": "광역시",
        "서울": "특별시",  #없음
        "세종": "특별시"
    }
    if city_name in city_types:
        city_type = city_types[city_name]
    else:
        city_type = "시"

    city_code_url = 'http://apis.data.go.kr/1613000/BusRouteInfoInqireService/getCtyCodeList' # 공공데이터 포털의 도시 코드 불러오기 api 링크
    city_code_params = {
        'serviceKey': 'NI9pDLpfb3/7YUQsHOwHKHmy0wHB0LruCc/wJ6Zt+qWR5JPnZdavOjSCJ6bOgpCc0LMAOVQETq4XNYxneKyrEg==', # 나(주동현)의 공공데이터 포털 키 <- 이거로 사용함 
        '_type': 'xml'
    }
    try:
        city_code_response = requests.get(city_code_url, params=city_code_params) # api요청을 보냄 
        city_code_response.raise_for_status()  # HTTP 오류가 발생한 경우 예외 발생
        city_code_soup = BeautifulSoup(city_code_response.text, 'xml') # xml로 보낸 파일을 추출

        city_elements = city_code_soup.find_all('item') # 받은 xml 파일에서 item 이라는 태그를 가진 모든것을 추출
        for city_element in city_elements:
            if city_element.find('cityname').text == city_name + city_type: # 광역시/특별시, 일반 시 구분하는 코드
                city_code = city_element.find('citycode').text # 도시 코드 xml에서 찾아서 city_code에 넣어줌 
                break
    except Exception as e:
        print(f'도시 코드 조회 중 오류가 발생했습니다: {e}')
    return city_code, city_type

# 노선번호 조회 함수
def get_route_id(city_code, route_number):
    route_id = None
    route_id_url = 'http://apis.data.go.kr/1613000/BusRouteInfoInqireService/getRouteNoList'
    route_id_params = {
        'serviceKey': 'NI9pDLpfb3/7YUQsHOwHKHmy0wHB0LruCc/wJ6Zt+qWR5JPnZdavOjSCJ6bOgpCc0LMAOVQETq4XNYxneKyrEg==',
        '_type': 'xml',
        'cityCode': city_code,
        'routeNo': route_number
    }
    try:
        route_id_response = requests.get(route_id_url, params=route_id_params)
        route_id_response.raise_for_status()  # HTTP 오류가 발생한 경우 예외 발생
        route_id_soup = BeautifulSoup(route_id_response.text, 'xml')
        route_id_element = route_id_soup.find('routeid')
        if route_id_element:
            route_id = route_id_element.text
    except Exception as e:
        print(f'노선번호 조회 중 오류가 발생했습니다: {e}')
    return route_id

def get_route_info(city_code, route_id):
    url = 'http://apis.data.go.kr/1613000/BusRouteInfoInqireService/getRouteInfoIem'
    params = {
        'serviceKey': 'NI9pDLpfb3/7YUQsHOwHKHmy0wHB0LruCc/wJ6Zt+qWR5JPnZdavOjSCJ6bOgpCc0LMAOVQETq4XNYxneKyrEg==',
        '_type': 'xml', 
        'cityCode': city_code, 
        'routeId': route_id
    }
    response = requests.get(url, params=params)
    soup = BeautifulSoup(response.text, 'xml')
    return soup

# 노선번호 조회 함수
def get_route_id(city_code, route_number):
    route_id = None
    route_id_url = 'http://apis.data.go.kr/1613000/BusRouteInfoInqireService/getRouteNoList'
    route_id_params = {
        'serviceKey': 'NI9pDLpfb3/7YUQsHOwHKHmy0wHB0LruCc/wJ6Zt+qWR5JPnZdavOjSCJ6bOgpCc0LMAOVQETq4XNYxneKyrEg==',
        '_type': 'xml',
        'cityCode': city_code,
        'routeNo': route_number
    }
    try:
        route_id_response = requests.get(route_id_url, params=route_id_params)
        route_id_response.raise_for_status()  # HTTP 오류가 발생한 경우 예외 발생
        route_id_soup = BeautifulSoup(route_id_response.text, 'xml')
        route_id_element = route_id_soup.find('routeid')
        if route_id_element:
            route_id = route_id_element.text
    except Exception as e:
        print(f'노선번호 조회 중 오류가 발생했습니다: {e}')
    return route_id
def get_route_info(city_code, route_id):
    url = 'http://apis.data.go.kr/1613000/BusRouteInfoInqireService/getRouteInfoIem'
    params = {
        'serviceKey': 'NI9pDLpfb3/7YUQsHOwHKHmy0wHB0LruCc/wJ6Zt+qWR5JPnZdavOjSCJ6bOgpCc0LMAOVQETq4XNYxneKyrEg==',
        '_type': 'xml', 
        'cityCode': city_code, 
        'routeId': route_id
    }
    response = requests.get(url, params=params)
    soup = BeautifulSoup(response.text, 'xml')
    return soup
# 경유 정류장 목록을 반환하는 함수
def print_via_stops(city_code, route_id):
    via_stops = []  # 경유 정류장을 저장할 리스트
    params = {
        'serviceKey': 'NI9pDLpfb3/7YUQsHOwHKHmy0wHB0LruCc/wJ6Zt+qWR5JPnZdavOjSCJ6bOgpCc0LMAOVQETq4XNYxneKyrEg==',
        'numOfRows': 800,
        'pageNo': 1,
        '_type': 'xml',
        'cityCode': city_code,  # 도시 코드 설정
        'routeId': route_id  # 노선 ID 설정
    }
    base_url = 'http://apis.data.go.kr/1613000/BusRouteInfoInqireService/getRouteAcctoThrghSttnList'
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        data = response.text
        root = ET.fromstring(data)
        prev_stop = None  # 이전 정류장 초기화
        a = 0
        print('----------경유 정류장----------')
        for item in root.iter('item'):
            nodenm_element = item.find('nodenm')
            updowncd_element = item.find('updowncd')
            if nodenm_element is not None:
                current_stop = nodenm_element.text
                updowncd = int(updowncd_element.text) if updowncd_element is not None else None
                
                if prev_stop == current_stop:  # 이전 정류장과 현재 정류장이 같은지 확인
                    print('----------회차----------')
                    print(current_stop)
                else:
                    a += 1
                    via_stops.append((current_stop, updowncd))  # 경유 정류장과 updowncd를 목록에 추가
                    if updowncd is not None:
                        print(f"{a}. {current_stop} (updowncd: {updowncd})")  # 현재 정류장과 updowncd 출력
                    else:
                        print(f"{a}. {current_stop}")  # 현재 정류장 출력
                prev_stop = current_stop  # 현재 정류장을 이전 정류장으로 업데이트
        print('----------경유 정류장----------')
    else:
        print(f'API 호출 실패 (응답 코드: {response.status_code})')
        print(response.text)  # 오류 응답 데이터 출력
    
    return via_stops  # 경유 정류장 목록 반환

# 노선 정보 조회 함수
def print_route_info(soup):
    bus_route_element = soup.find('routeno')
    starting_point_element = soup.find('startnodenm')
    ending_point_element = soup.find('endnodenm')
    route_type_element = soup.find('routetp')
    first_bus_start = soup.find('startvehicletime')
    last_bus_end = soup.find('endvehicletime')
    if bus_route_element:
        bus_route = bus_route_element.text
        print(f'버스 노선: {bus_route}')
    else:
        print('버스 노선 정보를 찾을 수 없습니다.')
    if starting_point_element:
        starting_point = starting_point_element.text
        print(f'기점: {starting_point}')
    else:
        print('기점 정보를 찾을 수 없습니다.')
    if ending_point_element:
        ending_point = ending_point_element.text
        print(f'종점: {ending_point}')
    else:
        print('종점 정보를 찾을 수 없습니다.')
    if route_type_element:
        route_type = route_type_element.text
        print(f'노선 유형: {route_type}')
    else:
        print('노선 유형 정보를 찾을 수 없습니다.')
    if first_bus_start:
        first_bus_start_time = first_bus_start.text
        first_bus_start_time = datetime.strptime(first_bus_start_time, '%H%M').strftime('%I:%M %p')
        print(f'첫차 시간: {first_bus_start_time}')
    else:
        print('첫차 시간 정보를 찾을 수 없습니다.')
    if last_bus_end:
        last_bus_end_time = last_bus_end.text
        last_bus_end_time = datetime.strptime(last_bus_end_time, '%H%M').strftime('%I:%M %p')
        print(f'막차 시간: {last_bus_end_time}')
    else:
        print('막차 시간 정보를 찾을 수 없습니다.')

def clear_screen():
    # 운영체제에 따라 콘솔을 지우는 명령어를 실행
    if os.name == 'nt':  # Windows
        os.system('cls')
    else:  # Linux와 macOS
        os.system('clear')

def save_via_stops(city_code, route_id, filename):
    via_stops = []  # 경유 정류장 저장
    params = {
        'serviceKey': 'NI9pDLpfb3/7YUQsHOwHKHmy0wHB0LruCc/wJ6Zt+qWR5JPnZdavOjSCJ6bOgpCc0LMAOVQETq4XNYxneKyrEg==',
        'numOfRows': 800,
        'pageNo': 1,
        '_type': 'xml',
        'cityCode': city_code,  # 도시 코드 설정
        'routeId': route_id  # 노선 ID 설정
    }
    base_url = 'http://apis.data.go.kr/1613000/BusRouteInfoInqireService/getRouteAcctoThrghSttnList'
    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.text
        root = ET.fromstring(data)
        for item in root.iter('item'):
            nodenm_element = item.find('nodenm')
            updowncd_element = item.find('updowncd')
            if nodenm_element is not None:
                current_stop = nodenm_element.text
                updowncd = int(updowncd_element.text) if updowncd_element is not None else None
                via_stops.append((current_stop, updowncd))

        # 파일로 저장
        with open(filename, 'w', encoding='utf-8') as file:
            for stop, updowncd in via_stops:
                file.write(f'{stop}, {updowncd}\n')
        print(f'경유 정류장 정보가 {filename}에 저장되었습니다.')
    else:
        print(f'API 호출 실패 (응답 코드: {response.status_code})')
        print(response.text)


def load_via_stops(filename):
    via_stops = []
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            stop, updowncd = line.strip().split(', ')
            via_stops.append((stop, updowncd))
    return via_stops

def get_initial_sound(char):
    # 한글 유니코드 범위
    base_code, initial_code, final_code = 44032, 588, 28
    # 초성 리스트
    initial_list = [
        'ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ'
    ]
    # 초성이 아닌 경우에는 빈 문자열 반환
    if '가' <= char <= '힣':
        # 한글 유니코드로 변환
        code = ord(char) - base_code
        # 초성 인덱스 계산
        initial_index = code // initial_code
        return initial_list[initial_index]
    else:
        return ''

def convert_to_initial_sound(station_name):
    return ''.join(get_initial_sound(char) for char in station_name if '가' <= char <= '힣')

# 정류장 이름을 초성으로 입력하여 해당 정류장을 경유하는 노선 출력하는 함수
def print_routes_via_station(initial_sound, filenames):
    for filename in filenames:
        via_stops = load_via_stops(filename)
        matched_stops = []  # 일치하는 정류장 정보를 저장할 리스트

        # 파일에서 불러온 각 정류장 이름의 초성을 확인하고, 입력받은 초성과 완벽히 일치할 경우 리스트에 추가
        for stop, updowncd in via_stops:
            if initial_sound == convert_to_initial_sound(stop):  # 입력받은 초성과 정류장 이름의 초성이 완벽히 일치하는 경우
                matched_stops.append((stop, updowncd))
        
        # 일치하는 정류장이 있는 경우에만 파일명과 정류장 정보 출력
        if matched_stops:
            print(f"\n파일명: {filename}")  # 일치하는 정류장이 있을 때만 파일명 출력
            for stop, updowncd in matched_stops:
                print(f'{stop} (노선번호: {filename.split("_")[2].split(".")[0]}): {updowncd}')



# 메인 함수
def main():
    city_code = None
    route_id = None
    route_number = None

    while True:
        a = input("노선번호 조회: ㄹ, 찾은 노선 저장하기: ㄴ, 찾은 노선 불러오기: ㅣ, 노선번호 찾기: ㄷ, 종료: ㅂ\n").strip().lower()
        
        if a == 'ㅂ':
            print("프로그램을 종료합니다.")
            break
        elif a == 'ㄹ':
            city_name = get_city_name()
            if city_name:
                city_code, city_type = get_city_code(city_name)
                if city_code:
                    route_number = input("노선번호를 입력하세요: ").strip()
                    route_id = get_route_id(city_code, route_number)
                    if route_id:
                        route_info = get_route_info(city_code, route_id)
                        print('버스 아이디:', route_id)
                        print_route_info(route_info)
                        via_stops = print_via_stops(city_code, route_id)
                    else:
                        print(f'{city_name}의 노선번호 {route_number}에 해당하는 정류장 위치를 가져올 수 없습니다.')
                else:
                    print(f'{city_name}의 도시 코드를 가져올 수 없습니다.')
        elif a == 'ㄴ':
            if city_code and route_id and route_number:
                filename = f'via_stops_{route_number}.txt'
                save_via_stops(city_code, route_id, filename)
            else:
                print("먼저 노선번호를 조회하세요.")
        elif a == 'ㅣ':
            route_number = input("로드할 노선번호를 입력하세요: ").strip()
            filename = f'via_stops_{route_number}.txt'
            try:
                stops = load_via_stops(filename)
                for stop, updowncd in stops:
                    print(f'{stop}, {updowncd}')
            except FileNotFoundError:
                print(f'{filename} 파일을 찾을 수 없습니다.')
        elif a == 'ㄷ':
            # 파일명에 via_stops가 포함된 모든 파일 찾기
            filenames = [filename for filename in os.listdir() if 'via_stops' in filename]
            if not filenames:
                print("via_stops를 포함한 파일이 없습니다.")
                return
            while True:
                initial_sound = input("정류장 이름의 초성을 입력하세요 (뒤로가기: ㅂ 입력): ").strip().lower()
                if initial_sound == 'ㅂ':
                    print("프로그램을 종료합니다.")
                    break
                else:
                    print_routes_via_station(initial_sound, filenames)
        else:
            print("올바른 선택이 아닙니다. 다시 시도하세요.")

if __name__ == "__main__":
    main()