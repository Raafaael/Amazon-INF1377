# RELATÓRIO DE AUDITORIA DE DESENVOLVIMENTO ASSISTIDO POR IA

**Projeto:** Amazon — Sistema de Comércio Eletrônico  
**Integrante responsável:** Rafael  
**Semana/período:** entrega semanal “Catálogo e Carrinho”, planejamento inicial de 07/11/2026 (`TODO.md`; não há número de semana definido, mantido o identificador `periodo-2026-11-07` usado na T01)  
**Tarefa atribuída:** T02 — Modelos e cadastro de produtos (models e cadastro administrativo de produtos/categorias)  
**Ferramenta de IA utilizada:** Claude Code (Claude Opus 5.5)  
**Consolidação deste relatório:** Codex, sem alterar as respostas atribuídas a Rafael

**Data da auditoria:** 07/11/2026; consolidação técnica em 10/11/2026
**Situação:** auditoria original concluída; ajustes posteriores verificados tecnicamente e ainda não reavaliados por Rafael

## 1. Introdução e contextualização

O projeto é um e-commerce acadêmico de livros e eletrônicos, feito em Django. A T02 define os models do catálogo, que são o contrato usado pelas tarefas de catálogo público (T03) e carrinho (T04), e o cadastro desses produtos pelo Django Admin. A IA foi usada para planejar, implementar e testar a tarefa. Antes da implementação, o plano passou por iterações de revisão. Esta auditoria reúne a avaliação de Rafael sobre o resultado e a compara com as verificações técnicas realizadas.

## 2. Descrição da tarefa e implementação realizada

**Solicitação (`TODO.md`, T02).** A tarefa pede:
- models de Categoria (com pai/subcategoria), Produto, Livro e Eletronico, além das entidades de apoio;
- registro desses models no Django Admin;
- validação de campos obrigatórios, estoque não negativo e preço maior que R$ 0,00 e menor que R$ 10.000,00 (SRS v1.1, RN-02), registrando a divergência do fluxo A5 do UC01;
- migrações;
- cadastro de pelo menos um Livro e um Eletrônico;
- testes básicos;
- comunicação do contrato dos models a Yuri e Pedro.

Referências: UC01, RF-CAT-01 a 09, RN-01 a 05.

**Implementação produzida pela IA** (base T01 da branch `semana-1`):

| Arquivo | O que contém |
|---|---|
| `catalog/models.py` | `Categoria` (pai opcional, `subcategorias`, bloqueio de ciclos), `Idioma` (tabela), `Autor`, `Editora`, `Fabricante`, `Produto` e as especializações `Livro`/`Eletronico` por herança multi-tabela. O `tipo` é preenchido na criação da instância. Há validador e `CheckConstraint` da faixa de preço, e um `Produto` genérico não pode ser criado. |
| `catalog/admin.py` | Telas de Livro e Eletrônico com seções "Dados gerais" e "Dados específicos"; entidades de apoio com cadastro pelo botão "+"; tela "Produtos" somente para consulta, sem incluir, alterar nem excluir. |
| `catalog/migrations/0001_initial.py` | Migração inicial do catálogo. |
| `catalog/fixtures/catalogo_demo.json` | Dados fictícios: 6 categorias, 3 livros e 3 eletrônicos, um deles sem estoque. |
| `catalog/tests/` | Testes de models, Admin e fixture organizados em `test_models.py`, `test_admin.py` e `test_fixture.py`, com dados comuns em `helpers.py`. A auditoria original cobria 35 testes; há 36 testes específicos dessas partes após os ajustes. |
| `catalog/CONTRATO.md` | Contrato para os demais integrantes: campos, consultas, regras garantidas e pendências. |

Decisões tomadas por Rafael durante o planejamento: Idioma como tabela e dados de demonstração por fixture.

## 3. Auditoria da implementação

### 3.1. Modelagem e relacionamentos

