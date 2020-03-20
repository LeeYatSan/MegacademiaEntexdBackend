from django.db import models

# Create your models here.


class SharingFileInfo(models.Model):
    class Meta:
        db_table = 'sharing_file_info'
    file_name = models.CharField(max_length=50)
    file_md5 = models.CharField(max_length=40)
    file_path = models.CharField(max_length=100)
    uploader_id = models.IntegerField()
    uploaded_time = models.DateTimeField(auto_now_add=True)