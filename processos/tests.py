from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Cliente, Prazo, Processo, classificar_alerta
from .painel import montar_painel


class ClassificarAlertaTests(TestCase):
    def test_limites(self):
        casos = {
            -1: "VENCIDO",
            0: "VERMELHO",
            3: "VERMELHO",
            4: "AMARELO",
            7: "AMARELO",
            8: "VERDE",
            30: "VERDE",
        }
        for dias, esperado in casos.items():
            self.assertEqual(classificar_alerta(dias), esperado, f"dias={dias}")

    def test_cumprido_ignora_data(self):
        self.assertEqual(classificar_alerta(-10, cumprido=True), "CUMPRIDO")
        self.assertEqual(classificar_alerta(2, cumprido=True), "CUMPRIDO")


class PrazoTests(TestCase):
    def setUp(self):
        cliente = Cliente.objects.create(nome="Teste")
        self.processo = Processo.objects.create(
            numero_processo="0001234-56.2026.8.26.0100",
            vara_comarca="1ª Vara Cível",
            assunto="Teste",
            cliente=cliente,
        )

    def test_dias_restantes_e_alerta(self):
        hoje = date(2026, 11, 1)
        p = Prazo.objects.create(
            processo=self.processo, descricao="Contestação",
            data_vencimento=date(2026, 11, 4),
        )
        self.assertEqual(p.dias_restantes(hoje), 3)
        self.assertEqual(p.nivel_alerta(hoje), "VERMELHO")

    def test_prazo_cumprido(self):
        p = Prazo.objects.create(
            processo=self.processo, descricao="Recurso",
            data_vencimento=date(2026, 11, 2), status=Prazo.Status.CUMPRIDO,
        )
        self.assertEqual(p.nivel_alerta(date(2026, 11, 1)), "CUMPRIDO")

    def test_excluir_processo_exclui_prazos(self):
        Prazo.objects.create(
            processo=self.processo, descricao="X", data_vencimento=date(2026, 12, 1)
        )
        self.processo.delete()
        self.assertEqual(Prazo.objects.count(), 0)


# ---------------------------------------------------------------------------
# Prova: painel de prazos
# ---------------------------------------------------------------------------


class PainelTests(TestCase):
    def setUp(self):
        self.hoje = date(2026, 11, 20)
        ana = Cliente.objects.create(nome="Ana")
        bia = Cliente.objects.create(nome="Bia")
        p1 = Processo.objects.create(numero_processo="1", vara_comarca="V", assunto="A", cliente=ana)
        p2 = Processo.objects.create(numero_processo="2", vara_comarca="V", assunto="B", cliente=bia)
        p3 = Processo.objects.create(numero_processo="3", vara_comarca="V", assunto="C")

        def prazo(proc, dias, status="PENDENTE"):
            Prazo.objects.create(
                processo=proc, descricao=f"d{dias}",
                data_vencimento=self.hoje + timedelta(days=dias), status=status,
            )

        prazo(p1, -2)   # vencido
        prazo(p1, 2)    # vermelho
        prazo(p2, 5)    # amarelo
        prazo(p2, 30)   # verde
        prazo(p3, 1)    # vermelho, sem cliente
        prazo(p1, 1, status="CUMPRIDO")  # cumprido

    def test_contagem_por_nivel(self):
        c = montar_painel(self.hoje)["contagem"]
        self.assertEqual(c["VENCIDO"], 1)
        self.assertEqual(c["VERMELHO"], 2)
        self.assertEqual(c["AMARELO"], 1)
        self.assertEqual(c["VERDE"], 1)
        self.assertEqual(c["CUMPRIDO"], 1)

    def test_totais(self):
        dados = montar_painel(self.hoje)
        self.assertEqual(dados["total"], 6)
        self.assertEqual(dados["total_pendentes"], 5)

    def test_por_cliente_ignora_cumpridos_e_agrupa_sem_cliente(self):
        nomes = {c["cliente"]: c for c in montar_painel(self.hoje)["clientes"]}
        self.assertEqual(nomes["Ana"]["pendentes"], 2)
        self.assertEqual(nomes["Ana"]["criticos"], 2)
        self.assertEqual(nomes["Bia"]["pendentes"], 2)
        self.assertEqual(nomes["Bia"]["criticos"], 0)
        self.assertEqual(nomes["Sem cliente"]["pendentes"], 1)

    def test_proximos_ordenados_por_vencimento(self):
        datas = [x["prazo"].data_vencimento for x in montar_painel(self.hoje)["proximos"]]
        self.assertEqual(datas, sorted(datas))

    def test_view_exige_login_de_staff(self):
        resp = self.client.get(reverse("painel"))
        self.assertEqual(resp.status_code, 302)

    def test_view_responde_para_staff(self):
        User = get_user_model()
        User.objects.create_superuser("admin", "a@a.com", "x")
        self.client.login(username="admin", password="x")
        resp = self.client.get(reverse("painel"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Painel de prazos")
