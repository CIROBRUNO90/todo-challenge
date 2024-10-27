from django.contrib import admin
from django.urls import path

from users.urls import urlpatterns as users_urls
from tasks.urls import urlpatterns as tasks_urls

urlpatterns = [
    path('admin/', admin.site.urls),
]

urlpatterns += users_urls
urlpatterns += tasks_urls
