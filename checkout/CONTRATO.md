# Checkout da Semana 2 — T10 de Davi

O app `checkout` compõe os serviços existentes de `addresses`, `shipping`, `orders`
e `payments`. Usa Django Templates e um registro de intenção de compra (`Checkout`);
os itens, valores e estados definitivos continuam pertencendo a `orders.Pedido`.

## Executar e conferir

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

Entre com uma conta local e adicione um produto disponível ao carrinho. A partir
de `/carrinho/`, use **Finalizar compra** e percorra as etapas:

1. **Endereço:** utiliza `SelecaoEnderecoForm` e `addresses/_selecao.html`.
   O cadastro de Rafael aceita `next` para retornar ao mesmo checkout.
2. **Entrega:** apresenta Padrão e Expressa por `shipping.services.cotar_frete`.
   As duas cotações são geradas ao selecionar o endereço e guardadas no banco;
   atualizar a página ou reenviar o mesmo endereço não sorteia novamente.
3. **Pagamento:** mostra endereço, prazo e resumo para revisão. O POST
   **Confirmar dados e escolher pagamento** chama `orders.services.criar_pedido`,
   usando o UUID do checkout como chave estável. O pedido fica aguardando
   pagamento e seus valores ficam congelados. Depois são apresentados os
   componentes de cartão e PIX de Pedro.
4. **Confirmação:** mostra o número e o estado real do pedido. PIX pendente tem
   QR não pagável e ação explícita de confirmação; recusa permite nova tentativa
   no mesmo pedido. Há links para detalhes e histórico de pedidos.

### Cenários de demonstração

- Cartão fictício `4242 4242 4242 4242`: após validar os dados, cada tentativa tem 50% de chance de aprovação e 50% de recusa. Em caso de recusa, tente novamente no mesmo pedido. Os testes automatizados controlam o sorteio para verificar os dois caminhos.
- Informe nome fictício, validade futura em `MM/AA` e CVV fictício de três dígitos.
- PIX: gerar QR mantém o pedido pendente; **Simular pagamento PIX** aprova.
  O prazo de expiração vem do simulador de Pedro. Pode cancelar ou gerar outro.
- Atualize a confirmação e reenvie o formulário: o pedido e a baixa de estoque
  permanecem únicos para aquela intenção.
- Antes de confirmar os dados, alterar preço/quantidade exige voltar ao carrinho
  e iniciar novamente. Se o estoque acabar depois de registrar o pedido, a
  aprovação é bloqueada e o carrinho é preservado.

## Regras da integração

- Todo checkout exige login e pertence ao usuário da requisição. UUID alheio
  retorna 404. Endereços e PIX também são restritos ao proprietário.
- As alterações usam POST e CSRF. Preço, frete, prazo e total enviados pelo
  cliente são ignorados; são utilizados os dados do servidor.
- Antes de registrar o pedido, o carrinho e o endereço são comparados com os
  dados revisados. Endereço editado/excluído exige nova seleção e cotação.
- Após registrar o pedido, voltar às etapas anteriores não altera seus valores.
  As páginas direcionam para o pagamento daquele pedido.
- Recusa, cancelamento de PIX e PIX pendente não limpam o carrinho nem baixam
  estoque. A aprovação revalida disponibilidade e realiza pagamento, baixa e
  limpeza dentro da mesma transação. Não há reserva antecipada de estoque.
- A limpeza retira apenas as quantidades compradas dos itens originais.
  Produtos novos, itens recriados e unidades adicionais permanecem no carrinho.
- `estoque_baixado` é o marcador persistente para impedir uma segunda baixa.
  Atualizar a página de resultado é somente leitura sobre essa conclusão.
- O serviço de pagamento, suas validações, máscaras, QR e histórico não foram
  duplicados. Os partials aceitam URLs opcionais (`cartao_action`,
  `gerar_pix_action`, `confirmar_pix_action`, `cancelar_pix_action`). Sem essas
  variáveis, as páginas próprias de pagamentos mantêm suas rotas anteriores.
- As rotas de demonstração de `payments` redirecionam pedidos associados a
  checkout para a T10. Isso evita aprovar pela interface isolada sem executar
  a baixa e a limpeza. Uma tentativa enviada pela rota antiga deve ser refeita
  no checkout; os dados de cartão não são transportados no redirecionamento.
- Chamadas internas de pagamento para pedidos da T10 devem passar por
  `checkout.services.pagar` ou `checkout.services.acao_pix`. Chamar diretamente
  o serviço isolado de Pedro não finaliza estoque/carrinho.
- O catálogo atual não distingue livros físicos de e-books. O fluxo reutiliza
  os endereços e entregas existentes; a exceção de compra exclusivamente digital
  continua pendente de modelagem/decisão do grupo, sem classificação inventada.

## Arquivos e testes

- `models.py` e `migrations/0001_initial.py`: intenção de compra e persistência.
- `services.py`: composição dos contratos e conclusão transacional.
- `forms.py`, `views.py`, `urls.py`: etapas e autorização.
- `templates/checkout/`: progresso, seleção, revisão, pagamento e resultado.
- Integrações pontuais em `cart/views.py`, `templates/cart/detail.html`,
  `payments/views.py`, partials de pagamento, configuração e CSS compartilhado.

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe manage.py test checkout
.\.venv\Scripts\python.exe manage.py test
```

Os testes HTTP usam os serviços reais dos quatro apps e banco temporário do
Django. Cobrem aprovação, recusa, PIX pendente/expirado/cancelado/confirmado,
CSRF real nos formulários, isolamento, reenvio, cotação persistente, dados
adulterados, mudanças no carrinho/endereço, estoque e rollback. A disputa de
estoque é simulada por duas compras sequenciais; não é teste de carga ou de
requisições simultâneas. Aparência e responsividade exigem revisão no navegador.
