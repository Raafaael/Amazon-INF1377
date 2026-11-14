# Contrato do app `orders` — T06, Semana 2

O app registra **pedidos simulados** e expõe `/pedidos/` (listagem própria) e `/pedidos/<id>/` (detalhes próprios). Ambas as páginas exigem login; pedido de outro usuário retorna 404. Não há endpoint de alteração de status para clientes.

## Criação para Davi (checkout)

```python
from decimal import Decimal
from orders.services import criar_pedido

pedido = criar_pedido(
    request.user,
    chave_checkout,                # string estável para esta intenção; até 64 caracteres
    endereco=endereco_do_usuario,  # objeto Endereco de Rafael, ou None sem entrega
    frete=Decimal('12.00'),        # cotação já escolhida de Yuri
    tipo_entrega='PADRAO',         # PADRAO, EXPRESSA ou AGENDADA
    prazo_entrega_dias=5,          # opcional
    previsao_entrega=None,         # data simulada opcional
)
```

- O serviço **lê o carrinho** do usuário, rejeita carrinho vazio, quantidades inválidas ou acima do estoque e preço/frete inválidos. Calcula subtotais e total com `Decimal` dentro de transação.
- O mesmo par `(usuário, chave_checkout)` sempre devolve o pedido original, inclusive após atualizar a página ou esvaziar o carrinho. O checkout deve gerar uma chave por **intenção de compra** e reutilizá-la em reenvios; não gerar outra chave a cada POST repetido.
- Itens guardam nome, quantidade, preço unitário e subtotal da compra; pedido guarda valores e uma **cópia** do endereço (`endereco_dados` e `endereco_entrega`). Editar/excluir o endereço ou mudar o produto depois não altera o histórico.
- O pedido começa em `AGUARDANDO_PAGAMENTO`, com um evento no histórico. O serviço **não limpa o carrinho nem baixa estoque**; o momento de baixa/limpeza e a política para pagamento recusado devem ser alinhados na integração. A chave impede duplicação da mesma intenção, não de intenções diferentes.
- A modalidade de entrega exige endereço do próprio usuário. Para demonstração isolada de T06, é possível criar sem modalidade/endereço/frete. Nesse caso, a tela indica “entrega ainda não informada”; isso **não classifica o pedido como digital**. O catálogo atual não distingue e-books.
- A exceção de validação é `django.core.exceptions.ValidationError`; o checkout deve capturá-la e mostrar a mensagem. A página de confirmação pode usar `reverse('orders:detalhe', args=[pedido.pk])`.

## Status para Pedro (pagamento) e Yuri (entrega)

```python
from orders.models import Pedido
from orders.services import atualizar_status

# Pedro: somente após resultado aprovado do simulador; PIX gerado continua pendente.
pedido = atualizar_status(pedido, Pedido.Status.PAGAMENTO_APROVADO,
                          origem='pagamento', observacao='Cartão fictício aprovado')
# Recusa: Pedido.Status.PAGAMENTO_RECUSADO com origem='pagamento'.

# Yuri: somente após aprovação, em ordem.
pedido = atualizar_status(pedido, Pedido.Status.EM_PREPARACAO, origem='entrega')
pedido = atualizar_status(pedido, Pedido.Status.ENVIADO, origem='entrega')
pedido = atualizar_status(pedido, Pedido.Status.ENTREGUE, origem='entrega')
```

- Cada transição válida cria `HistoricoStatusPedido` com data e observação opcional (até 255 caracteres). A transição e o histórico ocorrem na mesma transação. Saltos, repetições, entrega sem envio e entrega após recusa são rejeitados.
- `origem='pagamento'` aceita apenas resultado de pagamento (ou retorno de recusa para aguardando). `origem='entrega'` aceita apenas os três estados de entrega. Estas origens são **contratos internos para módulos confiáveis**, não parâmetros de formulário que o cliente possa escolher.
- `origem='administracao', usuario=request.user` exige `is_staff` e não pode aprovar/recusar pagamento; pode cancelar ou avançar transições permitidas. Não expor chamada direta a clientes. O Admin exibe os dados em modo leitura para preservar o histórico.
- Não há cancelamento, devolução ou reembolso completos nesta etapa; `CANCELADO` apenas representa um estado terminal controlado. A regra final de reserva/baixa de estoque e ações de pedido digital permanece para alinhamento do grupo.

## Demonstração sem checkout

Após `python manage.py migrate`, entre com uma conta local, adicione um produto ao carrinho e execute:

```text
python manage.py criar_pedido_demo NOME_DO_USUARIO
```

O comando usa a chave fixa `pedido-demo-1`: executá-lo de novo para a mesma conta **não duplica** o pedido e agora informa que devolveu um pedido já existente. Para criar **outro pedido** com os itens atuais do carrinho, use `python manage.py criar_pedido_demo NOME_DO_USUARIO --novo`. Também é possível usar `--chave nome-da-intencao-2` para controlar manualmente a chave; repeti-la devolve o mesmo pedido. Depois, acesse `/pedidos/` com essa conta. O pedido fica aguardando pagamento fictício; não há cobrança real e o carrinho permanece intacto.
