# TODO.md — Entrega semanal: Catálogo e Carrinho

> **Projeto:** Amazon (e-commerce acadêmico)  
> **Planejamento inicial:** 07/11/2026  
> **Prazo do professor:** a preencher pelo grupo  
> **Situação inicial:** repositório recém-criado, sem aplicação implementada.  
> **Documentação de referência:** `AGENTS.md`, `context.md` (ou `context_revisado.md`, até ser renomeado), SRS v1.1 e casos de uso UC01–UC05/UC11.

## 1. Objetivo desta entrega

Construir **a primeira versão executável e navegável** do site inspirado em um e-commerce, limitada a:

1. **Página inicial/catálogo:** listar livros e eletrônicos, navegar por categorias, pesquisar e aplicar filtros essenciais.
2. **Página de produto:** consultar dados do item e escolher quantidade para adicionar ao carrinho.
3. **Carrinho:** adicionar, consultar, alterar quantidade e remover produtos, exibindo subtotais e total.
4. **Cadastro administrativo básico de produtos:** suficiente para alimentar e demonstrar o catálogo.
5. **Inicialização local do projeto:** instalação reproduzível e execução por qualquer integrante.

**Não implementar nesta semana:** checkout/finalização de compra, pedidos, pagamentos, PIX, endereços/CEP, frete, entrega, avaliações completas, listas de desejos, painel administrativo personalizado ou telas adicionais. Essas funções pertencem ao escopo geral, mas **não** à tarefa semanal atual.

### Arquitetura desta semana

- **Python + Django** como base prática para iniciar a implementação.
- **Django Templates + HTML/CSS/JavaScript e Bootstrap** para a interface; sem React.
- **Django ORM** para os models e consultas; banco relacional.
- **Banco:** MySQL é uma **proposta** registrada no contexto, ainda não confirmação definitiva. Para o primeiro `runserver`, é aceitável usar o **SQLite padrão do Django de forma provisória**, caso MySQL ainda não esteja configurado; documentar isso no README e alinhar antes de estabelecer o banco final. Não instalar MySQL nem dependências de conexão sem a decisão do grupo.
- **Execução local com `.venv` e `requirements.txt`**, sem Docker, serviços de nuvem ou arquitetura de microsserviços.
- **Autenticação nativa do Django:** catálogo consultável; ações pessoais do carrinho exigem login. Nesta entrega basta uma tela de login simples e usuários criados para demonstração; não desenvolver um módulo completo de cadastro/perfil.

## 2. Integrantes e ordem de trabalho

| ID | Responsável | Tarefa desta semana | Dependência principal |
|---|---|---|---|
| **T01** | **Breno** | Inicialização do Django, estrutura mínima e instruções de execução | Nenhuma; **primeiro** |
| **T02** | **Rafael** | Models e cadastro administrativo de produtos/categorias | T01 |
| **T03** | **Yuri** | Navegação, listagem, detalhes, busca e filtros do catálogo | T01 e modelos de T02 |
| **T04** | **Pedro** | Models, regras e operações do carrinho | T01 e contrato de `Produto` de T02 |
| **T05** | **Davi** | Interface visual das telas de catálogo, produto, carrinho e login | T01; alinhar URLs/dados com T03/T04 |

**Ordem recomendada:** Breno prepara uma base funcional; Rafael define os models e seus nomes; Yuri e Pedro podem desenvolver em paralelo após conhecerem esse contrato; Davi pode preparar o layout-base desde cedo e conectar os templates quando views/URLs estiverem definidas. **A ordem não é uma divisão permanente do projeto**, apenas desta entrega.

### Contratos de integração (alinhar antes de editar)

- Apps propostas: `catalog` (produtos/categorias) e `cart` (carrinho). Projeto Django: `config`. Usar os nomes efetivamente criados por Breno.
- Model de referência: `catalog.Produto`; informações especializadas podem ficar em `Livro` e `Eletronico`, conforme a modelagem que Rafael definir.
- O carrinho deve referenciar o **usuário autenticado do Django**, sem criar um segundo sistema de login nesta etapa.
- Convenção sugerida de rotas e nomes, a confirmar no código: `/` (`catalog:index`), `/produto/<id>/` (`catalog:product_detail`), `/carrinho/` (`cart:detail`) e rotas **POST** para adicionar, atualizar e remover itens.
- **Propriedade dos arquivos:** Rafael edita prioritariamente `catalog/models.py`, `catalog/admin.py` e migrações; Yuri, `catalog/views.py`/`catalog/urls.py`; Pedro, arquivos do app `cart`; Davi, `templates/` e `static/`; Breno, `config/`, `manage.py`, `requirements.txt`, `.gitignore` e `README.md`. Mudanças fora dessa responsabilidade devem ser coordenadas para evitar sobrescrever trabalho alheio.
- Não usar funções ou nomes de rotas inexistentes silenciosamente: primeiro conferir os arquivos implementados e alinhar os contratos.

