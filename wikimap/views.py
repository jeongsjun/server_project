from django.shortcuts import render, redirect
from django.template import loader
from django.http import HttpResponse
from .models import CityInfo
from bs4 import BeautifulSoup
import wikipediaapi
import requests
from django.contrib import messages
import json
from geopy.geocoders import Nominatim
import re
from .models import User_Table
from django.http import JsonResponse
import sqlite3
import os

def wiki_home(request):
    return render(request, 'wikimap/base.html')

def home_page(request):
    return render(request, 'wikimap/base2.html')

def wiki_index(request):
    return render(request, 'wikimap/index.html')

def convert_address_to_region(address):
    address = address.rsplit(' ', 1)[0]  # 마지막 공백을 기준으로 문자열을 분리하고 첫 번째 부분을 선택
    address_list = address.split(' ')  # 나머지 부분을 띄어쓰기 기준으로 분리하여 리스트에 저장
    address_list = reversed(address_list)
    return address_list


def get_client_ip(request):  # 클라이언트 ip주소 반환
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def clean_location(location):
    # Check if the location ends with a number
    if location[-1].isdigit():
        # Remove the trailing number
        location = location.rsplit(' ', 1)[0]

    return location.strip()


def wikipedia_city_info(request):
    if request.method == 'POST':
        wiki = wikipediaapi.Wikipedia(
            language='ko',
            extract_format=wikipediaapi.ExtractFormat.WIKI,
            user_agent="Your_User_Agent_String_Here"
        )

        locations_input = request.POST.get('search-box', '')
        locations = locations_input.split(',')

        city_info_list = []

        for location_input in locations:
            location_input = location_input.strip()
            location = clean_location(location_input)

            # If the location is still not defined, skip to the next one
            if not location:
                continue

            page = wiki.page(location)

            if page.exists():
                city_info = {
                    'title': page.title,
                    'summary': page.summary,
                    'url': page.fullurl,
                }
                city_info_list.append(city_info)
            else:
                city_info_list.append({
                    'title': location,
                    'exists': False,
                    'text_content': f"The page for '{location}' does not exist on Korean Wikipedia."
                })

        return render(request, 'wikimap/result.html', {'city_info_list': city_info_list})

    else:
        return HttpResponse("Invalid request method.")


def google_map(request):
    return render(request, 'wikimap/NewFile.html')


def wiki_result(request):
    context = {}
    cities_input = request.POST.get('city', '')

    if cities_input:
        cities = convert_address_to_region(cities_input)  # 주소를 해당 지역으로 변환

        wiki = wikipediaapi.Wikipedia(
            language='ko',
            extract_format=wikipediaapi.ExtractFormat.WIKI,
            user_agent="Your_User_Agent_String_Here"
        )

        city_info_list = []

        for city in cities:
            try:
                page = wiki.page(city)
                if page.exists():
                    city_info = {
                        'title': page.title,
                        'summary': page.summary,
                        'url': page.fullurl,
                    }
                    city_info_list.append(city_info)
                    break  # 페이지가 존재하면 반복문을 중단합니다.
            except Exception as e:
                continue  # 에러가 발생하면 다음 도시로 넘어갑니다.

        context['city_info_list'] = city_info_list
    else:
        messages.error(request, '검색어를 작성하세요.')
        return redirect('wikimap:wiki_home')

    context['message'] = 'success'
    return HttpResponse(json.dumps(context), content_type="application/json")

