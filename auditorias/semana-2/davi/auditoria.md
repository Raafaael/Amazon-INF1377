# RELATÓRIO DE AUDITORIA DE DESENVOLVIMENTO ASSISTIDO POR IA

**Projeto:** Amazon — Sistema de Comércio Eletrônico  
**Integrante responsável:** Davi  
**Semana/período:** Semana 2, conforme TODO.md; prazo do professor não preenchido  
**Tarefa atribuída:** T10 — Checkout em etapas e confirmação da compra  
**Ferramenta de IA utilizada:** Codex  
**Data da auditoria:** 18/11/2026  
**Situação:** parcial — implementação e verificação técnica realizadas; avaliação humana pendente

## 1. Introdução e contextualização

A solicitação de Davi foi implementar sua tarefa T10 da Semana 2. O checkout
compõe o carrinho e os módulos existentes de endereços, frete, pedidos e
pagamentos em uma compra acadêmica simulada. Esta auditoria registra o código
produzido nessa solicitação e separa os testes executados pela IA da avaliação
humana, ainda não recebida. Não há cobrança ou entrega real.

## 2. Descrição da tarefa e implementação realizada

Foram criadas as etapas Endereço, Entrega, Pagamento e Confirmação, com indicador
de progresso e resumo dos produtos, quantidades e valores. O botão Finalizar
compra foi conectado ao fluxo e bloqueado para itens sem disponibilidade.

O app `checkout` guarda a intenção de compra, endereço revisado, cotações e
vínculo com o pedido. Reutiliza `SelecaoEnderecoForm`, a cotação de Yuri, a
criação de pedidos de Breno e os serviços, máscaras e partials de Pedro. Não
foram recriados os simuladores ou modelos dos demais módulos.

As cotações são persistidas e o UUID da intenção é reutilizado na criação do
pedido. O servidor revalida carrinho, endereço e estoque; após confirmar os
dados, os valores ficam registrados em Pedido. Aprovação, baixa de estoque e
limpeza das quantidades compradas acontecem na mesma transação. Recusa e PIX
pendente preservam o carrinho; produtos novos e quantidades adicionais também
são preservados. Não há reserva antecipada de estoque.

**Arquivos criados:** `checkout/{apps,models,forms,services,views,urls,tests}.py`,
`checkout/__init__.py`, `checkout/migrations/`, `checkout/CONTRATO.md` e
`templates/checkout/{base,_resumo,endereco,entrega,pagamento,resultado}.html`.

**Arquivos modificados:** `cart/views.py`, `templates/cart/detail.html`,
`config/settings.py`, `config/urls.py`, `payments/views.py`,
`templates/payments/_cartao.html`, `templates/payments/_pix.html`,
`static/css/site.css` e `README.md`.

**Impacto compartilhado:** os partials de pagamento aceitam ações opcionais do
checkout, mantendo as rotas anteriores como padrão. As views de demonstração
de pagamentos redirecionam pedidos associados à T10 ao checkout para evitar
aprovação sem baixa/limpeza. O fluxo de pedidos avulsos continua no módulo de
Pedro. As alterações foram anunciadas antes da implementação.

**Ambiente:** instalação de `requirements.txt` na `.venv`, alinhando Django
6.1.3 ao Django 5.2.19 declarado pelo projeto e instalando `qrcode` 8.2.
`manage.py migrate` aplicou `addresses.0001_initial`, `orders.0001_initial`,
`checkout.0001_initial` e `payments.0001_initial` sem apagar o banco local.
Uma demonstração em banco temporário separado foi iniciada na porta 8001,
com produtos e endereço fictícios e autenticação automática apenas nesse
processo de teste. Essa configuração não faz parte do código da aplicação.

## 3. Auditoria da implementação

### 3.1. Navegação, seleção de endereço e frete

**Critério esperado:** percorrer etapas, reutilizar cadastro/seleção do endereço,
comparar entregas e manter a cotação ao atualizar ou voltar.  
**O que foi verificado:** análise técnica da IA e testes HTTP dos serviços reais:
seleção própria, rejeição de endereço alheio/ausente/alterado/excluído,
persistência de cotação e validação de modalidades.  
**Avaliação do integrante:** ainda não recebida.  
**Problemas identificados:** aparência e responsividade não observadas no
navegador. Computer Use interrompeu a sessão por não conseguir determinar com
segurança a URL atual do Chrome; não foram utilizados meios alternativos de
automação para contornar esse bloqueio.  
**Sugestões de melhoria:** nenhuma sugestão humana recebida.  
**Resultado:** inconclusiva quanto à avaliação humana e visual.