---

## T01 — Breno · Inicializar o projeto Django

**Prioridade:** bloqueante · **Estado:** [x] Concluído

**Objetivo:** partindo de um repositório vazio, deixar o Django **instalável, iniciável e acessível no navegador**, sem adiantar a lógica de catálogo/carrinho.

**Checklist**

- [x] Criar e testar ambiente virtual local `.venv` e arquivo `requirements.txt` com dependências realmente usadas.
- [x] Inicializar o projeto Django (`manage.py`, `config/settings.py`, `config/urls.py` etc.).
- [x] Criar a estrutura mínima dos apps `catalog` e `cart`, registrá-los em `INSTALLED_APPS` e deixar URLs iniciais válidas, mesmo que ainda sejam placeholders.
- [x] Disponibilizar a rota `/` com uma página provisória simples (ex.: “Projeto Amazon em desenvolvimento”), sem tentar implementar o catálogo.
- [x] Manter `templates/` e `static/` configurados para o Davi trabalhar depois; evitar criar o layout definitivo.
- [x] Habilitar o Django Admin e o mecanismo de autenticação padrão; deixar rota de login disponível para a interface posterior.
- [x] Configurar `.gitignore` para `.venv/`, `__pycache__/`, `.env`, banco local de desenvolvimento e outros arquivos gerados; nunca incluir segredos.
- [x] Atualizar `README.md` com requisitos, criação/ativação de `.venv` no Windows e Linux/macOS, instalação, `migrate`, criação de usuário administrador e `runserver`.
- [x] Executar `python manage.py check`, `python manage.py migrate` e iniciar `python manage.py runserver` para confirmar que a página inicial responde.
- [x] Registrar no README qual banco está efetivamente configurado e quais escolhas continuam provisórias.

**Critério de conclusão:** outro integrante consegue seguir o README, executar a aplicação localmente e abrir `/` e `/admin/` **antes** de haver produtos ou carrinho implementados.

**Não fazer:** models completos de produtos, views de catálogo, carrinho funcional, telas definitivas ou módulos futuros.

---

## T02 — Rafael · Modelos e cadastro de produtos

**Prioridade:** alta · **Estado:** [x] Concluído · **Dependência:** T01

**Referência:** UC01, SRS `RF-CAT-01` a `RF-CAT-09` e regras `RN-01` a `RN-05`.

**Checklist**

- [x] Implementar models mínimos para **Categoria**, **Produto** e especializações **Livro** e **Eletronico**, com relacionamentos coerentes com o modelo de domínio/relacional.
- [x] Contemplar os atributos exigidos: produto (nome, descrição, preço, estoque, categoria e tipo); livro (ISBN, páginas, idioma, autor, editora); eletrônico (modelo, garantia, fabricante).
- [x] Criar somente entidades de apoio necessárias ao cadastro (ex.: Autor, Editora, Fabricante e representação simples de Idioma), documentando decisões de modelagem relevantes.
- [x] Permitir categoria pai/subcategoria sem introduzir estrutura complexa desnecessária.
- [x] Registrar os models no **Django Admin** para cadastrar categorias e produtos de demonstração; usar o Admin como interface administrativa inicial, sem criar tela extra.
- [x] Validar obrigatoriedade de campos, estoque não negativo e preço **maior que R$ 0,00 e menor que R$ 10.000,00**, conforme o SRS v1.1. Registrar a divergência do fluxo A5 do UC01, sem liberar preços fora desse limite.
- [x] Gerar e testar migrações; confirmar que é possível cadastrar pelo menos **um Livro e um Eletrônico** vinculados a categorias.
- [x] Criar testes básicos de validação dos produtos e das relações essenciais.
- [x] Informar a Yuri e Pedro o contrato real dos models, os campos de preço/estoque e o caminho para consultar os produtos.

**Critério de conclusão:** produtos de ambos os tipos podem ser cadastrados/consultados pelo Django Admin, são persistidos corretamente e respeitam as regras básicas. Há dados suficientes para demonstrar a interface.

