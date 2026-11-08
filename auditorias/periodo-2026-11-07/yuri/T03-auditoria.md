# RELATÓRIO DE AUDITORIA DE DESENVOLVIMENTO ASSISTIDO POR IA

**Projeto:** Amazon — Sistema de Comércio Eletrônico  
**Integrante responsável:** Yuri  
**Semana/período:** entrega semanal “Catálogo e Carrinho”, planejamento inicial de 07/11/2026 (`TODO.md`; não há número de semana definido)  
**Tarefa atribuída:** T03 — Catálogo público, navegação e filtros  
**Ferramenta de IA utilizada:** Copilot SDK em VS Code  
**Data da auditoria:** 08/11/2026  
**Situação:** concluída

## 1. Introdução e contextualização

Esta auditoria registra a implementação da parte de Yuri na tarefa T03, focada na vitrine pública do catálogo. O objetivo foi verificar se a home, a navegação por categorias, a busca, os filtros e a página de detalhe cumprem o escopo previsto em `TODO.md` e no contrato do app `catalog`, sem introduzir critérios não modelados no domínio.

A avaliação foi consolidada com a revisão do integrante, que confirmou que a tarefa atendeu ao esperado e que o auxílio da IA foi útil.

## 2. Descrição da tarefa e implementação realizada

O `TODO.md` exige que Yuri substitua o placeholder de Breno por uma home de catálogo funcional, com categorias, subcategorias, detalhe do produto, busca simples, filtros por preço e fabricante (somente eletrônicos), tratamento de resultados vazios e paginação quando houver mais de 50 itens. Também pede que os dados sejam expostos com clareza às templates, sem HTML montado dentro das views.

A implementação foi realizada em `catalog/views.py` e `catalog/urls.py`, além dos templates `templates/catalog/index.html` e `templates/catalog/product_detail.html`. A home passou a consultar produtos reais do banco, aplicar filtros combinados e renderizar página de detalhe. A navegação por categorias foi construída com rotas específicas para `categoria/<id>/` e `produto/<id>/`.

## 3. Auditoria da implementação

### 3.1. Catálogo, busca e filtros

**O que foi verificado:** execução de `python manage.py test catalog` e inspeção do código em `catalog/views.py` e `templates/catalog/index.html`.  
**Avaliação do integrante:** “Atendeu bem.” O catálogo, a busca e os filtros atenderam ao que eu esperava, inclusive a preservação dos valores de preço após a pesquisa.  
**Problemas identificados:** nenhum relatado.  
**Sugestões de melhoria:** nenhuma sugestão relevante no momento.  
**Resultado:** aprovada.

### 3.2. Navegação por categorias e produto

**O que foi verificado:** inspeção das rotas de categoria e detalhe do produto e testes automatizados da funcionalidade de listagem, categoria e visualização do item.  
**Avaliação do integrante:** “Nenhum problema.” A navegação por categorias e a página de detalhe do produto não apresentaram comportamento inesperado.  
**Problemas identificados:** nenhum relatado.  
**Sugestões de melhoria:** nenhuma sugestão específica.  
**Resultado:** aprovada.

### 3.3. Melhoria geral e avaliação da IA

**O que foi verificado:** respostas da auditoria em sequência, que apontaram que a implementação atendia ao escopo e que o auxílio da IA foi bem avaliado.  
**Avaliação do integrante:** “Nada a melhorar.” e “Foi muito útil.” O integrante considerou o resultado satisfatório e não identificou correções pendentes.  
**Problemas identificados:** nenhum relatado.  
**Sugestões de melhoria:** nenhuma no contexto da tarefa atual.  
**Resultado:** aprovada.

## 4. Síntese dos achados

| Etapa | Evidência/observação | Resultado | Pendência |
|---|---|---|---|
| Catálogo, busca e filtros | Atendeu ao que era esperado; valores de preço são preservados corretamente | Aprovada | Nenhuma |
| Navegação por categorias e produto | Não houve problema observado na navegação e detalhe | Aprovada | Nenhuma |
| Avaliação geral da IA | O integrante definiu como “muito útil” e sem melhorias exigidas | Aprovada | Nenhuma |

## 5. Recomendações

**Recomendação do integrante:** nenhuma melhoria específica foi indicada na revisão final da tarefa.  
**Análise técnica da IA:** manter o comportamento atual de preservação dos valores de busca, continuar cobrindo filtros por preço e categoria em testes e preservar a simplicidade da implementação conforme o escopo do projeto.

## 6. Conclusão e avaliação do uso da IA

A utilização da IA me ajudou muito nessa tarefa. O catálogo ficou funcional, a busca e os filtros atenderam ao que eu esperava, e a navegação por categoria e a página de detalhe não apresentou problemas. Não tenho sugestões de melhoria relevantes e considero o auxílio da IA muito útil.

Também foi validado por testes automatizados do app `catalog`, com resultado positivo. O feedback do integrante foi consistente com a implementação e não apontou correções pendentes para o escopo desta tarefa.

**Parecer final:** aprovada.

---
**Responsável pela avaliação:** Yuri  
**Elaboração:** relatório estruturado com auxílio de IA a partir das evidências, testes executados e respostas do integrante.
