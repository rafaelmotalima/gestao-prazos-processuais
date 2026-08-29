from django.db import models


class Processo(models.Model):
    """
    Entrega C1: cadastro de processos.
    O campo `cliente_nome` e texto livre por enquanto — na C2 ele vira um
    relacionamento (FK) com o modelo Cliente, para mostrar no video o
    "antes e depois" (texto livre -> relacionado).
    """

    class Status(models.TextChoices):
        ATIVO = "ATIVO", "Ativo"
        SUSPENSO = "SUSPENSO", "Suspenso"
        ARQUIVADO = "ARQUIVADO", "Arquivado"

    numero_processo = models.CharField(
        "Numero do processo", max_length=30, unique=True
    )
    vara_comarca = models.CharField("Vara / comarca", max_length=120)
    assunto = models.CharField("Assunto", max_length=200)
    cliente_nome = models.CharField(
        "Cliente (texto livre por enquanto)", max_length=150
    )
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.ATIVO
    )
    criado_em = models.DateTimeField("Criado em", auto_now_add=True)
    atualizado_em = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        verbose_name = "Processo"
        verbose_name_plural = "Processos"
        ordering = ["-criado_em"]

    def __str__(self):
        return f"{self.numero_processo} — {self.cliente_nome}"