**Não fazer:** inventário de vendedores, avaliações completas, telas públicas, checkout nem duplicação de models que outro integrante já criou.

---

## T03 — Yuri · Catálogo público, navegação e filtros

**Prioridade:** alta · **Estado:** [x] Concluído com ajuste de teste posterior à auditoria · **Dependências:** T01, T02

**Referências:** UC02, UC03; SRS `RF-FLT-01` a `RF-FLT-08`, `RN-20`; busca e detalhe previstos no levantamento.

**Checklist**

- [x] Implementar a view/URL da **Home (`/`)** para exibir os produtos cadastrados por Rafael (substituindo o placeholder de Breno).
- [x] Implementar **navegação por categorias e subcategorias**; permitir clicar na categoria e visualizar seus produtos.
- [x] Implementar página de **detalhes do produto**, com nome, descrição, preço, disponibilidade, tipo e dados específicos do Livro/Eletrônico.
- [x] Implementar **busca simples por palavra-chave**, ao menos pelo nome do produto, para a barra de pesquisa da Home funcionar.
- [x] Implementar filtro por **faixa de preço** e, para eletrônicos, por **fabricante**; permitir limpar filtros e combinar os critérios suportados.
- [x] Validar preços dos filtros, tratar resultados vazios e paginar a listagem quando ultrapassar **50 produtos por página**.
- [x] Expor às templates dados claros e consistentes, sem montar HTML dentro das views. Combinar com Davi os nomes de templates, parâmetros e URLs.
- [x] Testar listagem, detalhe, categoria vazia, filtros válidos/inválidos e paginação.
- [x] Registrar como **pendente de decisão** filtros do SRS que exigiriam informações não modeladas nesta etapa (ex.: avaliação média ou prazo estimado de entrega). Não inventar notas ou prazos falsos para fazer o filtro parecer funcional.

**Verificação em 08/11/2026:** o teste `catalog.tests.test_views.CatalogoPublicoTests.test_categoria_e_detalhe_do_produto_respondem` falha porque espera “Informações do livro”, enquanto o template integrado exibe “Sobre o livro”. A funcionalidade de detalhe respondeu, mas o teste precisa ser alinhado ao texto atual ou o texto precisa ser revisto com Davi/Yuri. Os filtros de avaliação média e prazo seguem sem decisão documentada na T03.

**Atualização técnica em 09/11/2026:** a expectativa do teste de detalhe foi alinhada ao título atual do template. A paginação já existia; os testes foram ampliados para verificar 50 produtos na primeira página, o restante na segunda, preservação de categoria/busca/faixa de preço, páginas inválidas ou acima do limite, categoria vazia e combinação de fabricante com preço. Filtros por avaliação média e prazo estimado de entrega permanecem **pendentes de decisão do grupo**, pois não há dados modelados para aplicá-los. Este ajuste posterior à auditoria de Yuri ainda não recebeu nova avaliação humana.

**Critério de conclusão:** a Home exibe produtos reais do banco; usuário navega até o detalhe, busca e filtra produtos e recebe mensagens adequadas se não houver resultado.

**Não fazer:** editar models de Rafael sem alinhamento, implementar avaliações, inventar cálculo de entrega ou montar layout visual elaborado.

---

## T04 — Pedro · Funcionalidade do carrinho

**Prioridade:** alta · **Estado:** [x] Concluído com pendência documentada · **Dependências:** T01 e modelo `Produto` de T02

**Referências:** UC04 (consultar), UC05 (remover), UC11 (adicionar); SRS `RF-CAR-01` a `RF-CAR-09` e `RN-06` a `RN-08`.

**Checklist**

- [x] Criar models **Carrinho** e **ItemCarrinho**, associados ao usuário autenticado e ao `Produto`, com migrações.
- [x] Implementar a consulta do carrinho do usuário, incluindo **carrinho vazio**.
- [x] Implementar **adicionar produto**, exigindo quantidade inteira positiva e disponível em estoque.
- [x] Se o produto já estiver no carrinho, **somar quantidades**, verificando o estoque considerando a quantidade total.
- [x] Implementar **alteração de quantidade** e **remoção completa do item**, com confirmação na interface antes de remover (coordenar com Davi).
- [x] Calcular `subtotal = preço unitário × quantidade` e `total = soma dos subtotais`; ao esvaziar, total deve ser zero.
- [x] Exigir autenticação nas operações de carrinho e garantir que ninguém consulte/edite itens de outro usuário.
- [x] Utilizar operações POST e proteção CSRF para alterações; retornar mensagens claras de sucesso/erro.
- [x] Criar testes para inclusão repetida, estoque insuficiente, quantidade inválida, remoção, total, carrinho vazio e isolamento entre usuários.
- [ ] Combinar com Davi campos, ações e nomes de URLs usados pelo formulário e pela tela do carrinho.

