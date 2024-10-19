from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from chatRoom.models import Discussion
from chatRoom.serializers import discussionSerializer


# Create your views here.
class showDiscussion(APIView):
    def get(self, request,course_id):
        try:
            discussion = Discussion.objects.filter(cno_id=course_id)
            ser = discussionSerializer(discussion, many=True)
            return Response({"code":200,"data":ser.data})
        except Discussion.DoesNotExist:
            return Response({'error':'课程未找到'},status=status.HTTP_404_NOT_FOUND)