**O que foi verificado:** análise técnica da IA:
- `python manage.py check` não apontou problemas;
- `makemigrations --check --dry-run` não indicou mudanças pendentes;
- testes de subcategorias, ciclo de categorias, proteção contra exclusão de categoria em uso e consulta conjunta de Livro/Eletrônico por `Produto` passaram.

**Avaliação do integrante:** “Tudo como esperado.”  
**Problemas identificados:** nenhum relatado.  
**Sugestões de melhoria:** nenhuma informada.  
**Resultado:** aprovada.

### 3.2. Validações (preço, estoque, campos obrigatórios, autor)

**O que foi verificado:** análise técnica da IA. Os testes automatizados passaram para:
- preço 0, negativo, 10.000 e com três casas decimais (rejeitados);
- preço 0,01 e 9.999,99 (aceitos);
- bloqueio no banco por `CheckConstraint`;
- estoque negativo;
- campos obrigatórios gerais e específicos;
- livro sem autor no Admin.

O fluxo A5 do UC01 não foi implementado: preços fora da faixa são rejeitados sem confirmação.

**Avaliação do integrante:** concordou com a rejeição do preço fora da faixa sem confirmação. Informou que testou as validações manualmente e não percebeu problemas.  
**Problemas identificados:** nenhum relatado. A divergência documental A5 × RN-02 continua registrada.  
**Sugestões de melhoria:** nenhuma informada.  
**Resultado:** aprovada.

### 3.3. Cadastro no Django Admin e dados de demonstração

**O que foi verificado:** análise técnica da IA:
- testes de cadastro e edição de Livro/Eletrônico pelo Admin;
- rejeição de edição com preço inválido, preservando o valor anterior;
- bloqueio do Admin para usuário comum;
- tela "Produtos" somente leitura (incluir, alterar e excluir retornam 403);
- `loaddata catalogo_demo` carregou 27 objetos (3 livros, 3 eletrônicos, 6 categorias);
- testes de coerência da fixture: cada produto tem o filho do seu tipo e cada livro tem autor.

**Avaliação do integrante:** fez testes manuais de cadastro/edição no Admin, da tela de Produtos e da fixture, e não percebeu problemas.  
**Problemas identificados:** nenhum relatado.  
**Sugestões de melhoria:** nenhuma informada.  
**Resultado:** aprovada.

### 3.4. Contrato para os demais integrantes (`catalog/CONTRATO.md`)

**O que foi verificado:** inspeção do documento pela IA, que corrigiu um import ausente em um exemplo.  
**Avaliação do integrante:** não houve pergunta específica sobre o contrato. Na síntese, Rafael disse que não alteraria nada na tarefa.  
**Problemas identificados:** não avaliado especificamente.  
**Sugestões de melhoria:** nenhuma informada.  
**Resultado:** não avaliada / inconclusiva (sem avaliação específica do integrante e ainda não validada por Yuri e Pedro).

### 3.5. Ajuste posterior: imutabilidade do tipo do produto

**O que foi verificado:** após a auditoria original, a análise técnica da IA identificou que atualizar um `Produto` pelo objeto pai permitia trocar `tipo` sem trocar sua especialização. `Produto.save()` passou a rejeitar essa troca; atualizar outros campos, como `estoque`, continua permitido. O teste `test_tipo_nao_pode_ser_alterado_pelo_produto_pai` cobre a regra. A proteção não se aplica a `QuerySet.update()` nem ao carregamento bruto de fixtures.

**Avaliação do integrante:** Rafael ainda não reavaliou esse ajuste.

**Problemas identificados:** a inconsistência possível pela atualização do objeto pai foi corrigida; operações que não chamam `save()` continuam fora dessa proteção.

**Sugestões de melhoria:** nenhuma sugestão humana posterior registrada.
**Resultado:** aprovada com ressalvas pela análise técnica da IA; reavaliação humana pendente.

### 3.6. Ajuste posterior: organização dos testes