**Verificação em 08/11/2026:** os 25 testes de `cart` passaram e os templates usam as rotas reais. A auditoria de Pedro ainda pede avisar Davi sobre as edições feitas nos templates; não há evidência de que essa comunicação ocorreu.

**Critério de conclusão:** com usuário autenticado, é possível adicionar um produto a partir do catálogo, visualizar o carrinho, alterar/remover itens e ver todos os valores atualizados corretamente.

**Não fazer:** finalizar compra, registrar Pedido/ItemPedido, processar pagamentos ou cadastrar endereços.

---

## T05 — Davi · Interface visual da Home, produto e carrinho

**Prioridade:** alta · **Estado:** [~] Em andamento · **Dependências:** T01; integração com T03 e T04

**Referências:** mockups da seção 3.1 do SRS, especialmente **Home**, **Página de Produto** e **Meu Carrinho**.

**Checklist**

- [x] Criar `base.html` reutilizável com **cabeçalho**, navegação, acesso ao catálogo, pesquisa, link para carrinho e área para mensagens do Django.
- [x] Montar a **Home** em formato de vitrine inspirado em lojas como Amazon, usando Bootstrap e CSS simples, sem copiar integralmente a identidade visual da empresa.
- [x] Montar **cards de produtos** com nome, preço, tipo, imagem ilustrativa/placeholder e link para detalhes.
- [x] Montar a **página de produto** com descrição, preço, informações relevantes, disponibilidade, quantidade e botão funcional de adicionar ao carrinho.
- [x] Montar **Meu Carrinho** com itens, quantidade editável, preço, subtotal, total, remoção com confirmação e estado vazio.
- [x] Criar **login simples** usando a autenticação nativa do Django, apenas para permitir o uso do carrinho. Não criar cadastro completo de clientes.
- [x] Integrar os formulários às URLs/views reais de Yuri e Pedro, respeitando CSRF, erros de validação e mensagens.
- [x] Verificar visualização em desktop e telas menores, mantendo layout organizado e navegação clara.
- [x] Validar que botões e links expostos realmente funcionam. **Não apresentar “Finalizar compra” como funcional nesta semana**; omitir ou sinalizar que ainda não está disponível.

**Verificação em 08/11/2026:** a estrutura da Home está nos templates e CSS; a auditoria anterior da T05 foi parcial e antecede a integração funcional posterior do carrinho. Falta revalidar visualmente e concluir a auditoria da integração com Davi. Os itens marcados como feitos representam código presente, não nova aprovação humana da T05.

**Critério de conclusão:** as três telas pedidas (Home/Catálogo, Produto, Carrinho) são navegáveis e visualmente coerentes; o usuário consegue executar os fluxos ligados ao backend, sem interfaces extras fora do escopo.

**Não fazer:** login personalizado avançado, páginas de pedido/pagamento/endereço, animações elaboradas, refatoração das regras de negócio dos demais.

---

## 3. Verificação integrada da entrega (após T01–T05)

- [x] Em ambiente limpo, seguir o **README** para instalar, migrar e executar localmente.
- [x] Acessar Home sem erro e visualizar pelo menos um livro e um eletrônico cadastrados pelo Django Admin.
- [x] Navegar por categoria, abrir detalhe de um produto, buscar e aplicar filtros básicos.
- [x] Fazer login como cliente de demonstração e adicionar produto ao carrinho.
- [x] Verificar subtotal e total; adicionar o mesmo produto novamente; alterar quantidade; remover.
- [x] Verificar estados de carrinho vazio, quantidade inválida e falta de estoque.
- [x] Conferir que usuário A não acessa o carrinho de usuário B e que apenas administrador cadastra produtos.
- [x] Executar `python manage.py check` e `python manage.py test`; registrar eventuais falhas ainda existentes.
- [ ] Confirmar que não existem links funcionais enganosos para checkout ou outras funcionalidades ainda não implementadas.
- [x] Atualizar README caso a forma real de execução tenha mudado.

