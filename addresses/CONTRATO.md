# Contrato do app `addresses` (T07 — Rafael, Semana 2)

Este documento é para quem vai **usar** os endereços: Davi (T10, checkout) e Breno (T06, pedidos). O código está em [`models.py`](models.py), [`forms.py`](forms.py), [`viacep.py`](viacep.py) e [`views.py`](views.py).

Referências: UC06, RN-09 a RN-11, `context.md` §7.4 e §8.3.

## Model `Endereco`

| Campo | Observação |
|---|---|
| `usuario` | dono do endereço (`request.user`); `user.enderecos.all()` |
| `cep` | sempre gravado como `00000-000` (`normalizar_cep()` em [`cep.py`](cep.py)) |
| `logradouro`, `numero`, `complemento`, `bairro`, `cidade`, `estado` | `numero` obrigatório (texto, aceita "120A"); `complemento` opcional; `estado` é UF (`Endereco.UF`) |
| `tipo` | `Endereco.Tipo.CASA` ou `Endereco.Tipo.TRABALHO` (enum do UML) |
| `padrao` | no máximo **um** padrão por usuário (RN-09) |

### Como usar

```python
from addresses.models import Endereco

Endereco.do_usuario(request.user)          # endereços do usuário, padrão primeiro
Endereco.padrao_do_usuario(request.user)   # padrão ou None
Endereco.obter_do_usuario(request.user, endereco_id)  # levanta Endereco.DoesNotExist se não for dele

endereco.texto_formatado      # "Rua X, 10 - Apto 2 — Bairro, Cidade/UF — CEP 00000-000"
endereco.dados_para_pedido()  # dict: cep, logradouro, numero, complemento, bairro, cidade, estado, tipo
```

- **Nunca** busque um endereço só pelo id que veio do formulário: use `obter_do_usuario`, `SelecaoEnderecoForm` ou `get_object_or_404(Endereco, pk=..., usuario=request.user)`.
- **Pedido (Breno):** copie `endereco.dados_para_pedido()` para os campos do pedido no momento da compra. Uma FK sozinha não basta, porque o cliente pode editar ou excluir o endereço depois, e o pedido histórico não pode mudar (TODO §2.1, acordo 4).

## Seleção no checkout (Davi)

```python
from addresses.forms import SelecaoEnderecoForm

form = SelecaoEnderecoForm(request.user, data=request.POST or None)
if form.is_valid():
    endereco = form.cleaned_data['endereco']   # sempre do próprio usuário
```

- O formulário lista só os endereços do usuário, já com o padrão marcado. Um id de outro usuário é rejeitado como escolha inválida.
- O partial `templates/addresses/_selecao.html` renderiza a lista de rádios e o link "Cadastrar novo endereço". Inclua-o **dentro** do `<form method="post">` do checkout:

```django
{% include 'addresses/_selecao.html' with form=form_endereco next_url=request.get_full_path %}
```

- Cadastro com retorno ao checkout: `{% url 'addresses:novo' %}?next=<url do checkout>`. O `next` é preservado no POST, após erro de validação e no botão Cancelar. URLs externas são descartadas.

## Rotas

| Nome | URL | Método |
|---|---|---|
| `addresses:lista` | `/enderecos/` | GET — página **Meus endereços** |
| `addresses:novo` | `/enderecos/novo/` | GET/POST (aceita `?next=`) |
| `addresses:editar` | `/enderecos/<id>/editar/` | GET/POST |
| `addresses:excluir` | `/enderecos/<id>/excluir/` | POST |
| `addresses:tornar_padrao` | `/enderecos/<id>/padrao/` | POST |
| `addresses:consultar_cep` | `/enderecos/cep/<cep>/` | GET — JSON para o formulário |

Todas exigem login. Endereço de outro usuário → 404.

## ViaCEP

`addresses.viacep.consultar_cep(cep)` devolve `ResultadoCep` (`cep`, `logradouro`, `bairro`, `cidade` ← `localidade`, `estado` ← `uf`, `campos_faltando`). Possíveis erros:

| Exceção | Resposta JSON | Quando |
|---|---|---|
| `CepInvalido` | 400 | formato inválido (não acessa a rede) |
| `CepNaoEncontrado` | 404 | ViaCEP devolve `erro: true` |
| `ServicoCepIndisponivel` | 503 | sem conexão, timeout (5 s), HTTP de erro ou resposta não JSON |

No formulário, um CEP **não encontrado ou inválido limpa** logradouro, bairro, cidade e UF, como no exemplo oficial do ViaCEP, para não misturar dados de outro CEP. A falha do serviço (503) **não** limpa, para preservar o que o usuário digitou. Se a consulta falhar ou vier incompleta, o usuário pode **preencher os campos à mão** e salvar (decisão de Rafael). Ao salvar, o servidor valida o formato do CEP e os campos obrigatórios, sem consultar o ViaCEP de novo.

## Decisões e pendências

- **Padrão automático (decisão de Rafael):**
  - quem ainda não tem endereço padrão (por exemplo, no primeiro cadastro) recebe o endereço cadastrado como padrão;
  - ao excluir o padrão, o endereço restante **mais recente** vira o novo padrão (`Endereco.delete()`, inclusive no Admin);
  - limitação: se o usuário editar o endereço padrão e desmarcar "padrão", ele fica sem padrão até escolher outro.
- **MySQL:** a regra "um padrão por usuário" usa uma `UniqueConstraint` condicional, que funciona no SQLite atual. O MySQL não suporta índice condicional, e o Django ignora a constraint nele (com aviso). Nesse caso, só a garantia da aplicação continua valendo (`save()` desmarca os outros padrões numa transação).
- **Compra só digital (RN-11, UC06 RN7):** o catálogo ainda não distingue livro físico de digital. A regra de não exigir endereço fica pendente de decisão do grupo e do checkout.
- **Proteção de dados (SRS 5.3 / 3.4):** criptografia em repouso e HTTPS **não** são atendidos automaticamente; o grupo precisa decidir. Use só dados fictícios na demonstração.
- **Link "Meus endereços" no menu** (`templates/base.html`): adicionado a pedido de Rafael, dentro do bloco `{% if user.is_authenticated %}`, logo após "Meu carrinho". **Davi:** é a única linha alterada por Rafael nesse arquivo; mantenha-a ou reposicione-a ao montar a navegação do checkout.
