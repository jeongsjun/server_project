from django.shortcuts import render, redirect
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


def wiki_home(request):
    return render(request, 'wikimap/base.html')


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


def index(request):
    return HttpResponse("Hello, world!")
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

def index(request):
    return HttpResponse("Hello, world!")