**Verificação técnica em 08/11/2026:** `manage.py check` passou; `makemigrations --check --dry-run` não detectou mudanças; `migrate` aplicou `catalog.0001_initial` e `cart.0001_initial` ao SQLite local; 31 testes de models/Admin do catálogo e 25 testes do carrinho passaram. A suíte completa executou 66 testes com 1 falha de expectativa textual no detalhe do livro (“Informações do livro” no teste × “Sobre o livro” no template). O banco local contém 0 produtos; a fixture de demonstração foi validada por testes, mas não carregada nele para evitar sobrescrever dados por PK. Portanto, os fluxos integrados com produtos reais no banco local e a conferência visual final permanecem pendentes.

**Atualização técnica em 09/11/2026:** `python manage.py check` passou sem avisos e `python manage.py test` aprovou os 70 testes. As migrações de `catalog` e `cart` estão aplicadas. Antes da carga, todas as tabelas do catálogo local estavam vazias; `python manage.py loaddata catalogo_demo` carregou 27 objetos, incluindo 3 livros e 3 eletrônicos. Requisições ao `runserver` local para Home, categoria, detalhe e busca retornaram HTTP 200; `/admin/` redirecionou ao login e a página de login respondeu HTTP 200. Os itens que exigem observação no navegador, cadastro manual pelo Admin e avaliação humana seguem pendentes.

**Avaliação manual relatada por Breno em 09/11/2026:** realizou os passos 1 a 9 do roteiro de verificação integrada (ambiente limpo, cadastro e consulta de produtos, catálogo e filtros, login, operações e estados do carrinho, isolamento entre usuários e permissão administrativa) e informou que todos funcionaram. Essa informação é relato do integrante; a revisão visual e dos links do passo 10 permanece atribuída a Davi e ainda não foi confirmada nesta avaliação.

**Observação:** esta é uma conferência do **resultado integrado**, não uma sexta tarefa atribuída permanentemente a um integrante. Cada responsável deve testar sua entrega; a integração deve ser combinada pelo grupo.

## 4. Fluxo obrigatório dos agentes e auditoria

1. **Identificar o integrante** pelo contexto ou perguntar diretamente: **Breno, Davi, Rafael, Yuri ou Pedro**.
2. Ler `AGENTS.md`, o arquivo de contexto e este `TODO.md`; selecionar **somente a tarefa semanal atribuída** ao integrante. Não presumir que ele é responsável para sempre por esse módulo.
3. Inspecionar o repositório, implementar a tarefa, executar scripts/migrações/testes pertinentes e relatar alterações, resultados e limitações. **Agentes não podem realizar `git commit`, `git push`, rebase, reset ou reescrita de histórico.** O versionamento é decisão dos integrantes.
4. Após a implementação, conduzir a **auditoria da tarefa desse integrante** com **até 5 perguntas sequenciais no total**, preferencialmente uma por vez, identificadas como `Pergunta 1/5`, `Pergunta 2/5` etc. Ajustar as perguntas às etapas efetivamente implementadas; não repetir perguntas já respondidas. Interfaces de resposta compactas podem ser utilizadas se disponíveis; caso contrário, perguntar em texto.
5. Perguntar sobre **avaliação da implementação**, **problemas encontrados**, **sugestões de melhoria** e **resultado percebido**. Fazer as perguntas com foco nas partes da tarefa, e não no projeto inteiro. Não inventar resposta, opinião, execução de teste ou aprovação.
6. Elaborar o relatório de autoria em **primeira pessoa**, fundamentado apenas nas respostas reais e nas verificações observáveis, com: identificação do integrante no cabeçalho, introdução/contexto, tarefa e etapas, achados, recomendações (se houver) e **conclusão em perspectiva humana** sem precisar repetir o nome no texto. **Não incluir campo Instituição**.
7. Salvar o relatório inicialmente em Markdown, por exemplo `auditorias/semana-atual/breno/T01-auditoria.md`, e exportar para DOCX se solicitado/viável no ambiente. Uma tarefa por auditoria; não misturar avaliações de integrantes diferentes.

### Status e acompanhamento

- `[ ]` **Não iniciado:** nenhum código entregue para a tarefa.
- `[~]` **Em andamento:** há implementação parcial e/ou auditoria pendente.
- `[x]` **Concluído:** critérios de conclusão verificados, com pendências documentadas quando houver.

**Importante:** a etapa final não pressupõe que esta semana inclua o restante do sistema. A próxima distribuição do professor deverá **atualizar este `TODO.md`**, preservando relatórios de auditoria já produzidos.
