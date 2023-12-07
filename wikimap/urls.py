from django.urls import path
from .views import *
from . import views

app_name='wikimap'#무조건 있어야 식별 가능

urlpatterns = [
    path('', wiki_home, name='wiki_home'),
    path('index/', wiki_index, name='wiki_index'),
    path('city_info/', wikipedia_city_info, name='wikipedia_city_info'),
    path('google_map/', google_map, name='google_map'),
    path('wiki_result/', wiki_result, name='wiki_result'),
    path('login/', login, name='login'),
    path('signup/',views.signup,name='signup'),
    path('', views.index, name='index'),  # 'index'라는 이름의 URL 패턴 추가
]