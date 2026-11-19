# Contrato do app `payments` — T09, Semana 2

Pagamentos **simulados** (cartão fictício e PIX de demonstração). Não há banco, gateway nem cobrança real. Rotas sob `/pagamentos/`, todas com login; pedido ou pagamento de outro usuário retorna 404.

| Rota | Nome | Uso |
|---|---|---|
| `GET /pagamentos/` | `payments:lista` | Pedidos do usuário aguardando pagamento (ou com pagamento recusado) |
| `GET/POST /pagamentos/pedido/<id>/` | `payments:pagar` | Página de demonstração; o POST processa o cartão |
| `POST /pagamentos/pedido/<id>/pix/` | `payments:gerar_pix` | Gera (ou reaproveita) PIX pendente |
| `POST /pagamentos/pix/<pagamento_id>/confirmar/` | `payments:confirmar_pix` | Ação “Simular pagamento PIX” |
| `POST /pagamentos/pix/<pagamento_id>/cancelar/` | `payments:cancelar_pix` | Cancela PIX pendente |

Todas as rotas POST aceitam `next` (somente URL interna) para voltar ao checkout.

## Modelos

- `Pagamento`: `pedido`, `modalidade` (`CARTAO`/`PIX`), `valor` (copiado de `pedido.total` no servidor), `status` (`PENDENTE`, `APROVADO`, `RECUSADO`, `CANCELADO`), `mensagem` e datas. No máximo **um** `APROVADO` por pedido. `pedido.pagamentos` lista as tentativas.
- `PagamentoCartao` (`pagamento.cartao`): `bandeira` fictícia, `ultimos_digitos`, `parcelas` (1–12, sem juros) e `valor_parcela`. **Não guarda número completo, nome, validade nem CVV.**
- `PagamentoPix` (`pagamento.pix`): `codigo` (`PIXSIM-...`) e `expira_em` (**1 minuto**). O QR contém texto livre `PIX SIMULADO - NAO PAGAVEL ...`, não um BR Code, e é gerado localmente com `qrcode` (SVG).

## Serviços (para Davi)

```python
from django.core.exceptions import ValidationError
from payments import services

pagamento = services.pagar_com_cartao(request.user, pedido, numero='4242 4242 4242 4242',
                                      nome='Fulano Teste', validade='12/28', cvv='123', parcelas=3)
pagamento.status           # 'APROVADO' ou 'RECUSADO'; pagamento.mensagem explica o resultado

pix = services.gerar_pix(request.user, pedido)     # PENDENTE; pedido continua AGUARDANDO_PAGAMENTO
services.confirmar_pix(request.user, pix)          # APROVADO; pedido → PAGAMENTO_APROVADO
services.cancelar_pix(request.user, pix)           # CANCELADO; pedido continua aguardando
services.pix_ativo(pedido)                         # PIX pendente e válido, ou None
```

- Erros (dados inválidos, pedido alheio, já pago, PIX expirado/não pendente) levantam `ValidationError`.
- O pedido precisa estar em `AGUARDANDO_PAGAMENTO` ou `PAGAMENTO_RECUSADO`. Em nova tentativa após recusa, o serviço volta o pedido para `AGUARDANDO_PAGAMENTO` antes de registrar o novo resultado.
- Pagar com cartão cancela um PIX pendente do mesmo pedido.
- O status do pedido só muda via `orders.services.atualizar_status(..., origem='pagamento')` (contrato de Breno), sempre com evento no histórico.
- O serviço **não limpa o carrinho nem baixa estoque**. Essa decisão fica para a integração do checkout.

### Partials para o checkout

```django
{# na view: contexto.update(payments.views.contexto_pagamento(pedido)); contexto['next'] = request.path #}
{% include 'payments/_cartao.html' %}   {# usa pedido, form_cartao, next #}
{% include 'payments/_pix.html' %}      {# usa pedido, pix, pix_qr, pix_expirado, expiracao_segundos, next #}
```

O formulário de cartão envia para `payments:pagar`. Em caso de erro de validação, o usuário é levado à página de pagamento do próprio app.

## Regra da operadora simulada (não exibida na tela)

Após a validação, cada tentativa com cartão sorteia um dos dois resultados com chances iguais: **50% aprovado** e **50% recusado**. O número não determina o resultado; precisa ter 16 dígitos e passar no algoritmo de Luhn, com validade futura (MM/AA) e CVV de 3 dígitos. O resultado sorteado é registrado no pagamento e no histórico do pedido; atualizar a página não sorteia novamente. Uma recusa permite outra tentativa no mesmo pedido.

Número fictício válido para testar: `4242 4242 4242 4242`. Os testes automatizados controlam o sorteio para cobrir aprovação e recusa sem depender do acaso.
