from datetime import date

from django.test import TestCase

from .models import Cliente, Prazo, Processo, classificar_alerta


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
