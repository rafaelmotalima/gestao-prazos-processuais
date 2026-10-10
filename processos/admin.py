from django.contrib import admin

from .models import Cliente, Processo


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nome", "cpf_cnpj", "telefone", "email")
    search_fields = ("nome", "cpf_cnpj", "email")


@admin.register(Processo)
class ProcessoAdmin(admin.ModelAdmin):
    list_display = (
        "numero_processo",
        "cliente",
        "vara_comarca",
        "status",
        "criado_em",
    )
    list_filter = ("status", "vara_comarca")
    search_fields = ("numero_processo", "cliente__nome", "assunto")
    autocomplete_fields = ("cliente",)
    ordering = ("-criado_em",)