from django.urls import path

from time_table import views

app_name = 'time_table'

urlpatterns = [
    path('', views.setting, name='setting'),
    path('add_face', views.add_face, name="add_face"),
    path('camera', views.detectme, name='camera'),
]
