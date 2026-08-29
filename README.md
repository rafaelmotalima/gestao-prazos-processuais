# Gestão de Prazos Processuais

Projeto da disciplina *Software Product* — 202602 EAD ADS 5A.

Stack: **Django + PostgreSQL**, usando o admin do Django como front-end
das telas de cadastro (é uma UI real, integrada a front+back+banco — não
é Postman/Swagger).

## Escopo desta entrega (C1)

CRUD completo de `Processo`. O campo cliente ainda é texto livre
(`cliente_nome`); na C2 ele vira um relacionamento com um novo modelo
`Cliente`, para mostrar no vídeo o "antes e depois".

## Como rodar

1. Subir o banco (Postgres via Docker):
   ```bash
   docker compose up -d
   ```

2. Criar e ativar um ambiente virtual:
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```

3. Instalar dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Copiar o arquivo de variáveis de ambiente:
   ```bash
   cp .env.example .env
   ```
   (o projeto já usa os mesmos valores como padrão, então isso é opcional
   em dev — mas é bom já deixar o hábito para quando for hospedar)

5. Rodar as migrações:
   ```bash
   python manage.py migrate
   ```

6. Criar um usuário para acessar o admin:
   ```bash
   python manage.py createsuperuser
   ```

7. Subir o servidor:
   ```bash
   python manage.py runserver
   ```

8. Acessar `http://localhost:8000/admin/` e logar — lá já dá pra
   cadastrar, editar, listar e excluir processos.

## Para o vídeo da C1

1. Mostrar o board e dizer que a funcionalidade é o cadastro de processos.
2. Cadastrar um processo pelo admin (`/admin/processos/processo/add/`).
3. Mostrar ele aparecendo na listagem.
4. Fechar confirmando no banco: `python manage.py dbshell` e depois
   `SELECT * FROM processos_processo;`

## Roadmap (ver cronograma completo)

- **C2**: modelo `Cliente` + FK em `Processo` (substitui `cliente_nome`)
- **C3**: modelo `Prazo` vinculado a `Processo`, com lógica de alerta
  (vermelho ≤3 dias, amarelo ≤7, verde o resto)
- **Prova**: dashboard agregando prazos por urgência/cliente + diagramas
  de casos de uso e de classes
