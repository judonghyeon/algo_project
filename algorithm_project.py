import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from datetime import datetime
import os
import pandas as pd
from tabulate import tabulate

# [1. 사용자로부터 도시명을 입력 받는 함수]
def get_city_name():
        city_name = input("도시명을 입력하세요(서울시 제외, 뒤로가기: 0 입력): ")
        return city_name
    
# [2. 도시이름으로부터 도시코드를 조회하는 함수]
def get_city_code(city_name):
    city_code = None
    city_type = None
    
    # 도시 유형(광역시, 특별시) 딕셔너리
    city_types = {
        "부산": "광역시",
        "인천": "광역시",
        "대구": "광역시",
        "대전": "광역시",
        "광주": "광역시",
        "울산": "광역시",
        "서울": "특별시",  # 서울은 api가 따로 존재해 구현 불가 (서울시 api를 따로 불러와야함)
        "세종": "특별시"
    }
    
    # 만약 도시 유형 딕셔너리에 입력한 이름이 존재하면 도시 타입을 해당하는 것으로 변경 (ex) 인천 입력시 도시타입 = 광역시
    if city_name in city_types:
        city_type = city_types[city_name]
    else:
        city_type = "시" 

    # 공공데이터 포털의 도시 코드 불러오기 api 링크 (국토교통부 버스 정류소 정보 - [도시코드 목록 조회])
    city_code_url = 'http://apis.data.go.kr/1613000/BusRouteInfoInqireService/getCtyCodeList'
    
    # api에 요청할 요청변수(파라미터)
    city_code_params = {
        'serviceKey': 'NI9pDLpfb3/7YUQsHOwHKHmy0wHB0LruCc/wJ6Zt+qWR5JPnZdavOjSCJ6bOgpCc0LMAOVQETq4XNYxneKyrEg==', # 주동현의 공공데이터 포털 인증키
        '_type': 'xml' # 응답 데이터가 xml 형식으로 되게 설정
    }
    
    try:
        # api 주소에 params 파라미터를 전송, 전송하면 받게되는 응답을 city_code_response 변수에 저장 
        city_code_response = requests.get(city_code_url, params=city_code_params)
        
        #HTTP 요청을 보낼 때 에러 발생 시 에러메세지 출력
        city_code_response.raise_for_status()  
        
        # city_code_soup 변수에 xml 형식으로 응답(response)을 파싱해 저장
        city_code_soup = BeautifulSoup(city_code_response.text, 'xml')

        # 받은 xml 파일에서 item 이라는 태그를 가진 모든것을 추출
        city_elements = city_code_soup.find_all('item')
        
        # 추출한 item 태그를 가진 요소들을 for문으로 하나씩 살펴봄
        for city_element in city_elements:
            # item 태그에서 찾아낸 cityname이 입력한 cityname + citytype이랑 같다면 정확히 찾아낸 것이므로 item 태그에서 찾아낸 citycode를 city_code변수에 저장
            if city_element.find('cityname').text == city_name + city_type: 
                city_code = city_element.find('citycode').text
                break
    
    # 예외 발생시 에러 메세지 출력
    except Exception as e:
        print(f'도시 코드 조회 중 오류가 발생했습니다: {e}')
    
    return city_code, city_type

# [3. 도시코드와 노선번호로 노선의 세부정보를 조회하는 함수]
def get_route_id(city_code, route_number):
    route_id = None     
    
    # 국토교통부 버스노선정보 api [노선번호목록 조회] 이용
    route_id_url = 'http://apis.data.go.kr/1613000/BusRouteInfoInqireService/getRouteNoList'
    
    # api에 요청할 요청변수(파라미터)
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
        
        # route_id_soup에서 <routeid> ~~~ </routeid>로 된 부분을 추출해 변수에 저장
        route_id_element = route_id_soup.find('routeid')
        
        # 추출한 부분이 있을 때 <routeid>, </routeid>를 제거한 텍스트 부분만을 추출해 변수에 저장
        if route_id_element:
            route_id = route_id_element.text
        
    except Exception as e:
        print(f'노선번호 조회 중 오류가 발생했습니다: {e}')
    return route_id