### 3.2. Pedido, valores e reenvio

**Critério esperado:** valores revisados no servidor e congelados no pedido,
sem duplicação por reenvio ou atualização.  
**O que foi verificado:** testes da IA com confirmação repetida, alterações de
preço/quantidade/estoque, valores adulterados no POST, retorno a etapas
anteriores e manutenção dos preços históricos.  
**Avaliação do integrante:** ainda não recebida.  
**Problemas identificados:** nenhum defeito confirmado nessa verificação
automatizada; isso não constitui aprovação humana.  
**Sugestões de melhoria:** nenhuma sugestão humana recebida.  
**Resultado:** inconclusiva quanto à avaliação humana.

### 3.3. Pagamento e conclusão transacional

**Critério esperado:** distinguir aprovação, recusa e PIX pendente; exigir ação
explícita para confirmar PIX e ajustar estoque/carrinho somente após aprovação.  
**O que foi verificado:** testes da IA de cartão aprovado/recusado/inválido,
PIX pendente/confirmado/cancelado/expirado, troca de PIX por cartão, reenvios,
estoque esgotado, duas compras sequenciais disputando estoque, preservação de
itens adicionados depois e rollback de pagamento/histórico por falha na baixa.  
**Avaliação do integrante:** ainda não recebida.  
**Problemas identificados:** não foi realizado teste de carga ou concorrência
simultânea. O catálogo não distingue e-books de livros físicos; a exceção de
compra exclusivamente digital depende de decisão/modelagem do grupo.  
**Sugestões de melhoria:** nenhuma sugestão humana recebida.  
**Resultado:** inconclusiva quanto à avaliação humana.

### 3.4. Autorização e formulários

**Critério esperado:** login obrigatório, dados restritos ao proprietário e
ações de alteração via POST com CSRF.  
**O que foi verificado:** testes da IA com acesso por outro usuário, falta de
autenticação, métodos inválidos, POST sem CSRF e submissão dos formulários HTML
reais com CSRF habilitado. Não foram persistidos dados completos de cartão/CVV.  
**Avaliação do integrante:** ainda não recebida.  
**Problemas identificados:** nenhum defeito confirmado nesses cenários. Não foi
realizada auditoria geral de segurança do projeto.  
**Sugestões de melhoria:** nenhuma sugestão humana recebida.  
**Resultado:** inconclusiva quanto à avaliação humana.

## 4. Síntese dos achados

| Etapa | Evidência técnica da IA | Resultado humano | Pendências |
|---|---|---|---|
| Endereço e entrega | Fluxos HTTP e cotações persistentes | Inconclusivo | Conferência visual em desktop e tela menor |
| Pedido e resumo | Reenvio sem duplicação e valores congelados | Inconclusivo | Avaliação de Davi |
| Pagamento e conclusão | Aprovação, recusa, PIX, estoque e rollback | Inconclusivo | Avaliação de Davi; definição futura para e-books |
| Autorização | Proprietário, login, POST e CSRF real | Inconclusivo | Avaliação de Davi |

### Registro dos comandos

- `.\.venv\Scripts\python.exe manage.py test checkout --verbosity 1`: **19 testes aprovados**.
- `.\.venv\Scripts\python.exe manage.py test --verbosity 1`: **186 testes aprovados** na execução final.
- `.\.venv\Scripts\python.exe manage.py check`: nenhuma inconsistência identificada.
- `.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run`: nenhuma alteração pendente.
- `.\.venv\Scripts\python.exe manage.py migrate`: quatro migrações iniciais aplicadas com sucesso.
- `git diff --check`: sem erros de whitespace; aviso sobre futura conversão LF/CRLF no CSS.
- Requisição HTTP ao carrinho da demonstração isolada: **200**. Não comprova aparência ou execução do JavaScript.

