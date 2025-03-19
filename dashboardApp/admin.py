from django.contrib import admin
from .models import UserDataSource, WorkHour, lecture, UploadedCSV, UserToken

# Register your models here.
admin.site.register(lecture)
admin.site.register(UserDataSource)
admin.site.register(WorkHour)
admin.site.register(UploadedCSV)
admin.site.register(UserToken)
