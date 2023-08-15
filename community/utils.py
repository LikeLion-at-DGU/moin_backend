from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os

@csrf_exempt
def upload_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        community_id = request.POST.get('id')
        community_path = os.path.join('community', community_id)

        # 이미지 확장자 확인
        image_extension = image.name.split('.')[-1].lower()
        if image_extension not in ['jpg', 'jpeg', 'png']:
            return JsonResponse({'error': 'Unsupported image format.'}, status=400)

        # 커뮤니티 폴더 내 이미지 파일 개수 확인
        try:
            existing_images = [filename for filename in os.listdir(community_path) if filename.lower().endswith(('.jpg', '.jpeg', '.png'))]
            next_image_number = len(existing_images) + 1
            image_name = f"{next_image_number}.{image_extension}"  # 새 이미지 파일 이름

        except FileNotFoundError:
            # 커뮤니티 폴더가 없는 경우 디렉토리 생성
            os.makedirs(community_path)
            image_name = f"1.{image_extension}"  # 새 이미지 파일 이름

        # 이미지 저장 경로 생성
        image_path = os.path.join(community_path, image_name)

        # 이미지 저장
        with open(image_path, 'wb') as f:
            for chunk in image.chunks():
                f.write(chunk)

        image_url = '/' + image_path  # 이미지 URL

        return JsonResponse({'image_url': image_url})

    return JsonResponse({'error': 'Image upload failed.'}, status=400)