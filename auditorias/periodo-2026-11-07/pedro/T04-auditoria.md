# RELATÓRIO DE AUDITORIA DE DESENVOLVIMENTO ASSISTIDO POR IA

**Projeto:** Amazon — Sistema de Comércio Eletrônico  
**Integrante responsável:** Pedro  
**Semana/período:** entrega semanal “Catálogo e Carrinho”, planejamento inicial de 07/11/2026 (`TODO.md`; não há número de semana definido, mantido o identificador `periodo-2026-11-07` usado nas demais auditorias)  
**Tarefa atribuída:** T04 — Funcionalidade do carrinho (models, regras e operações do carrinho)  
**Ferramenta de IA utilizada:** Claude Code (Claude Opus 5.5)  
**Data da auditoria:** 08/11/2026  
**Situação:** concluída

## 1. Introdução e contextualização

O projeto é um e-commerce acadêmico de livros e eletrônicos, feito em Django. A T04 implementa o carrinho de compras do usuário autenticado, usando o model `catalog.Produto` definido na T02 e as telas criadas na T05. A IA foi usada para levantar a tarefa no `TODO.md`, apontar as decisões não definidas na documentação, implementar o app `cart`, escrever os testes e verificar o fluxo no navegador. Esta auditoria reúne a minha avaliação do resultado e a compara com as verificações técnicas realizadas.

## 2. Descrição da tarefa e implementação realizada

**Solicitação (`TODO.md`, T04).** A tarefa pede:
- models `Carrinho` e `ItemCarrinho`, associados ao usuário autenticado e ao `Produto`, com migrações;
- consulta do carrinho, incluindo o estado vazio;
- adicionar produto com quantidade inteira positiva e disponível em estoque, somando quantidades quando o produto já estiver no carrinho;
- alterar quantidade e remover o item, com confirmação na interface antes de remover;
- `subtotal = preço × quantidade` e `total = soma dos subtotais`, com total zero no carrinho vazio;
- autenticação obrigatória e isolamento entre usuários;
- operações POST com CSRF e mensagens claras;
- testes para inclusão repetida, estoque insuficiente, quantidade inválida, remoção, total, carrinho vazio e isolamento.

Referências: UC04, UC05, UC11; RF-CAR-01 a 09; RN-06 a RN-08.

**Decisões tomadas antes da implementação** (pontos não definidos nos artefatos):
- O preço **não é armazenado** no `ItemCarrinho`; é sempre lido do `Produto`. O preço registrado no momento da compra fica para o `ItemPedido`, fora desta entrega.
- Alterar a quantidade para **0 remove o item**; valores negativos ou não numéricos são rejeitados.
- A IA pôde editar os templates da T05 (Davi) **apenas** para ligar formulários e botões às rotas do carrinho.

**Implementação produzida pela IA** (base da branch `semana-1`):

| Arquivo | O que contém |
|---|---|
| `cart/models.py` | `Carrinho` (um por usuário, `OneToOneField`) e `ItemCarrinho` (produto único por carrinho e quantidade ≥ 1, também como restrições do banco). Regras de adicionar/somar, validação de estoque, alteração de quantidade, subtotal e total. |
| `cart/migrations/0001_initial.py` | Migração inicial do carrinho. |
| `cart/views.py` / `cart/urls.py` | `cart:detail` (login obrigatório) e rotas POST `cart:add`, `cart:update` e `cart:remove`, com mensagens de sucesso/erro. Itens de outro usuário retornam 404. Usuário anônimo que tenta adicionar é levado ao login e volta à página do produto. |
| `templates/catalog/product_detail.html` | Formulário de adicionar ao carrinho ligado à rota, com CSRF. |
| `templates/cart/detail.html` | Formulário de atualizar quantidade e botão Remover com confirmação; removidos os avisos provisórios de “aguardando integração”. |
| `cart/tests.py` | 25 testes automatizados (alguns com vários valores por `subTest`). |

## 3. Auditoria da implementação

### 3.1. Models e regras de negócio

**O que foi verificado:** testes automatizados de subtotal, total, carrinho vazio, quantidade inválida, inclusão repetida e estoque; teste manual no navegador realizado pela IA (adicionar 2 unidades, alterar para 3, tentar exceder o estoque). Testei a aplicação localmente.  
**Avaliação do integrante:** as regras funcionaram como eu esperava; o único ponto de atenção que encontrei está na interface (seção 3.2).  
**Problemas identificados:** nenhum relatado nas regras.  
**Sugestões de melhoria:** nenhuma para esta etapa.  
**Resultado:** aprovada.

