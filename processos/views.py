from django.contrib import admin
from django.shortcuts import render

from .painel import montar_painel


def painel(request):
    """Painel de prazos (Prova). Registrado via admin.site.admin_view, então exige login de staff."""
    contexto = {
        **admin.site.each_context(request),
        "title": "Painel de prazos",
        "painel": montar_painel(),
    }
    return render(request, "processos/painel.html", contexto)
