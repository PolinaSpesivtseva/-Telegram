from rest_framework.views import APIView
# from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import Group

class CheckAuthView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        return JsonResponse({
            "detail": "authenticated",
            "pro_version": request.user.groups.filter(name='CanUseChatGPT').exists()
        })