### 3.2. Interface e integração com as telas

**O que foi verificado:** fluxo no navegador (adicionar pela página do produto, atualizar, remover cancelando e confirmando, mensagens de erro de estoque); meu teste manual.  
**Avaliação do integrante:** encontrei uma inconsistência: alterar a quantidade para 0 remove o item, assim como o botão Remover, mas apenas o botão pedia confirmação. Como são duas formas de exclusão, ambas deveriam ter o mesmo fluxo. Após a correção, o comportamento fez sentido, e considerei bons os fluxos de adicionar pela página do produto, as mensagens e o redirecionamento ao login.  
**Problemas identificados:** remoção por quantidade 0 sem confirmação, contrariando o checklist da T04 e o UC05. **Corrigido** no `templates/cart/detail.html`: a quantidade 0 agora exibe a mesma confirmação do botão Remover; cancelar mantém o item. Verificado pela IA no navegador e **reavaliado por mim**.  
**Sugestões de melhoria:** ver seção 3.4.  
**Resultado:** aprovada (problema corrigido e reavaliado).

### 3.3. Testes automatizados

**O que foi verificado (análise técnica da IA):** `python manage.py test cart` — 25 testes, todos aprovados. `python manage.py check` sem problemas. Na suíte completa (`python manage.py test`), há **1 falha preexistente** fora da T04: `catalog.tests.test_views` procura o texto “Informações do livro”, mas o template exibe “Sobre o livro”.  
**Avaliação do integrante:** não avaliei os testes automatizados especificamente.  
**Problemas identificados:** nenhum nos testes do carrinho; a falha do catálogo pertence às tarefas T03/T05.  
**Sugestões de melhoria:** não houve.  
**Resultado:** não avaliada pelo integrante (evidência técnica favorável).

### 3.4. Sugestões de evolução do carrinho

Registradas como recomendações minhas, **não implementadas** por estarem fora do checklist da T04 e envolverem o `base.html` (T05):
- uma segunda “visão” do carrinho, como um painel sobre a página exibido ao passar o mouse (mouseover);
- um contador junto ao link “Meu carrinho” no menu, com a quantidade de itens diferentes no carrinho.

## 4. Síntese dos achados

| Etapa | Evidência / observação | Resultado | Pendências |
|---|---|---|---|
| Models e regras | Testes automatizados; teste no navegador (IA); meu teste manual | Aprovada | — |
| Interface e integração | Encontrei remoção por quantidade 0 sem confirmação; corrigida e reavaliada | Aprovada | Avisar o Davi sobre as edições nos templates |
| Testes automatizados | 25 testes do carrinho aprovados (IA); 1 falha preexistente no catálogo | Não avaliada pelo integrante | Falha do catálogo para T03/T05 |
| Evolução | Prévia por mouseover e contador no menu (minhas sugestões) | — | Decisão do grupo para entregas futuras |

## 5. Recomendações

**Minhas recomendações:**
- Avaliar, em uma próxima entrega, a prévia do carrinho por mouseover e o contador de itens no menu.

**Sugestões técnicas adicionais da IA:**
- Informar ao Davi as alterações feitas em `templates/cart/detail.html` e `templates/catalog/product_detail.html`.
- Alinhar com Yuri/Davi a falha preexistente em `catalog.tests.test_views` (“Informações do livro” × “Sobre o livro”).
- Os models do carrinho não foram registrados no Django Admin, pois isso não consta no checklist.

O problema da quantidade 0 foi corrigido e reavaliado; as demais recomendações permanecem pendentes.

## 6. Conclusão e avaliação do uso da IA

A ajuda da IA nesta tarefa foi muito boa e bem assertiva. Testei o carrinho e identifiquei uma inconsistência: a remoção pela quantidade 0 não pedia confirmação, diferente do botão Remover. Ela foi corrigida, e o fluxo passou a fazer sentido. Também registrei melhorias que gostaria de ver no carrinho, como a prévia ao passar o mouse e o contador de itens no menu. Ainda assim, não confio 100% no resultado, porque a aplicação funciona como uma caixa preta para mim: consigo ver o resultado, mas não o que foi feito para chegar até ele.

**Parecer final:** aprovada com ressalvas — as etapas avaliadas atendem ao checklist da T04 e o problema encontrado foi corrigido e reavaliado, mas os testes automatizados e o código não foram revisados por mim, e declaro confiança parcial no resultado.

---
**Responsável pela avaliação:** Pedro  
**Elaboração:** relatório estruturado com auxílio de IA a partir das evidências e respostas do integrante.
