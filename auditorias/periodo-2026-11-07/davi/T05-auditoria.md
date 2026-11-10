# RELATÓRIO DE AUDITORIA DE DESENVOLVIMENTO ASSISTIDO POR IA

**Projeto:** Amazon — Sistema de Comércio Eletrônico

**Integrante responsável:** Davi

**Semana/período:** periodo-2026-11-07, identificador das auditorias desta entrega

**Tarefa atribuída:** T05 — Interface visual da Home, produto, carrinho e login

**Ferramenta de IA utilizada:** Codex

**Data da auditoria inicial:** 08/11/2026

**Atualização técnica:** 09/11/2026

**Situação:** parcial — integração técnica verificada; revisão visual atual e avaliação humana da integração pendentes.

## 1. Introdução e contextualização

A T05 prevê a interface da aplicação Django para catálogo, detalhe de produto, carrinho e login. Na avaliação inicial, o carrinho ainda era um placeholder. Na versão atual da `main`, os models, as operações e as rotas de Pedro já existem e os templates estão integrados. A pendência anterior de backend foi resolvida.

Este relatório preserva as respostas humanas de 08/11 e acrescenta as evidências técnicas de 09/11. Os resultados dos testes executados pelo agente não representam aprovação humana da versão atual.

## 2. Descrição da tarefa e implementação realizada

O layout compartilhado utiliza `templates/base.html`, Bootstrap e `static/css/site.css`. A Home apresenta produtos, busca, filtros, categorias e paginação; o detalhe mostra as informações do tipo, disponibilidade e formulário de quantidade. O login e o logout usam as views nativas do Django.

Os formulários do produto e do carrinho utilizam as rotas reais `cart:add`, `cart:update` e `cart:remove`, com POST e CSRF. A view de consulta fornece `itens` e `total`. A integração funcional foi implementada por Pedro após a primeira auditoria; nesta rodada, foram conferidos seus campos e endpoints, sem recriar as regras de negócio.

Na atualização da T05, o agente realizou os seguintes ajustes:

- Preservou a palavra pesquisada ao enviar o formulário de filtros.
- Preservou a categoria nos links de paginação quando ela vem de um parâmetro da URL.
- Corrigiu as mensagens de erro para o estilo `alert-danger` do Bootstrap e o anúncio acessível de erro.
- Preservou o nome de usuário quando o login falha e evitou que o link do cabeçalho retornasse ao próprio login após autenticar.
- Acrescentou uma indicação de que quantidade zero remove o item e identificou os controles de quantidade pelo produto.
- Documentou os campos, contextos, métodos e rotas em `cart/CONTRATO.md`.
- Criou três testes de integração em `catalog/tests/test_interface.py`.

Davi informou em 09/11 que já combinou os campos e as rotas com Pedro. O checkbox correspondente da T04 já estava modificado localmente antes desta rodada; essa alteração foi preservada.

## 3. Auditoria da implementação

### 3.1. Layout e navegação

**O que foi verificado:** inspeção dos templates e do CSS. A navegação aponta para rotas existentes, e o checkout aparece como botão desativado com a indicação de indisponibilidade. Busca e filtros preservam seus dados nos cenários automatizados.

**Avaliação do integrante:** na primeira pergunta de 08/11, respondeu “Atende ao esperado” sobre a organização visual. Não foi recebida nova avaliação visual após a integração posterior do carrinho.

**Problemas identificados:** o formulário de filtros perdia a busca, a paginação podia perder a categoria passada na query e a classe de erro não correspondia ao Bootstrap. Esses pontos foram corrigidos nesta rodada; as regressões de busca e categoria foram verificadas por testes.

**Sugestões de melhoria:** o integrante respondeu “Sem sugestões” na entrevista inicial.

**Resultado:** aprovada com ressalvas no escopo técnico verificado; aparência atual sem nova avaliação humana.

### 3.2. Produto, login e operações do carrinho

**O que foi verificado:** o teste usa `Client(enforce_csrf_checks=True)` e lê os campos e ações do HTML renderizado. Verifica rejeição de POST sem CSRF, redirecionamento anônimo ao login, preservação de usuário e destino após senha inválida, retorno ao produto após autenticar, erro de estoque, adição de duas unidades, atualização para três, remoção, total zero e logout. Com um produto de R$ 50,00, os totais esperados de R$ 100,00 e R$ 150,00 foram confirmados.

