# RELATÓRIO DE AUDITORIA DE DESENVOLVIMENTO ASSISTIDO POR IA

**Projeto:** Amazon — Sistema de Comércio Eletrônico  
**Integrante responsável:** Yuri  
**Semana/período:** Semana 2 (`TODO.md`; período do professor não preenchido)  
**Tarefa atribuída:** T08 — Frete fictício e acompanhamento de entrega  
**Ferramenta de IA utilizada:** Copilot SDK em VS Code  
**Data da auditoria:** 18/11/2026  
**Situação:** parcial

## 1. Introdução e contextualização

Esta auditoria avalia a implementação específica da T08: cotação demonstrativa de frete e acompanhamento de estados de entrega, sem integração com transportadora real. A avaliação registra separadamente os testes automatizados executados e o que Yuri observou na interface e na linha do tempo.

## 2. Descrição da tarefa e implementação realizada

A T08 prevê comparar frete e prazo em modalidades simuladas e acompanhar a evolução de pedidos após pagamento aprovado. A implementação criou o app `shipping`, com cotações aleatórias limitadas para Padrão e Expressa, página de comparação com CEP e ação administrativa protegida para avançar estados usando o serviço existente de pedidos.

Na primeira versão, o simulador também oferecia Agendada. Após testar a interface, Yuri solicitou retirar essa modalidade, observando que ela era desnecessária e mais cara que a entrega padrão apesar do prazo maior. A opção e o campo de data foram removidos do simulador; a modalidade histórica ainda presente no modelo compartilhado `Pedido.TipoEntrega` foi preservada para não alterar o contrato de outro módulo. A gravação das escolhas de frete no pedido segue dependente da integração com o checkout T10.

Arquivos alterados nesta implementação e revisão: `shipping/forms.py`, `shipping/services.py`, `shipping/views.py`, `shipping/urls.py`, `shipping/tests.py`, `shipping/apps.py`, `config/settings.py`, `config/urls.py`, `templates/shipping/simulador.html`, `templates/base.html`, `templates/orders/detalhe.html` e `TODO.md`.

## 3. Auditoria da implementação

### 3.1. Cotação e comparação de modalidades

**Critério esperado:** comparar valores e prazos determinísticos das modalidades exibidas no simulador.  
**O que foi verificado:** Yuri informou que testou o simulador e observou Padrão por R$ 15,90, Expressa por R$ 29,90 e, na versão inicial, Agendada por R$ 24,90. Para Agendada, informou ter escolhido 27/12/2026 e observado o valor de R$ 24,90; não informou o prazo ou a previsão exibidos. Os valores foram descritos como esperados.  
**Origem da observação:** integrante.  
**Avaliação do integrante:** os valores estavam como esperado, mas Yuri pediu a retirada de Agendada por considerá-la desnecessária e mais cara que Padrão, embora demorasse mais.  
**Problemas identificados:** nenhum erro técnico relatado na cotação. A relação preço/prazo de Agendada foi considerada inadequada pelo integrante.  
**Sugestões de melhoria:** remover a modalidade Agendada do simulador.  
**Encaminhamento:** alteração aplicada na Revisão 1; ver seção 3.3.  
**Resultado:** aprovada com ressalvas na versão inicial; substituída pela revisão abaixo.

### 3.2. Acompanhamento e transições de entrega

**Critério esperado:** após pagamento aprovado, avançar pelos estados de entrega em ordem, com histórico coerente e sem ação livre de cliente.  
**O que foi verificado:** Yuri relatou ter observado “Pagamento aprovado, Em preparação, Enviado, Entregue” e confirmou que avançaram na ordem esperada. Os testes automatizados também exercitam transições permitidas, bloqueio antes do pagamento, datas de envio/entrega e autorização administrativa.  
**Origem da observação:** integrante e testes automatizados da IA, identificados separadamente.  
**Avaliação do integrante:** a sequência observada correspondeu ao esperado.  
**Problemas identificados:** nenhum relatado nesse fluxo.  
**Sugestões de melhoria:** nenhuma adicional informada.  
**Encaminhamento:** sem ajuste solicitado para a sequência de estados.  
**Resultado:** aprovada.

### 3.3. Revisão 1 — 18/11/2026 — remoção da modalidade Agendada

