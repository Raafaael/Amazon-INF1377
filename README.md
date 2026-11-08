# Projeto Amazon — INF1377

Base local de um comércio eletrônico acadêmico. Nesta etapa, o projeto contém apenas a estrutura inicial do Django, páginas provisórias e autenticação padrão. Catálogo e carrinho ainda serão implementados pelos integrantes responsáveis.

## Requisitos

- Python 3.10 ou mais recente e `pip` (testado com Python 3.13).
- Navegador moderno.
- Não é necessário instalar MySQL nem Docker para esta etapa.

O banco configurado atualmente é **SQLite**, em `db.sqlite3`, apenas para desenvolvimento local. O uso de MySQL continua como proposta do grupo, sem decisão final. A interface futura usará Django Templates e poderá usar Bootstrap; nenhuma dependência de interface é necessária agora.

## Instalação e execução

Execute os comandos na pasta do repositório.

### Windows (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Se a política do PowerShell impedir a ativação, use diretamente `.\.venv\Scripts\python.exe` no lugar de `python` nos comandos posteriores.

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Criar o administrador e acessar a aplicação

As instruções desta seção valem **tanto para Windows quanto para Linux/macOS**. O comando `python manage.py createsuperuser`, incluído nos dois exemplos acima, cria uma conta de administrador no banco local. Quando ele pedir os dados, você pode informar **`admin`** como nome de usuário, deixar o e-mail vazio (pressione Enter) e escolher uma senha para esse ambiente. A senha não aparece enquanto é digitada. O projeto não inclui uma conta pronta; evite reutilizar uma senha pessoal.

Depois de executar `python manage.py runserver`, abra:

- <http://127.0.0.1:8000/> — página inicial provisória;
- <http://127.0.0.1:8000/admin/> — Administração do Django; entre com o superusuário criado acima;
- <http://127.0.0.1:8000/accounts/login/> — tela de login padrão, ainda sem layout definitivo; a conta criada acima também pode entrar aqui e será redirecionada à página inicial;
- <http://127.0.0.1:8000/carrinho/> — página provisória do app `cart`.

Para verificar a configuração sem iniciar o servidor, execute `python manage.py check`. Para encerrar o servidor, pressione `Ctrl+C`.

## Configuração local

O projeto usa `DEBUG=True` e uma chave pública de desenvolvimento como valor padrão de `DJANGO_SECRET_KEY`. Essa configuração serve somente para execução local. Caso queira fornecer uma chave própria nesta sessão do PowerShell, execute `$env:DJANGO_SECRET_KEY = 'sua-chave-local'` antes de iniciar o servidor; no Linux/macOS, use `export DJANGO_SECRET_KEY='sua-chave-local'`. Não registre chaves reais no repositório.

Os diretórios `templates/` e `static/` já estão configurados para as próximas etapas. O arquivo `db.sqlite3`, o ambiente `.venv` e arquivos gerados são ignorados pelo Git. Não há produtos, operações de carrinho nem telas definitivas nesta entrega da T01.