**Avaliação do integrante:** na pergunta 2 de 08/11, respondeu “Está claro; não testei os fluxos”. Isso se referia à interface antiga, que informava a dependência do backend. Davi confirmou o alinhamento com Pedro em 09/11, mas não relatou teste pessoal da versão integrada nesta sessão.

**Problemas identificados:** não houve falha nos cenários automatizados executados após os ajustes. A confirmação de remoção no navegador usa JavaScript e não é exercitada pelo cliente de testes do Django.

**Sugestões de melhoria:** nenhuma nova sugestão humana recebida.

**Resultado:** integração técnica verificada; avaliação humana atual inconclusiva.

### 3.3. Responsividade e confirmação de remoção

**O que foi verificado:** a inspeção do código confirmou os breakpoints do layout, o menu recolhível, os campos de quantidade e o `confirm()` antes de remover, inclusive ao atualizar com zero. Essa inspeção não substitui executar a interface em um navegador.

**Avaliação do integrante:** não recebida para a versão integrada em desktop e telas pequenas.

**Problemas identificados:** o Computer Use encerrou a conferência por não conseguir determinar com segurança a URL atual do Chrome no Windows. Não houve captura válida das telas, teste do menu móvel ou exercício do diálogo de confirmação nesta rodada.

**Sugestões de melhoria:** realizar a revisão visual quando o acesso ao navegador estiver disponível ou registrar o teste manual do integrante.

**Resultado:** inconclusiva quanto à observação visual e aos diálogos do navegador.

## 4. Síntese dos achados

| Etapa | Evidência | Resultado e pendência |
|---|---|---|
| Busca e filtros | Formulário renderizado preserva `q` e categoria | Regressão corrigida e testada |
| Paginação | Categoria da query mantida ao seguir o link Próxima | Regressão corrigida e testada |
| Login e carrinho | Fluxo dos formulários com CSRF real e valores conferidos | Verificação técnica aprovada |
| Contrato com Pedro | Relato explícito de Davi e rotas conferidas no código | Documentado em `cart/CONTRATO.md` |
| Responsividade e confirmação | Inspeção do código; acesso ao Chrome interrompido pelo Computer Use | Revisão visual pendente |
| Avaliação humana atual | Respostas iniciais preservadas; sem relato pessoal dos fluxos novos | Não atribuir aprovação à versão integrada |

**Comandos e resultados em 09/11/2026:**

- `python manage.py check`: sem problemas identificados.
- `python manage.py test --verbosity 1`: 73 testes aprovados, incluindo os três testes novos da interface.
- `git diff --check`: sem erros de whitespace.

Os comandos Django foram executados em um ambiente temporário com **Django 5.2.19**, instalado a partir de `requirements.txt`. A `.venv` existente usa Django 6.1.3 e o Python padrão usa 6.1.1; essas instalações foram preservadas. Os testes criaram e destruíram seu próprio banco. Um servidor temporário para a tentativa visual usou outro SQLite e a fixture de demonstração, sem alterar o banco local de trabalho; esse servidor foi encerrado.

## 5. Recomendações

Conferir Home, produto, login e carrinho em desktop e celular, especialmente menu recolhível, campos, mensagens, valores e confirmação/cancelamento de remoção. Confirmar visualmente que o checkout está indisponível.

A avaliação inicial da T05 teve três perguntas respondidas, encerradas em 08/11: organização visual (“Atende ao esperado”), clareza da pendência e teste (“Está claro; não testei os fluxos”) e melhorias/avaliação final (“Sem sugestões”). Essas respostas não foram substituídas por opiniões presumidas. Não houve nova entrevista nesta atualização técnica.

O Markdown é o relatório editável desta rodada. A conversão para DOCX com renderização e conferência visual não foi realizada neste ambiente.

## 6. Conclusão e avaliação do uso da IA

Na avaliação inicial, a organização visual atendeu ao que eu esperava. Informei que a pendência do carrinho estava clara e que não tinha testado os fluxos. Não apresentei sugestões. Agora confirmei que já alinhei os campos e as rotas com Pedro, mas ainda não registrei minha avaliação pessoal da interface integrada nem uma opinião final específica sobre a contribuição da IA. Essa parte da avaliação permanece incompleta.

**Parecer final:** a dependência anterior do backend foi resolvida e a integração técnica passou nos testes. A auditoria permanece parcial quanto à revisão visual atual e à avaliação humana da integração.

---
**Responsável pela avaliação:** Davi

**Elaboração:** relatório estruturado com auxílio de IA a partir das evidências e respostas do integrante.
