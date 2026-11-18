# RELATÓRIO DE AUDITORIA DE DESENVOLVIMENTO ASSISTIDO POR IA

**Projeto:** Amazon — Sistema de Comércio Eletrônico  
**Integrante responsável:** Pedro  
**Semana/período:** Semana 2 — Checkout, pedidos, pagamentos e entrega (`TODO.md`)  
**Tarefa atribuída:** T09 — Pagamento simulado com cartão e PIX (QR Code)  
**Ferramenta de IA utilizada:** Claude Code (Claude Opus 5.5)  
**Data da auditoria:** 17/11/2026  
**Situação:** concluída. A rodada inicial e as Revisões 1 e 2 foram avaliadas e retestadas. O uso do partial no checkout não foi verificado por mim.

## 1. Introdução e contextualização

O projeto é um e-commerce acadêmico em Django. Na Semana 2, o grupo completa o fluxo de compra. A T09 entrega o pagamento **simulado** por cartão fictício e PIX de demonstração, sem cobrança real.

Antes de implementar, a IA analisou os requisitos e propôs sete decisões. Validei e ajustei essas decisões. Depois, a IA implementou e testou o código. Esta auditoria registra o que verifiquei no navegador e as correções feitas durante a revisão.

## 2. Descrição da tarefa e implementação realizada

**Solicitação (`TODO.md`, T09):**
- modelos de pagamento;
- formulário de cartão fictício com máscaras e validação no servidor, sem salvar CVV nem número completo;
- resultado aprovado/recusado reproduzível;
- PIX com QR Code local e não pagável;
- ação explícita para confirmar o PIX;
- página própria e partial para o checkout;
- somente pagamento aprovado marca o pedido como pago;
- testes e documentação.

**Decisões validadas antes da implementação:**
- Aprovação por paridade do último dígito do cartão, **sem mostrar a regra na tela**.
- Validação por Luhn, validade futura e CVV de 3 dígitos.
- Modelos separados (`Pagamento`, `PagamentoCartao`, `PagamentoPix`), **com opção de parcelas**.
- Expiração do PIX em **1 minuto**.
- Nova tentativa permitida após recusa.
- QR Code gerado com a biblioteca `qrcode`.

**Implementação gerada pela IA:**
- **App novo `payments/`:** modelos, serviços, formulário, views, URLs, Admin somente leitura, JS de máscaras e contagem regressiva, 27 testes e `CONTRATO.md`.
- **Templates:** `templates/payments/` com a página de pagamento, a lista de pedidos a pagar e os partials `_cartao.html` e `_pix.html`.
- **Arquivos compartilhados:** uma linha cada em `config/settings.py`, `config/urls.py` e `requirements.txt`.
- **Integração:** o status do pedido muda pelo `atualizar_status(..., origem='pagamento')` da T06.
- **Parcelas:** a IA definiu o limite de 1 a 12, sem juros. Os documentos não definem esse limite.

**Testes da IA:**
- `python manage.py test`: 162 testes, OK (após a Revisão 2).
- `python manage.py check` e `makemigrations --check`: sem pendências.
- Verificação no navegador pela IA: máscaras, recusa, aprovação, cartão vencido, QR, confirmação do PIX e histórico do pedido, expiração após 1 minuto e reabertura da aba PIX expirada.

## 3. Auditoria da implementação

### 3.1. Cartão fictício — máscaras, validade e mensagem de recusa

**Critério esperado:** máscaras nos campos, validação clara dos dados e mensagem de recusa compreensível.  
**O que foi verificado:** no pedido de demonstração, testei o formulário, inclusive a validade `18/28`, e enviei um cartão terminado em ímpar.  
**Avaliação do integrante:** a máscara de validade aceitava mês inexistente (`18`). A mensagem de recusa era clara, mas não deixava claro se eu tinha errado no preenchimento ou se o problema era do cartão.  
**Problemas identificados (achados do integrante):**
1. A validade não era verificada durante o preenchimento. O servidor já rejeitava o valor no envio, mas não confirmei o que aparecia nesse momento.
2. A mensagem de recusa era ambígua quanto à causa.

**Encaminhamento:** escolhi o aviso ao sair do campo. A IA implementou o aviso de validade (mês 01–12, formato e vencimento). A mensagem de recusa passou a ser "Dados do cartão válidos, mas o pagamento foi recusado pela operadora simulada. Tente outro cartão ou pague com PIX.". A IA verificou no navegador (`18/28`: mês inválido, `12/20`: vencido) e por teste.  
**Reteste do integrante:** a validação da data e a nova mensagem de recusa deram certo.  
**Resultado:** problema relatado → correção aplicada → reteste aprovado. **Aprovada.**

### 3.2. PIX simulado — expiração

**Critério esperado:** o QR fica pendente, expira em 1 minuto e não é confirmado automaticamente.  
**O que foi verificado:** gerei um PIX e esperei expirar. Os botões ficaram desabilitados e o PIX apareceu como expirado. Ao dar refresh, a página voltou para a aba Cartão e não mostrou mais o estado expirado.  
**Problema identificado (achado do integrante):** depois do refresh, o usuário perdia o contexto do PIX expirado.  
**Encaminhamento:** correção solicitada e aplicada (ver Revisão 1).  
**Resultado:** ver Revisão 1.

