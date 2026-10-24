from datetime import date

from django.db import models
from django.utils import timezone


class Cliente(models.Model):
    nome = models.CharField("Nome", max_length=150)
    cpf_cnpj = models.CharField("CPF/CNPJ", max_length=20, blank=True)
    telefone = models.CharField("Telefone", max_length=20, blank=True)
    email = models.EmailField("E-mail", blank=True)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Processo(models.Model):
    class Status(models.TextChoices):
        ATIVO = "ATIVO", "Ativo"
        SUSPENSO = "SUSPENSO", "Suspenso"
        ARQUIVADO = "ARQUIVADO", "Arquivado"

    numero_processo = models.CharField("Número do processo", max_length=30, unique=True)
    vara_comarca = models.CharField("Vara / comarca", max_length=120)
    assunto = models.CharField("Assunto", max_length=200)
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="processos",
        verbose_name="Cliente",
    )
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ATIVO)
    criado_em = models.DateTimeField("Criado em", auto_now_add=True)
    atualizado_em = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        verbose_name = "Processo"
        verbose_name_plural = "Processos"
        ordering = ["-criado_em"]

    def __str__(self):
        cliente_nome = self.cliente.nome if self.cliente else "sem cliente"
        return f"{self.numero_processo} — {cliente_nome}"


# ---------------------------------------------------------------------------
# AC3: prazos com alerta de vencimento
# ---------------------------------------------------------------------------

LIMITE_VERMELHO = 3  # até 3 dias restantes
LIMITE_AMARELO = 7   # até 7 dias restantes


def classificar_alerta(dias_restantes, cumprido=False):
    """
    Regra de negócio do alerta (separada do modelo para ser fácil de testar):
      - prazo cumprido            -> "CUMPRIDO"
      - já passou do vencimento   -> "VENCIDO"
      - 3 dias ou menos           -> "VERMELHO"
      - de 4 a 7 dias             -> "AMARELO"
      - mais de 7 dias            -> "VERDE"
    """
    if cumprido:
        return "CUMPRIDO"
    if dias_restantes < 0:
        return "VENCIDO"
    if dias_restantes <= LIMITE_VERMELHO:
        return "VERMELHO"
    if dias_restantes <= LIMITE_AMARELO:
        return "AMARELO"
    return "VERDE"


class Prazo(models.Model):
    class Status(models.TextChoices):
        PENDENTE = "PENDENTE", "Pendente"
        CUMPRIDO = "CUMPRIDO", "Cumprido"

    processo = models.ForeignKey(
        Processo,
        on_delete=models.CASCADE,
        related_name="prazos",
        verbose_name="Processo",
    )
    descricao = models.CharField("Descrição", max_length=200)
    data_vencimento = models.DateField("Data de vencimento")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDENTE)
    criado_em = models.DateTimeField("Criado em", auto_now_add=True)

    class Meta:
        verbose_name = "Prazo"
        verbose_name_plural = "Prazos"
        ordering = ["data_vencimento"]

    def __str__(self):
        return f"{self.descricao} ({self.data_vencimento:%d/%m/%Y})"

    def dias_restantes(self, hoje=None):
        hoje = hoje or timezone.localdate()
        return (self.data_vencimento - hoje).days

    def nivel_alerta(self, hoje=None):
        return classificar_alerta(
            self.dias_restantes(hoje),
            cumprido=(self.status == self.Status.CUMPRIDO),
        )