# [4. 도시코드와 노선번호로 노선의 세부정보롤 xml 형식으로 반환하는 함수]
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

# [5. 도시코드, 노선번호로 특정 노선이 지나가는 모든 정류장을 출력, 반환하는 함수]
def print_via_stops(city_code, route_id):
    via_stops_up = []  # 경유 정류장(상행 또는 회차 없는 노선의 정류장)을 저장할 리스트
    via_stops_down = []
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
    
    # 응답 상태 코드가 200(정상)일 때
    if response.status_code == 200:
        data = response.text
        root = ET.fromstring(data)
        prev_stop = None  # 이전 정류장 초기화
        a = 0
        for item in root.iter('item'):
            nodenm_element = item.find('nodenm')
            updowncd_element = item.find('updowncd')
            if nodenm_element is not None:
                current_stop = nodenm_element.text
                updowncd = int(updowncd_element.text) if updowncd_element is not None else None
                a += 1
                # 경유 정류장과 updowncd를 목록에 추가
                if (updowncd is not None) and (updowncd == 0):
                    via_stops_up.append((current_stop, '상행'))
                elif (updowncd is not None) and (updowncd == 1):
                    via_stops_down.append((current_stop, '하행'))
                else:
                    via_stops_up.append((current_stop, 'X'))
                    
        print('----------경유 정류장----------')
        headers = ['정류장', '회차여부']
        if len(via_stops_up) != 0 :
            df_test1 = pd.DataFrame(via_stops_up)
            print(tabulate(df_test1, headers, tablefmt='fancy_grid', showindex=True, stralign='center'))
        if len(via_stops_down) != 0 :
            df_test2 = pd.DataFrame(via_stops_down)
            print(tabulate(df_test2, headers, tablefmt='fancy_grid', showindex=True, stralign='center'))
    else:
        print(f'API 호출 실패 (응답 코드: {response.status_code})')
        print(response.text)  # 오류 응답 데이터 출력
    
    via_stops = []
    via_stops.extend(via_stops_up)
    via_stops.extend(via_stops_down)
    return via_stops  # 경유 정류장 목록 반환

# [6. xml 데이터를 통해 노선 정보를 출력하는 함수]
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

# [7. 도시코드와 정류장번호로 해당 정류장을 지나가는 모든 버스노선 정보를 딕셔너리 리스트로 반환하는 함수]
def get_bus_routes_via_station(city_code, node_id):
    route_list = []
    api_url = 'http://apis.data.go.kr/1613000/BusSttnInfoInqireService/getSttnThrghRouteList'
    params = {
        'serviceKey': 'NI9pDLpfb3/7YUQsHOwHKHmy0wHB0LruCc/wJ6Zt+qWR5JPnZdavOjSCJ6bOgpCc0LMAOVQETq4XNYxneKyrEg==',
        'pageNo': 1,
        'numOfRows': 100,  # 최대한 많은 결과를 받기 위해 값 조정
        '_type': 'xml',
        'cityCode': city_code,
        'nodeid': node_id
    }

    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()  # HTTP 요청 오류가 있을 경우 예외를 발생시킵니다.

        soup = BeautifulSoup(response.text, 'xml')
        route_elements = soup.find_all('item')

        for route in route_elements:
            route_info = {}
            for child in route.find_all():
                route_info[child.name] = child.text.strip()
            route_list.append(route_info)

    except Exception as e:
        print(f'버스 노선 조회 중 오류가 발생했습니다: {e}')

    return route_list

# [보조. 화면 clear 함수]
def clear_screen():
    # 운영체제에 따라 콘솔을 지우는 명령어를 실행
    if os.name == 'nt':  # Windows
        os.system('cls')
    else:  # Linux와 macOS
        os.system('clear')

