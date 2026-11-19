from django.contrib import admin
from django.urls import path

from processos.views import painel

urlpatterns = [
    path('admin/painel/', admin.site.admin_view(painel), name='painel'),
    path('admin/', admin.site.urls),
]
