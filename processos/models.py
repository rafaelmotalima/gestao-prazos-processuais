from django.db import models


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
    """
    Entrega C2: o campo cliente agora é um relacionamento (FK) com o
    modelo Cliente, no lugar do texto livre da C1.
    """

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