**O que foi verificado:** após uma sugestão de Rafael para dividir os testes, os 35 casos existentes foram movidos de `catalog/tests.py` para `catalog/tests/test_models.py`, `test_admin.py` e `test_fixture.py`, com apoio de `helpers.py`. O teste de imutabilidade elevou a quantidade atual dessas partes a 36. Em 10/11/2026, `python manage.py test catalog.tests.test_models catalog.tests.test_admin catalog.tests.test_fixture` executou **36 testes, todos OK**.

**Avaliação do integrante:** a sugestão de reorganização veio de Rafael; ele ainda não avaliou os arquivos reorganizados.

**Problemas identificados:** nenhum erro técnico identificado nos 36 testes executados.

**Sugestões de melhoria:** dividir os testes por responsabilidade, conforme a observação registrada de Rafael.
**Resultado:** aprovada com ressalvas pela análise técnica da IA; reavaliação humana pendente.

## 4. Síntese dos achados

| Etapa | Evidência/observação | Resultado | Pendências |
|---|---|---|---|
| Modelagem | Integrante: “tudo como esperado”. IA: `check` e testes de relações OK | Aprovada | — |
| Validações | Integrante testou manualmente e concordou com a rejeição sem confirmação. IA: testes de limites e constraint OK | Aprovada | Corrigir na documentação a divergência A5 × RN-02 |
| Admin e fixture | Integrante fez testes manuais sem problemas. IA: testes de Admin e fixture OK | Aprovada | Sugerir ao Breno a instrução de `loaddata` no README |
| Contrato | Inspeção da IA; sem avaliação específica do integrante | Inconclusiva | Validação por Yuri e Pedro ao usarem os models |
| Imutabilidade do tipo, posterior | IA: teste de troca do tipo pelo objeto pai passou | Aprovada com ressalvas | Reavaliação de Rafael; operações em massa não passam por `save()` |
| Organização dos testes, posterior | Sugestão de Rafael; IA: 36 testes específicos passaram em 10/11/2026 | Aprovada com ressalvas | Reavaliação dos arquivos reorganizados por Rafael |

Na auditoria original, `python manage.py test catalog` executou 35 testes, todos OK. A verificação técnica de 10/11/2026 executou 36 testes específicos de models, Admin e fixture, todos OK.

## 5. Recomendações

**Do integrante:** nenhuma alteração sugerida.

**Sugestões técnicas adicionais da IA** (não avaliadas pelo integrante):
- decidir em grupo a necessidade de um campo "ativo" (citado em RF-FLT-03/UC03) e de imagem do produto;
- definir formato e unicidade do ISBN;
- corrigir no UC01 o fluxo A5;
- usar a fixture só em banco local de demonstração, porque ela sobrescreve registros com as mesmas PKs.

Na avaliação original, Rafael não indicou correções. Posteriormente, a IA corrigiu a troca indevida de `tipo` pelo objeto pai e reorganizou os testes após sugestão de Rafael. Esses dois ajustes estão tecnicamente verificados e ainda não foram reavaliados por ele.

## 6. Conclusão e avaliação do uso da IA

A modelagem ficou como eu esperava. Concordo em rejeitar preços fora da faixa sem pedir confirmação. Testei as validações e fiz testes manuais dos fluxos de cadastro e edição no Admin, da tela de Produtos e dos dados de demonstração, e não percebi problemas. Não alteraria nada na implementação. Tivemos uma boa etapa de planejamento, com algumas iterações que melhoraram o plano final, e chegamos a um bom estado.

**Parecer final:** T02 aprovada na auditoria original nas etapas de modelagem, validações e cadastro pelo Admin, com base nos testes automatizados e nos testes manuais relatados. O contrato não teve avaliação específica. Os dois ajustes posteriores foram verificados tecnicamente, mas ainda não receberam parecer humano de Rafael.

---
**Responsável pela avaliação:** Rafael  
**Elaboração:** relatório estruturado com auxílio de IA a partir das evidências e respostas do integrante.
