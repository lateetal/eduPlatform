import os
import oss2
from django.test import TestCase

class MyTestCase(TestCase):
    def setUp(self):
        # 这里配置 OSS 的认证信息
        self.accessKeyId = 'LTAI5tAtNfQg5VqN22gT3Tsn'
        self.accessKeySecret = 'Mqha28ubnHLtRlZaaDhXiqz6O9Xnwf'
        self.auth = oss2.Auth(self.accessKeyId, self.accessKeySecret)
        self.endpoint = 'http://oss-cn-beijing.aliyuncs.com'
        self.bucketName = 'edu-platform-2024'
        self.bucket = oss2.Bucket(self.auth, self.endpoint, self.bucketName)

    def test_upload_image(self):
        print("in")
        with open("./cute.png", 'rb') as fileobj:
            # Seek方法用于指定从第1000个字节位置开始读写。上传时会从您指定的第1000个字节位置开始上传，直到文件结束。
            fileobj.seek(0, os.SEEK_SET)
            # Tell方法用于返回当前位置。
            current = fileobj.tell()
            # 填写Object完整路径。Object完整路径中不能包含Bucket名称。
            self.bucket.put_object('course/pic/testupload.png', fileobj)