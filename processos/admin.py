from django.contrib import admin
from django.utils.html import format_html

from .models import Cliente, Prazo, Processo

# Página inicial do admin com o atalho para o painel de prazos (Prova)
admin.site.index_template = "processos/admin_index.html"

CORES_ALERTA = {
    "VENCIDO": ("#7f1d1d", "Vencido"),
    "VERMELHO": ("#c0392b", "Urgente"),
    "AMARELO": ("#d4a017", "Atenção"),
    "VERDE": ("#2e8b57", "No prazo"),
    "CUMPRIDO": ("#6b7280", "Cumprido"),
}


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nome", "cpf_cnpj", "telefone", "email")
    search_fields = ("nome", "cpf_cnpj", "email")


class PrazoInline(admin.TabularInline):
    model = Prazo
    extra = 0


@admin.register(Processo)
class ProcessoAdmin(admin.ModelAdmin):
    list_display = ("numero_processo", "cliente", "vara_comarca", "status", "criado_em")
    list_filter = ("status", "vara_comarca")
    search_fields = ("numero_processo", "cliente__nome", "assunto")
    autocomplete_fields = ("cliente",)
    ordering = ("-criado_em",)
    inlines = [PrazoInline]


@admin.register(Prazo)
class PrazoAdmin(admin.ModelAdmin):
    list_display = (
        "descricao",
        "processo",
        "data_vencimento",
        "dias_restantes_col",
        "alerta",
        "status",
    )
    list_filter = ("status",)
    search_fields = ("descricao", "processo__numero_processo", "processo__cliente__nome")
    autocomplete_fields = ("processo",)
    ordering = ("data_vencimento",)

    @admin.display(description="Dias restantes")
    def dias_restantes_col(self, obj):
        return obj.dias_restantes()

    @admin.display(description="Alerta")
    def alerta(self, obj):
        cor, texto = CORES_ALERTA[obj.nivel_alerta()]
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 10px;'
            'border-radius:10px;font-weight:bold;">{}</span>',
            cor,
            texto,
        )
