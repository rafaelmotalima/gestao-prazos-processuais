from django.contrib import admin

from .models import Processo


@admin.register(Processo)
class ProcessoAdmin(admin.ModelAdmin):
    list_display = (
        "numero_processo",
        "cliente_nome",
        "vara_comarca",
        "status",
        "criado_em",
    )
    list_filter = ("status", "vara_comarca")
    search_fields = ("numero_processo", "cliente_nome", "assunto")
    ordering = ("-criado_em",)