def piechart(request):
    context = {}
    conn = sqlite3.connect(r'citydata.sqlite3')
    cursor = conn.cursor()

    cities_input = request.POST.get('city', '')
    print(cities_input)
    cities = convert_address_to_region(cities_input)        # 역순으로 cities를 가져옴
    print(cities)
    for city in cities:
        print(city)

        # db에 해당 city가 있는지 확인, 있다면 해당 구역과 구역이 가지고있는 cities 출력
        result = retable(city)
        if result is not None:
            break
    print(result)
    #예외처리. result가 None이라면.. chart를 그리지 않고 경고문 띄우기
    region = result[0]
    cities = result[1]


    formatted_cities = ','.join("'" + city + "'" for city in cities)
    query = f"SELECT city, population, extent FROM city_data WHERE city IN ({formatted_cities})"
    cursor.execute(query)
    data = cursor.fetchall()

    population_extent_data = [{'city': row[0], 'population': row[1], 'extent': row[2]} for row in data]

    # print(population_extent_data)
    population_extent_data = population_extent_data

    context['population_extent_data'] = population_extent_data
    context['message'] = 'success'
    return HttpResponse(json.dumps(context), content_type="application/json")
    json_string = json.dumps({'population_extent_data': population_extent_data})

    # JSON 문자열을 HttpResponse 객체에 넣어 반환
    # return HttpResponse(json_string, content_type="application/json")


    # return JsonResponse({'population_extent_data': population_extent_data})
    request.population_extent_data = population_extent_data
    print('ss')
    # print(request)
    # print(type(request))
    return request
    context = {'population_extent_data': population_extent_data}
    # return context
    # return HttpResponse(context, content_type="application/json")
    # return JsonResponse(context)
    # return HttpResponse(json.dumps(context), content_type="application/json")


def retable(city_name):

    dictionary = {}

    dictionary['main_cities'] = ["서울특별시", "부산광역시", "대구광역시", "인천광역시", "광주광역시", "대전광역시", "울산광역시", "세종특별자치시", "경기도", "강원특별자치도", "충청북도",  "충청남도", "전라북도", "전라남도", "경상북도", "경상남도", "제주특별자치도"]

    dictionary['경기도'] = ["가평군", "고양시", "과천시", "광명시", "광주시_(경기도)", "구리시", "군포시", "김포시", "남양주시", "동두천시", "부천시", "성남시", "수원시", "시흥시", "안산시", "안성시", "안양시", "양주시", "양평군", "여주시", "오산시", "용인시", "의왕시", "의정부시", "이천시", "파주시", "평택시", "포천시", "하남시", "화성시"]

    dictionary['서울특별시'] = ["강남구", "강동구", "강북구", "강서구_(서울특별시)", "관악구", "광진구", "구로구", "금천구", "노원구", "도봉구", "동대문구", "동작구", "마포구", "서대문구", "서초구", "성동구", "성북구", "송파구", "양천구", "영등포구", "용산구", "은평구", "종로구", "중구_(서울특별시)", "중랑구"]

    dictionary['강원도'] = ["강릉시", "고성군", "동해시", "삼척시", "속초시", "양구군", "양양군", "영월군", "원주시", "인제군",  "정선군", "철원군", "춘천시", "태백시", "평창군", "홍천군", "화천군", "횡성군"]

    dictionary['인천광역시'] = ["강화군", "계양구", "남동구", "동구_(인천광역시)", "미추홀구", "부평구", "서구_(인천광역시)", "연수구"]

    dictionary['충청북도'] = ["청주시", "충주시", "제천시", "보은군", "옥천군", "영동군", "증평군", "진천군", "괴산군", "음성군", "단양군"]

    dictionary['충청남도'] = ["천안시", "공주시", "보령시", "아산시", "서산시", "논산시", "계룡시", "당진시", "금산군", "부여군", "서천군", "청양군", " 홍성군", "예산군", "태안군"]

    dictionary['전라북도'] = ["전주시", "군산시", "익산시", "정읍시", "남원시", "김제시", "완주군", "진안군", "무주군", "장수군", "임실군", "순창군", "고창군 ", "부안군"]

    dictionary['전라남도'] = ["목포시", "여수시", "순천시_(전라남도)", "나주시", "광양시", "담양군", "곡성군", "구례군", "고흥군", "보성군", "화순군", "장흥군", "강진군", "해남군", "영암군", "무안군", "함평군", "영광군_(전라남도)", "장성군", "완도군", "진도군", "신안군"]

    dictionary['경상북도'] = ["경산시", "경주시", "고령군", "구미시", "군위군", "김천시", "문경시", "봉화군", "상주시", "성주군", "안동시", "영덕군", "영양군 ", "영주시", "영천시", "예천군", "울릉군", "울진군", "의성군", "청도군", "청송군", "칠곡군", "포항시"]

    dictionary['경상남도'] = ["거제시", "거창군", "고성군", "김해시", "남해군", "밀양시", "사천시", "산청군", "양산시", "의령군", "진주시", "창녕군", "창원시 ", "통영시", "하동군", "함안군", "함양군", "합천군"]

    dictionary['부산광역시'] = ["강서구_(부산광역시)", "금정구", "기장군", "남구_(부산광역시)", "동구", "동래구", "부산진구", "북구_(부산광역시)", "사상구", "사하구", "서구", "수영구", "연제구 ", "영도구", "중구", "해운대구"]

    dictionary['제주특별자치도'] = ["서귀포시", "제주시"]

    for region, city_names in dictionary.items():
        for city_name_example in city_names:
            if city_name in city_name_example:
                return region, city_names

    return None