Os testes do Django utilizaram banco temporário, separado dos dados locais.
O checklist e o estado de `TODO.md` não foram alterados, conforme a instrução
expressa recebida nesta conversa. Não houve escrita de estado/histórico do Git.

## 5. Recomendações

**Análise técnica da IA:** conferir as quatro etapas em navegador desktop e
em tela menor; testar máscaras, mensagens e links do resultado. Manter a
distinção entre PIX gerado e pagamento confirmado. Ao integrar novas ações,
pagamentos de pedidos da T10 devem passar pelos serviços do checkout para
preservar a conclusão transacional. Resolver a identificação de e-books com o
grupo antes de dispensar endereço/frete para qualquer livro.

**Recomendações do integrante:** ainda não recebidas. Nenhum ajuste decorrente
de feedback humano foi realizado.

### Roteiro disponível para avaliação

1. Abrir o carrinho com produtos disponíveis e usar Finalizar compra.
2. Selecionar endereço, comparar Padrão/Expressa e revisar o resumo.
3. Confirmar os dados e usar cartão fictício aprovado, recusado ou PIX.
4. Conferir o estado exibido e abrir Ver detalhes do pedido; atualizar a página.
5. Repetir a navegação em tela menor e observar progresso, campos e resumo.

O contrato `checkout/CONTRATO.md` contém os comandos e números fictícios para
reproduzir os cenários. A entrevista terá **quatro perguntas sequenciais**;
nenhuma resposta de avaliação foi recebida até este rascunho.

**Pergunta 1/4 — navegação e frete:** ao percorrer Endereço → Entrega →
Pagamento e voltar à entrega antes de confirmar os dados, o resumo e o frete
permaneceram coerentes? Relate o que observou, inclusive se não testou.
**Resposta:** pendente. As perguntas seguintes serão adaptadas à resposta,
sem reiniciar a entrevista ou atribuir aprovação antecipada.

### Conferência do checklist T10 pela IA

| Item do TODO.md | Evidência da implementação | Situação técnica |
|---|---|---|
| Finalizar compra com itens válidos e login | Botão do carrinho, validação e testes de acesso/estoque | Verificado |
| Checkout em etapas com progresso | Quatro templates e navegação HTTP | Funcional verificado; visual pendente |
| Reutilizar os quatro módulos | Chamadas reais de endereço, cotação, pedido e pagamento | Verificado |
| Resumo e revalidação no servidor | Snapshots, Decimal e rejeição de alterações/adulterações | Verificado |
| Cartão/PIX com componentes existentes | Partials, máscaras existentes, QR e testes dos formulários | Servidor verificado; máscaras no navegador pendentes |
| Confirmação com identificador e estado correto | Resultado de aprovação, recusa e PIX pendente | Verificado |
| Atualizar/voltar/reenviar sem duplicar | Chave estável, marcador de baixa e testes de reenvio | Verificado nos testes; sem teste de carga |
| Tratar estados inválidos | Testes de carrinho vazio, login, endereço, estoque e pagamento | Verificado |
| Layout consistente e navegação necessária | Base compartilhada, Bootstrap e CSS responsivo | Inspecionado no código; visual pendente |
| Testes simples de fluxo e autorização | 19 testes T10, serviços reais e CSRF real | Verificado |

Essa conferência técnica não substitui os pareceres humanos das seções 3 e 4.
A versão parcial foi exportada para `relatorio.docx`, mantendo a avaliação humana
pendente. O Markdown permanece como referência editável para consolidar a entrevista.

## 6. Conclusão e avaliação do uso da IA

A IA consegiu concluir bem as tarefas, foram mais de 1000 linhas envolvidas todas revisadas, envolvendo  
várias áreas diferentes, mas ela conseguiu se sair bem, todas as etapas foram implementada
a parte visual ficou bem parecida com a amazon de verdade, em relação ao carrinho e etapas da compra,  
assim como a página de pedidos  

**Parecer final:** T10 aprovada, a IA conseguiu fazer tudo que foi pedido, sem problemas
Os testes passaram bem, nenhum problema foi identificado

---
**Responsável pela avaliação:** Davi  
**Elaboração:** relatório estruturado com auxílio de IA a partir das evidências
técnicas disponíveis; respostas do integrante ainda pendentes.
