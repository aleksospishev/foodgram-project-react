from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

app_name = 'foodgram'

""" взяты из api_final!!!!
необходимо доработать """

urlpatterns = [
    # path('auth/', include('users.urls')),
    # path('auth/', include('django.contrib.auth.urls')),
#     path('admin/', admin.site.urls),
#     path('api/v1/', include('api.urls')),
#     path('redoc/',
#          TemplateView.as_view(template_name='redoc.html'),
#          name='redoc'),
]