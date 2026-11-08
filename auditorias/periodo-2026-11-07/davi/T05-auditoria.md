# RELATÓRIO DE AUDITORIA DE DESENVOLVIMENTO ASSISTIDO POR IA

**Projeto:** Amazon — Sistema de Comércio Eletrônico  
**Integrante responsável:** Davi  
**Semana/período:** periodo-2026-11-07 (identificador da pasta de auditorias existente)  
**Tarefa atribuída:** T05 — Interface visual da Home, produto, carrinho e login  
**Ferramenta de IA utilizada:** Codex  
**Data da auditoria:** 08/11/2026  
**Situação:** parcial — interface preparada; integração funcional do carrinho depende do app `cart`.

## 1. Introdução e contextualização

A tarefa T05 prevê as telas de catálogo, detalhe de produto, carrinho e login para a aplicação Django. Esta auditoria registra a implementação visual realizada, as verificações técnicas disponíveis e as respostas de Davi. As operações do carrinho ainda não estão implementadas no backend.

## 2. Descrição da tarefa e implementação realizada

A tarefa solicita um layout reutilizável, vitrine responsiva, cards de produtos, página de detalhes com quantidade e adição ao carrinho, tela de carrinho, login nativo do Django e integração com as rotas dos apps de catálogo e carrinho.

Foram criados `templates/base.html`, `templates/cart/detail.html` e `static/css/site.css`; os templates de catálogo, produto e login foram adaptados para usar a base comum. O detalhe exibe quantidade e disponibilidade, mas o botão de adição está desativado até existir uma rota de backend. A rota atual do carrinho foi ajustada para renderizar o estado visual vazio; sem models e operações de carrinho, não exibe itens nem permite alterar quantidades ou remover produtos.

## 3. Auditoria da implementação

### 3.1. Layout, catálogo e navegação

**O que foi verificado:** inspeção dos templates e CSS; `python manage.py check` não identificou problemas; `git diff --check` não apontou erros de whitespace. A pessoa avaliadora informou que a organização visual atende ao esperado.

**Avaliação do integrante:** “Atende ao esperado”.

**Problemas identificados:** nenhum relatado pelo integrante.

**Sugestões de melhoria:** nenhuma sugestão apresentada.

**Resultado:** aprovada com ressalvas — a avaliação humana foi favorável, mas não houve validação visual pelo navegador nesta auditoria.

### 3.2. Página de produto e login

**O que foi verificado:** templates inspecionados; o login usa POST e CSRF e apresenta mensagens de erro. O detalhe mostra informações específicas de livros e eletrônicos. A adição ao carrinho não pode ser exercida sem a rota do backend.

**Avaliação do integrante:** não houve resposta separada sobre estas telas; a avaliação geral da organização visual foi “Atende ao esperado”.

**Problemas identificados:** integração de adição ao carrinho pendente.

**Sugestões de melhoria:** nenhuma sugestão apresentada.

**Resultado:** aprovada com ressalvas.

### 3.3. Tela e integração do carrinho

**O que foi verificado:** a rota existente foi conectada ao template da tela. O código de `cart/models.py` está vazio e `cart/urls.py` contém somente a rota de consulta; não existem rotas para adicionar, alterar ou remover itens. As ações dependentes do backend não foram habilitadas.

**Avaliação do integrante:** informou que a pendência está clara e que não testou os fluxos.

**Problemas identificados:** carrinho sem implementação funcional no backend; a tela de itens e suas ações só poderá ser integrada quando Pedro definir os dados e URLs.

**Sugestões de melhoria:** nenhuma sugestão apresentada.

**Resultado:** inconclusiva quanto ao fluxo funcional; a apresentação do estado vazio está implementada.

## 4. Síntese dos achados

| Etapa | Evidência/observação | Resultado | Pendência |
|---|---|---|---|
| Layout e navegação | Avaliação humana: atende ao esperado; check Django passou | Aprovada com ressalvas | Conferência visual no navegador não realizada |
| Produto e login | Templates atualizados; controles e CSRF presentes | Aprovada com ressalvas | Adição ao carrinho aguarda backend |
| Carrinho | Tela vazia renderiza; integrante confirmou que a pendência está clara e não testou fluxos | Inconclusiva | Models, operações e URLs de Pedro |
| Avaliação da contribuição da IA | Não foi expressa opinião final sobre a contribuição | Inconclusiva | Avaliação humana não registrada |

## 5. Recomendações

**Recomendação técnica da IA:** após Pedro implementar models, operações e URLs, integrar os formulários de adição, alteração de quantidade e remoção com os nomes reais do contrato do app `cart`. Em seguida, verificar os fluxos autenticados e o estado com itens.

Davi informou não ter sugestões adicionais. A suíte de testes não foi executada; somente `python manage.py check` e `git diff --check` foram verificados.

## 6. Conclusão e avaliação do uso da IA

A organização visual atende ao que eu esperava. Informei que a interface deixa clara a pendência do carrinho e que não testei esses fluxos. Não apresentei sugestões de melhoria. Não registrei uma avaliação final sobre a contribuição da IA, então essa parte da auditoria permanece incompleta. A integração funcional do carrinho também depende da implementação do backend.

**Parecer final:** compatível com as evidências e respostas recebidas; tarefa parcialmente implementada e auditoria parcial.

---
**Responsável pela avaliação:** Davi  
**Elaboração:** relatório estruturado com auxílio de IA a partir das evidências e respostas do integrante.
