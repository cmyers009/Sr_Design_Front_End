from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="UI"),
    path('depth_stream', views.depth_stream, name='depth_stream'),
    path('rgb_stream',views.rgb_stream,name="rgb_stream"),
    

]