**Pedido específico:** remover a ferramenta/campo de Data Agendada, considerada desnecessária e com relação preço/prazo desfavorável.  
**Implementação adicional:** removidos a opção Agendada, o campo de data e sua lógica de cotação do formulário e do comparador. Permanecem Padrão e Expressa, com suas cotações fixas. A escolha `AGENDADA` no modelo compartilhado de pedidos foi preservada para evitar alteração do contrato de outro módulo.  
**Testes da IA:** `.venv/bin/python manage.py test shipping orders` — 24 testes passaram; `.venv/bin/python manage.py check` — sem problemas; `.venv/bin/python manage.py makemigrations --check --dry-run` — nenhuma migration necessária. Os testes também verificam a ausência do campo/opção Agendada na interface e a rejeição dessa modalidade pelo serviço do simulador.  
**Reteste do integrante:** após atualizar `/entrega/frete/`, Yuri informou que não vê mais o campo Data Agendada e que os valores estão como esperado.  
**Problemas identificados:** nenhum relatado no reteste.  
**Encaminhamento:** alteração retestada pelo integrante; gravação da cotação no pedido continua pendente da T10.  
**Resultado:** aprovada para a interface revista.

### 3.4. Revisão 2 — 18/11/2026 — variação controlada dos valores de frete

**Pedido específico:** variar os valores calculados de Padrão e Expressa, sem perder a regra de que Padrão deve ser sempre mais barato.
**Implementação adicional:** cada cotação sorteia centavos em faixas separadas: Padrão, de R$ 12,00 a R$ 20,00; Expressa, de R$ 25,00 a R$ 35,00. A separação das faixas garante a ordem de preços; o prazo permanece fixo por modalidade. Os testes substituem o sorteio por valores controlados para serem reproduzíveis.
**Testes da IA:** `.venv/bin/python manage.py test shipping orders` — 24 testes passaram; `.venv/bin/python manage.py check` — sem problemas; `.venv/bin/python manage.py makemigrations --check --dry-run` — nenhuma migration necessária.
**Avaliação do integrante:** Yuri afirmou que “os valores observados foram consistentes” e informou uma cotação de Padrão R$ 14,19 e Expressa R$ 32,53. A resposta confirma um exemplo dentro das faixas e com a relação de preço solicitada; não foram fornecidos dois pares de cotações para comparar diretamente a variação entre recálculos.
**Problemas identificados:** nenhum relatado.
**Encaminhamento:** alteração implementada e validada tecnicamente; o integrante observou valores consistentes, mas a variação entre duas cotações não ficou demonstrada pelas respostas registradas.
**Resultado:** aprovada com ressalva quanto à evidência humana da variação entre recálculos.

## 4. Síntese dos achados

| Etapa | Evidência/observação | Resultado | Pendências |
|---|---|---|---|
| Valores e prazos de frete | Yuri observou Padrão R$ 15,90, Expressa R$ 29,90 e Agendada R$ 24,90 na primeira versão | Aprovada com ressalva inicial; Agendada retirada | Prazo exato observado para Agendada não informado |
| Acompanhamento | Yuri observou pagamento aprovado → preparação → enviado → entregue, em ordem esperada | Aprovada | Nenhuma relatada |
| Revisão da interface | Yuri confirmou que o campo Data Agendada não aparece mais e que os valores estão como esperado | Aprovada | Nenhuma relatada |
| Revisão dos valores | Faixas aleatórias controladas e relação Padrão < Expressa cobertas por teste; Yuri relatou uma amostra de R$ 14,19 e R$ 32,53 | Aprovada com ressalva | Não houve comparação humana entre dois pares de recotações |
| Persistência no pedido | O checkout T10 ainda não grava a cotação no pedido | Parcial | Integração depende da T10 |

## 5. Recomendações

**Recomendação do integrante:** manter somente Padrão e Expressa no simulador; retirar a modalidade Agendada.  
**Análise técnica da IA:** integrar os valores e prazos escolhidos ao pedido quando o checkout T10 estiver disponível e validar que a cotação confirmada não seja recalculada após a criação do pedido. As faixas disjuntas garantem tecnicamente que a opção Padrão permaneça mais barata. A opção `AGENDADA` preservada no modelo compartilhado não é oferecida pelo simulador revisado.

## 6. Conclusão e avaliação do uso da IA

Eu testei os valores do simulador e considerei que estavam como esperado. Também observei os status do pedido avançando na ordem correta. Pedi a remoção da entrega Agendada porque não a considero necessária e ela custava mais que a entrega padrão, apesar de demorar mais. Após a alteração, confirmei que o campo de data não aparece mais e que os valores estão como esperado. Pedi que os valores de frete variassem dentro de limites, mantendo Padrão mais barato que Expressa. Na conferência, observei Padrão a R$ 14,19 e Expressa a R$ 32,53, que considerei consistentes. A integração da cotação ao pedido ainda depende do checkout.

**Parecer final:** a interface de frete e a sequência de acompanhamento foram verificadas; os limites e a ordem de preço também foram validados tecnicamente. A variação entre recálculos não foi comparada explicitamente na avaliação humana, e a persistência integrada da cotação permanece pendente da T10.

---
**Responsável pela avaliação:** Yuri  
**Elaboração:** relatório estruturado com auxílio de IA a partir das evidências, testes executados e respostas do integrante.
