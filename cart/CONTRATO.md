# Contrato da interface do carrinho — T04 e T05

Contrato do código integrado na `main`, conferido em 09/11/2026. Davi informou nesta sessão que já alinhou com Pedro o uso dos campos e rotas. As rotas abaixo já existem; a T05 utiliza os endpoints de Pedro.

| Operação | Nome Django | Caminho | Método e campos |
|---|---|---|---|
| Consultar carrinho | `cart:detail` | `/carrinho/` | GET, usuário autenticado |
| Adicionar produto | `cart:add` | `/carrinho/adicionar/<produto_id>/` | POST, `quantidade` inteira positiva e `csrfmiddlewaretoken` |
| Atualizar item | `cart:update` | `/carrinho/item/<item_id>/atualizar/` | POST, `quantidade` inteira e `csrfmiddlewaretoken`; zero remove o item após confirmação na interface |
| Remover item inteiro | `cart:remove` | `/carrinho/item/<item_id>/remover/` | POST, `csrfmiddlewaretoken`; confirmação antes do envio |

## Dados dos templates

- `catalog/product_detail.html`: recebe `produto`, `especializacao` e `categoria_selecionada`; envia o campo `quantidade` para `cart:add`, com `produto.pk` na URL. Se o produto estiver sem estoque, quantidade e botão ficam desativados.
- `cart/detail.html`: recebe `itens` e `total`. Cada item fornece `pk`, `produto`, `quantidade` e `subtotal`. O formulário identifica o item por `item.pk`, não pelo identificador do produto.
- Preços, subtotais e total são calculados pelo backend com `Decimal`. O template apenas formata a apresentação com duas casas decimais.
- As views retornam mensagens pelo framework de mensagens do Django, exibidas em `base.html`. Erros usam o estilo `alert-danger` do Bootstrap.

## Autenticação e limites

- Login: GET/POST `/accounts/login/`, nome `login`; campos `username`, `password`, `next` e token CSRF. O redirecionamento seguro de `next` é tratado pela view nativa do Django.
- Logout: POST `/accounts/logout/`, nome `logout`, com CSRF.
- A consulta, atualização e remoção exigem login; a adição anônima redireciona ao login e retorna ao detalhe. Após entrar, o usuário deve confirmar a adição novamente.
- Atualização e remoção consultam somente itens pertencentes ao usuário autenticado. As regras de quantidade e estoque continuam no backend de Pedro.
- A confirmação de remoção usa `confirm()` no navegador. Cancelar mantém o item; atualizar com zero também solicita confirmação.
- Checkout permanece desativado e sinalizado como indisponível. Nenhuma rota de pedido ou pagamento foi adicionada.
