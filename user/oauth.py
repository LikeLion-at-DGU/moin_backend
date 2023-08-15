import requests
import os

from json import JSONDecodeError

from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.google import views as google_view
from allauth.socialaccount.providers.kakao import views as kakao_view
from allauth.socialaccount.models import SocialAccount

from django.utils import timezone
from django.shortcuts import redirect
from django.contrib.auth import login
from django.http import JsonResponse
from .models import *

# 구글 소셜로그인 변수 설정
# 도메인 설정 필요
state = os.environ.get("STATE")
BASE_URL = 'https://moin.dcs-hyungjoon.com/'
GOOGLE_CALLBACK_URI = BASE_URL + 'api/v1/auth/google/login/callback/'
KAKAO_CALLBACK_URI = BASE_URL + 'api/v1/auth/kakao/login/callback/'

# 구글 로그인
def google_login(request):
    scope = "https://www.googleapis.com/auth/userinfo.email"
    client_id = os.environ.get("SOCIAL_AUTH_GOOGLE_CLIENT_ID")
    return redirect(f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&response_type=code&redirect_uri={GOOGLE_CALLBACK_URI}&scope={scope}")

def google_callback(request):
    client_id = os.environ.get("SOCIAL_AUTH_GOOGLE_CLIENT_ID")
    client_secret = os.environ.get("SOCIAL_AUTH_GOOGLE_SECRET")
    code = request.GET.get('code')

    # 1. 받은 코드로 구글에 access token 요청
    token_req = requests.post(f"https://oauth2.googleapis.com/token?client_id={client_id}&client_secret={client_secret}&code={code}&grant_type=authorization_code&redirect_uri={GOOGLE_CALLBACK_URI}&state={state}")
    
    token_req_json = token_req.json()
    error = token_req_json.get("error")

    if error is not None:
        raise JSONDecodeError(error)

    access_token = token_req_json.get('access_token')

    # 2. 가져온 access_token으로 이메일값을 구글에 요청
    email_req = requests.get(f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}")
    email_req_status = email_req.status_code

    if email_req_status != 200:
        return JsonResponse({'err_msg': 'failed to get email'}, status=status.HTTP_400_BAD_REQUEST)
    
    email_req_json = email_req.json()
    email = email_req_json.get('email')

    # 3. 전달받은 이메일, access_token, code를 바탕으로 회원가입/로그인
    try:
        # 전달받은 이메일로 등록된 유저가 있는지 탐색
        user = User.objects.get(email=email)

        # FK로 연결되어 있는 socialaccount 테이블에서 해당 이메일의 유저가 있는지 확인
        social_user = SocialAccount.objects.get(user=user)

        # 있는데 구글계정이 아닐때
        if social_user.provider != 'google':
            return JsonResponse({'err_msg': 'no matching social type'}, status=status.HTTP_400_BAD_REQUEST)

        data = {'access_token': access_token, 'code': code}
        accept = requests.post(f"{BASE_URL}api/v1/auth/google/login/finish/", data=data)
        accept_status = accept.status_code

        # 뭔가 중간에 문제가 생기면 에러
        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signin'}, status=accept_status)

        accept_json = accept.json()
        accept_json.pop('user', None)

    except User.DoesNotExist:
        # 전달받은 이메일로 기존에 가입된 유저가 아예 없으면 => 새로 회원가입 & 해당 유저의 jwt 발급
        data = {'access_token': access_token, 'code': code}
        accept = requests.post(f"{BASE_URL}api/v1/auth/google/login/finish/", data=data)
        accept_status = accept.status_code

        if accept_status != 200:
            return JsonResponse({'err_msg': 'failed to signup'}, status=accept_status)
        
        uid = email_req_json.get('user_id')
        nickname = 'google_' + str(uid)
        user = User.objects.get(email=email)
        user.nickname = nickname
        user.save()

    except SocialAccount.DoesNotExist:
        # User는 있는데 SocialAccount가 없을 때 (=일반회원으로 가입된 이메일일때)
        return JsonResponse({'err_msg': 'email exists but not social user'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = User.objects.get(email=email)
    
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    login(request, user)

    res = {
        "detail": "로그인 성공!",
        "access": access_token,
        "refresh": str(refresh),
    }
    return JsonResponse(res)
    


class GoogleLogin(SocialLoginView):
    adapter_class = google_view.GoogleOAuth2Adapter
    callback_url = GOOGLE_CALLBACK_URI
    client_class = OAuth2Client


#Kakao
def kakao_login(request):
    client_id = os.environ.get("SOCIAL_AUTH_KAKAO_CLIENT_ID")
    return redirect(f"https://kauth.kakao.com/oauth/authorize?client_id={client_id}&redirect_uri={KAKAO_CALLBACK_URI}&response_type=code&scope=account_email")

def kakao_callback(request):
    client_id = os.environ.get("SOCIAL_AUTH_KAKAO_CLIENT_ID")
    code = request.GET.get("code")

    # code로 access token 요청
    token_request = requests.get(f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={client_id}&redirect_uri={KAKAO_CALLBACK_URI}&code={code}")
    token_response_json = token_request.json()

    # 에러 발생 시 중단
    error = token_response_json.get("error", None)
    if error is not None:
        raise JSONDecodeError(error)

    access_token = token_response_json.get("access_token")

    # access token으로 카카오톡 프로필 요청
    profile_request = requests.post(
        "https://kapi.kakao.com/v2/user/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    profile_json = profile_request.json()
    
    error = profile_json.get("error")
    if error is not None:
        raise JSONDecodeError(error)
    
    kakao_account = profile_json.get("kakao_account")
    email = kakao_account.get("email", None) 
    nickname = kakao_account.get("nickname", None)

    # 이메일 없으면 오류 => 카카오톡 최신 버전에서는 이메일 없이 가입 가능해서 추후 수정해야함
    if email is None:
        return JsonResponse({'err_msg': 'failed to get email'}, status=status.HTTP_400_BAD_REQUEST)
    
    uid = profile_json.get("id")

    try:
        user = User.objects.get(email=email)
        social_user = SocialAccount.objects.get(user=user)

        if social_user.provider != "kakao":
            return JsonResponse(
                {"err_msg": "no matching social type"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        data = {"access_token": access_token, "code": code}
        accept = requests.post(f"{BASE_URL}api/v1/auth/kakao/login/finish/", data=data)
        accept_status = accept.status_code

        if accept_status != 200:
            return JsonResponse({"err_msg": "failed to signin"}, status=accept_status)
        
    except User.DoesNotExist: 
        try:
            user = User.objects.create(email=email,nickname=nickname)
        except:
            nickname = "kakao_" + str(uid)
            user = User.objects.create(email=email,nickname=nickname)

        SocialAccount.objects.create(
            user=user,
            uid=uid,
            extra_data=profile_json,
            date_joined=profile_json.get("connected_at"),
            last_login=timezone.now(),
            provider="kakao",
        )
    except SocialAccount.DoesNotExist:
        return JsonResponse(
            {"err_msg": "user exists but not social user"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    user = User.objects.get(email=email)
    login(request, user)

    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    response_data = {
        "message": "Login Susccess",
        "access_token": access_token,
        "refresh_token": str(refresh),
    }
    response = JsonResponse(response_data)
    return response

class KakaoLogin(SocialLoginView):
    adapter_class = kakao_view.KakaoOAuth2Adapter
    callback_url = KAKAO_CALLBACK_URI
    client_class = OAuth2Client