def login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Check if the user exists in the database
        try:
            user = User_Table.objects.get(username=username)
        except User_Table.DoesNotExist:
            return JsonResponse({'success': False, 'message': '아이디가 없습니다.'})

        # Check if the password is correct
        if user.password == password:
            # 로그인 성공
            return JsonResponse({'success': True})
        else:
            # 비밀번호가 틀림
            return JsonResponse({'success': False, 'message': '비밀번호가 틀립니다.'})
    else:
        # GET 메서드로 요청이 들어온 경우 로그인 페이지를 렌더링
        if request.method == "GET":
            return render(request, 'wikimap/login.html')
        else:
            # 잘못된 HTTP 메서드
            return JsonResponse({'success': False, 'message': '잘못된 요청입니다.'})


def signup(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        name = data.get('name')
        username = data.get('username')
        password = data.get('password')
        passwordck = data.get('passwordck')
        birthdate = data.get('birthdate')

        # 입력 필드가 빈 경우에 대한 처리
        if not (name and username and password and passwordck and birthdate):
            return HttpResponse('모든 필드를 입력해주세요.', status=400)

        # 패스워드 확인
        if password != passwordck:
            return HttpResponse('패스워드가 일치하지 않습니다.', status=400)

        # 동일한 사용자 이름이 이미 있는지 확인
        if User_Table.objects.filter(username=username).exists():
            return HttpResponse('이미 존재하는 사용자 이름입니다.', status=400)

        # 모든 검사를 통과한 경우 데이터베이스에 저장
        user_table = User_Table(name=name, username=username, password=password, birthdate=birthdate)
        user_table.save()

    return render(request, 'wikimap/signup.html')


def signup(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        name = data.get('name')
        username = data.get('username')
        password = data.get('password')
        passwordck = data.get('passwordck')
        birthdate = data.get('birthdate')

        # 입력 필드가 빈 경우에 대한 처리
        if not (name and username and password and passwordck and birthdate):
            return HttpResponse('모든 필드를 입력해주세요.', status=400)

        # 패스워드 확인
        if password != passwordck:
            return HttpResponse('패스워드가 일치하지 않습니다.', status=400)

        # 동일한 사용자 이름이 이미 있는지 확인
        if User_Table.objects.filter(username=username).exists():
            return HttpResponse('이미 존재하는 사용자 이름입니다.', status=400)

        # 모든 검사를 통과한 경우 데이터베이스에 저장
        user_table = User_Table(name=name, username=username, password=password, birthdate=birthdate)
        user_table.save()

    return render(request, 'wikimap/signup.html')


def chart(request):
    context = piechart(request)
    print(context)

    # return render(request, 'wikimap/signup.html')
    return render(context, 'wikimap/piechart.html')
    return render(request, 'wikimap/piechart.html', context)
    # return render(request, 'wikimap/empty..html')