### 3.3. PIX simulado — confirmação

**Critério esperado:** somente a ação "Simular pagamento PIX" aprova o pagamento e marca o pedido como pago.  
**O que foi verificado:** confirmei um PIX gerado.  
**Avaliação do integrante:** ficou claro para o usuário que o pagamento deu certo.  
**Problemas identificados:** nenhum relatado. Depois, conferi o histórico de status em "Ver pedido" e deu certo.  
**Resultado:** aprovada.

### Revisão 1 — 17/11/2026 — PIX expirado após refresh

**Pedido:** ao recarregar a página, manter a aba PIX e informar que o último código expirou.  
**Implementação da IA:** quando a última tentativa do pedido é um PIX expirado, a página abre na aba PIX com o aviso "Seu último PIX expirou. Gere um novo código." e o botão **Gerar novo PIX**. Foi incluído um novo teste automatizado.  
**Reteste do integrante:** a página voltou à aba PIX com o aviso de expiração, como eu esperava.  
**Resultado:** problema relatado → correção aplicada → reteste aprovado. **Aprovada.**

### Revisão 2 — 17/11/2026 — Envio do cartão abria a aba PIX

**Achado do integrante:** depois de retestar a validade e a mensagem, ao clicar em **Pagar** a página me levava para a aba PIX, com o aviso de PIX expirado.  
**Causa (análise técnica da IA):** no pedido de teste, a última tentativa era um PIX expirado. Quando o envio do cartão voltava com erro de validação, a regra da Revisão 1 reabria a aba PIX e escondia o erro do cartão. Foi uma regressão introduzida pela Revisão 1.  
**Implementação da IA:** um envio pelo formulário de cartão sempre volta na aba **Cartão**. A aba PIX expirada continua aparecendo ao abrir ou recarregar a página. Foi incluído um teste automatizado, e a IA verificou no navegador (cartão vencido no pedido com PIX expirado: aba Cartão com "Cartão vencido.").  
**Reteste do integrante:** deu certo; com validade inválida e com dados válidos, a página permaneceu na aba Cartão.  
**Resultado:** problema relatado → correção aplicada → reteste aprovado. **Aprovada.**

## 4. Síntese dos achados

| Etapa | Evidência | Origem | Resultado | Pendência |
|---|---|---|---|---|
| Máscara/validação da validade | `18/28` aceito sem aviso na digitação | Integrante | Corrigido e retestado | — |
| Mensagem de recusa | Causa ambígua (preenchimento × cartão) | Integrante | Corrigido e retestado | — |
| PIX expirado após refresh | Voltava à aba Cartão sem aviso | Integrante | Corrigido e retestado | — |
| Envio do cartão com PIX expirado | Abria a aba PIX e escondia o erro do cartão (regressão da Revisão 1) | Integrante | Corrigido e retestado | — |
| Confirmação do PIX | Pagamento confirmado com clareza; histórico em "Ver pedido" conferido | Integrante | Aprovado | — |
| Testes automatizados (162) e navegador | Aprovação, recusa, PIX, permissões, persistência | Análise técnica da IA | OK | Não substituem a avaliação humana |

## 5. Recomendações

- **Minhas:** a validade deve ser avisada ao sair do campo, e a mensagem de recusa deve deixar clara a causa. As duas foram aplicadas e retestadas. O envio do cartão deve permanecer na aba Cartão; corrigido e retestado.
- **Sugestões técnicas da IA:**
  - Validar o limite de 12 parcelas com o grupo.
  - Validar o uso dos partials `_cartao.html` e `_pix.html` no checkout da T10.
  - Decidir com o grupo se é preciso um link para `/pagamentos/` na navegação (`base.html` é compartilhado).

## 6. Conclusão e avaliação do uso da IA

A utilização da IA me ajudou a implementar o pagamento simulado com cartão e PIX a partir das decisões que validei antes. Nos testes, identifiquei que a validade aceitava um mês inexistente, que a mensagem de recusa não deixava claro se o erro era meu ou do cartão e que o estado do PIX expirado se perdia ao recarregar a página. A IA corrigiu esses pontos. Retestei o PIX expirado, a validação da data e a nova mensagem de recusa, e deram certo. No reteste, identifiquei que o botão Pagar passou a me levar para a aba PIX expirada; a IA corrigiu e, no reteste, deu certo. Na confirmação do PIX, ficou claro que o pagamento deu certo. Também conferi o histórico de status do pedido, e deu certo.

**Parecer final:** aprovada com ressalvas. Os fluxos principais foram avaliados e os problemas encontrados foram corrigidos. Falta verificar a integração com o checkout (T10).

---
**Responsável pela avaliação:** Pedro  
**Elaboração:** relatório estruturado com auxílio de IA a partir das evidências e respostas do integrante.