# [8. 도시코드와 노선번호, 저장할 파일 이름으로 해당 노선이 지나가는 정류장목록을 파일로 만들어 저장하는 함수]
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

# [9. 파일이름으로 해당 파일이 존재할 때 파일 안 정류장 정보를 리스트로 저장해 반환하는 함수]
def load_via_stops(filename):
    via_stops = []
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                stop, updowncd = line.strip().split(', ')
                via_stops.append((stop, updowncd))
    except FileNotFoundError:
        print(f'{filename} 파일을 찾을 수 없습니다.')
        return via_stops
    return via_stops

# [10. 도시코드, 정류장이름으로 정류장id를 반환하는 함수]
def get_station_id(city_code, nodenm):
    url = 'http://apis.data.go.kr/1613000/BusSttnInfoInqireService/getSttnNoList'
    params = {
        'serviceKey': 'NI9pDLpfb3/7YUQsHOwHKHmy0wHB0LruCc/wJ6Zt+qWR5JPnZdavOjSCJ6bOgpCc0LMAOVQETq4XNYxneKyrEg==',
        'pageNo': 1,
        'numOfRows': 100,  # 더 많은 결과를 검색하기 위해 값 조정
        '_type': 'xml',
        'cityCode': city_code,
        'nodeNm': nodenm
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        # Parse the XML response
        root = ET.fromstring(response.content)
        
        # Find the station with the exact same name
        for item in root.iter('item'):
            current_nodenm = item.find('nodenm').text
            if current_nodenm == nodenm:  # Check if the names match exactly
                nodeid = item.find('nodeid').text
                return nodeid  # Return the nodeid of the station with the exact name
        
        # If no exact match is found
        return "정확히 일치하는 정류장을 찾을 수 없습니다."
    else:  
        return "데이터를 받는데 실패했습니다."

# [11-1. 한글 문자를 초성으로 변환해 반환하는 함수]
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

# [11. 한글 문자열을 하나씩 분리해 11-1. 초성으로 반환하는 함수를 호출해서 이를 연결한 것을 반환하는 함수 (초성 문자열 반환)]
def convert_to_initial_sound(station_name):
    return ''.join(get_initial_sound(char) for char in station_name if '가' <= char <= '힣')

# [12. 정류장 이름을 초성으로 입력하여 해당 정류장을 지나가는 노선번호를(파일로 저장한 노선만) 출력하는 함수]
def print_routes_via_station(initial_sound, filenames):
    for filename in filenames:
        # 파일에서 정류장 목록을 불러옴
        via_stops = load_via_stops(filename)
        matched_stops = []  # 일치하는 정류장 정보를 저장할 리스트

        # 파일에서 불러온 각 정류장 이름의 초성을 확인하고, 입력받은 초성에 포함되는 경우 리스트에 추가
        for stop, updowncd in via_stops:
            if initial_sound in convert_to_initial_sound(stop):  # 입력받은 초성이 정류장 이름의 초성에 포함되는 경우
                matched_stops.append((stop, updowncd))
        
        # 일치하는 정류장이 있는 경우에만 파일명(노선번호)과 정류장 정보 출력
        if matched_stops:
            print(f"\n파일명: {filename}")  # 일치하는 정류장이 있을 때만 파일명 출력
            for stop, updowncd in matched_stops:
                if updowncd == '0':
                    print(f'{stop} (노선번호: {filename.split("_")[2].split(".")[0]}): 상행')
                elif updowncd == '1':
                    print(f'{stop} (노선번호: {filename.split("_")[2].split(".")[0]}): 하행')



def display_menu():
    print("                                      [ 버스정보 API를 활용한 버스노선정보 저장 및 로드 프로그램 ]                                             ")
    print("╒══════════════════╤═══════════════════════╤═════════════════════════════╤════════════════════════════════╤═════════════════════════╤═════════╕")
    print("│ 버스정보 조회: 1 │ 찾은 버스정보 저장: 2 │ 저장한 버스정보 불러오기: 3 │ 저장한 정보에서 정류장 찾기: 4 │ 정류장 경유노선 조회: 5 │ 종료: 0 │")
    print("╘══════════════════╧═══════════════════════╧═════════════════════════════╧════════════════════════════════╧═════════════════════════╧═════════╛")

# 메인 함수
def main():
    city_code = None
    route_id = None
    route_number = None


    while True:
        clear_screen()
        display_menu()
        a = input().strip().lower()
        clear_screen()
        display_menu()
        if a == '0':
            print("프로그램을 종료합니다.")
            print("[ 버스정보 API를 활용한 버스노선정보 저장 및 로드 프로그램 ]")
            print("[02조]")
            print("202311388 김민상 \n202311442 주동현 \n202110674 서강찬 \n202311826 홍민기")
            
            break
        elif a == '1':
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
                        print_via_stops(city_code, route_id)
                    else:
                        print(f'{city_name}의 노선번호 {route_number}에 해당하는 정류장 위치를 가져올 수 없습니다.')
                else:
                    print(f'{city_name}의 도시 코드를 가져올 수 없습니다.')
            input("계속하려면 아무 키나 누르세요...")
        elif a == '2':

            if city_code and route_id and route_number:
                filename = f'via_stops_{route_number}.txt'
                save_via_stops(city_code, route_id, filename)
            else:
                print("먼저 노선번호를 조회하세요.")
            input("계속하려면 아무 키나 누르세요...")
        elif a == '3':
            routenumber = input("로드할 노선번호를 입력하세요: ").strip()
            filename = f'via_stops_{routenumber}.txt'  # Ensure the variable name matches
            stops = load_via_stops(filename)
            if not stops:
                print(f'{filename} 파일을 찾을 수 없습니다.')
            else:
                for stop, updowncd in stops:
                    if updowncd == '0':
                        print(f'{stop}, 상행')
                    elif updowncd == '1':
                        print(f'{stop}, 하행')
                    else:  # This part added
                        print(f'{stop}')
            input("계속하려면 아무 키나 누르세요...")
        elif a == '4':
            # 파일명에 via_stops가 포함된 모든 파일 찾기
            filenames = [filename for filename in os.listdir() if 'via_stops' in filename]
            if not filenames:
                print("via_stops를 포함한 파일이 없습니다.")
                return
            while True:
                initial_sound = input("정류장 이름의 초성을 입력하세요 (뒤로가기: 0 입력): ").strip().lower()
                if initial_sound == '0':
                    break
                else:
                    print_routes_via_station(initial_sound, filenames)
            input("계속하려면 아무 키나 누르세요...")

        elif a == '5':
            city_name = input("도시명을 입력하세요(서울시 제외, 뒤로가기: 0 입력): ")
        
            if city_name == '0':
                continue  # 뒤로가기 선택 시, 다시 메뉴로 돌아감
            
            city_code = get_city_code(city_name)

            nodenm = str(input("정류장 이름 : "))
            
            node_id = get_station_id(city_code, nodenm)

            bus_routes = get_bus_routes_via_station(city_code, node_id)

            # 버스 경로 정보를 DataFrame으로 변환하고 열 이름 변경
            df_test = pd.DataFrame(bus_routes, columns=['endnodenm', 'routeid', 'routeno', 'routetp', 'startnodenm'])
            df_test.rename(columns={
                'endnodenm': '종점',
                'routeid': '노선아이디',
                'routeno': '노선번호',
                'routetp': '노선유형',
                'startnodenm': '기점'
            }, inplace=True)
            
            print(tabulate(df_test, headers='keys', tablefmt='fancy_grid', showindex=True))
            
            input("계속하려면 아무 키나 누르세요...")
        else:
            print("올바른 선택이 아닙니다. 다시 시도하세요.")

        
if __name__ == "__main__":
    main()