# Projeto Amazon — INF1377

Base local de um comércio eletrônico acadêmico. O projeto contém catálogo de livros e eletrônicos, cadastro pelo Django Admin, busca, filtros, carrinho e checkout em etapas com endereços, frete fictício, pagamento simulado e consulta de pedidos. A avaliação humana da integração do checkout está pendente.

## Requisitos

- Python 3.10 ou mais recente e `pip` (testado com Python 3.13).
- Navegador moderno.
- Não é necessário instalar MySQL nem Docker para esta etapa.

O banco configurado atualmente é **SQLite**, em `db.sqlite3`, apenas para desenvolvimento local. O uso de MySQL continua como proposta do grupo, sem decisão final. A interface usa Django Templates e Bootstrap via CDN; é necessário acesso à rede para carregar o CSS e JavaScript do Bootstrap.

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

- <http://127.0.0.1:8000/> — catálogo;
- <http://127.0.0.1:8000/admin/> — Administração do Django; entre com o superusuário criado acima;
- <http://127.0.0.1:8000/accounts/login/> — tela de login; a conta criada acima também pode entrar aqui e será redirecionada à página inicial;
- <http://127.0.0.1:8000/carrinho/> — carrinho do usuário autenticado.
- <http://127.0.0.1:8000/pedidos/> — histórico de pedidos do usuário autenticado.

Para preencher um **banco local de demonstração vazio**, depois de `migrate` você pode executar `python manage.py loaddata catalogo_demo`. A fixture inclui livros, eletrônicos e categorias. Ela usa identificadores fixos e **pode sobrescrever registros com os mesmos IDs**; não a recarregue sobre dados que queira preservar. Também é possível cadastrar produtos pelo Admin, nas seções **Livros** e **Eletrônicos**.

Para verificar a configuração sem iniciar o servidor, execute `python manage.py check`. Para encerrar o servidor, pressione `Ctrl+C`.

## Configuração local

O projeto usa `DEBUG=True` e uma chave pública de desenvolvimento como valor padrão de `DJANGO_SECRET_KEY`. Essa configuração serve somente para execução local. Caso queira fornecer uma chave própria nesta sessão do PowerShell, execute `$env:DJANGO_SECRET_KEY = 'sua-chave-local'` antes de iniciar o servidor; no Linux/macOS, use `export DJANGO_SECRET_KEY='sua-chave-local'`. Não registre chaves reais no repositório.

Os diretórios `templates/` e `static/` estão configurados. O arquivo `db.sqlite3`, o ambiente `.venv` e arquivos gerados são ignorados pelo Git. Os módulos de pedidos, endereços, frete e pagamento são integrados pelo checkout da Semana 2.

### Checkout da Semana 2

Após instalar as dependências e executar `python manage.py migrate`, entre na
aplicação, adicione produtos disponíveis ao carrinho e clique em **Finalizar
compra**. O fluxo passa por **Endereço → Entrega → Pagamento → Confirmação**.
O cadastro de endereço retorna ao checkout. Depois de revisar o resumo e
confirmar os dados, escolha cartão fictício ou PIX simulado.

Para demonstrar aprovação, use o cartão fictício `4242 4242 4242 4242`; para
recusa, `4111 1111 1111 1111`, com nome fictício, validade futura e CVV fictício
de três dígitos. O PIX só é aprovado pela ação **Simular pagamento PIX**; gerar
o QR não confirma a compra. Nenhuma modalidade realiza cobrança real.

O pedido mantém os valores confirmados e não é duplicado por reenvio. O carrinho
e o estoque só são ajustados após aprovação; recusa e PIX pendente preservam
os itens. Novos produtos e quantidades adicionais no carrinho são preservados.
O contrato, as decisões de integração e o roteiro completo estão em
[`checkout/CONTRATO.md`](checkout/CONTRATO.md). Os testes específicos usam
`python manage.py test checkout`.

### Demonstração de pedidos antes do checkout

Depois de migrar o banco e criar uma conta local, entre na aplicação e adicione um produto ao carrinho. Em outro terminal, na raiz do projeto, execute `python manage.py criar_pedido_demo NOME_DO_USUARIO`. O comando registra um pedido fictício e informa seu número. Reexecutar sem opções devolve o **mesmo** pedido, sem duplicá-lo; para criar **outro** pedido com os itens atuais do carrinho, execute `python manage.py criar_pedido_demo NOME_DO_USUARIO --novo`. Abra `/pedidos/` autenticado com essa conta para ver a lista, os detalhes, os valores e o primeiro evento do histórico. O pedido permanece **aguardando pagamento**; a demonstração não cobra, não baixa estoque e não limpa o carrinho. O contrato de integração está em `orders/CONTRATO.md`.

Para verificar a implementação, execute `python manage.py check` e `python manage.py test orders`. A suíte completa usa `python manage.py test`.
