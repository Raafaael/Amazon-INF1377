# Contexto do projeto — E-commerce Amazon (acadêmico)

> **Documento de contexto para agentes de IA (`context.md`)**  
> **Última revisão contra os materiais entregues:** 07/11/2026  
> **Idioma do projeto:** português (Brasil)  
> **Estado:** modelagem e documentação elaboradas; implementação planejada. Referência documental mais completa disponibilizada: **SRS versão 1.1 (03/11/2026)**, com seções 1–6 e apêndices. Este documento **não** afirma que funcionalidades já estão implementadas.

## 0. Instruções essenciais para agentes

Este arquivo explica **o produto, o domínio e as decisões atuais**. Não é uma ordem para implementar tudo imediatamente.

1. **Leia o código existente antes de sugerir ou editar arquivos.** Use nomes, padrões e convenções já presentes no repositório. As estruturas abaixo são sugestões, não um retrato de arquivos existentes.
2. **Preserve o caráter acadêmico:** escolha implementações simples, locais e compreensíveis. Não introduza React, API REST completa, Docker, Kubernetes, microsserviços, filas, Redis, cloud, CI/CD complexo ou gateways de pagamento sem solicitação explícita.
3. **Python e a ausência de Docker são decisões explícitas do grupo.** **Django + Templates + Bootstrap + MySQL + Django ORM** é a **proposta simplificada mais recente**, ainda sujeita a confirmação do grupo. Não retorne automaticamente à proposta anterior em Node.js/React.
4. **Pagamentos e acompanhamento de entregas são simulações internas.** Não existe cobrança, PIX bancário, transportadora ou autorização financeira real. O SRS v1.1 e o diagrama de casos de uso **desenham serviços de pagamento/PIX/transporte como atores ou caixas externas conceituais**, mas registram que sua execução será simulada. Não confundir representação de análise com obrigação de integrar provedores reais.
5. **A integração externa prevista é a consulta de CEP**, por exemplo ViaCEP; seu provedor exato pode ser ajustado. Trate falhas e dados incompletos.
6. **Não invente requisitos, campos ou regras.** Consulte primeiramente o **SRS v1.1** e os **11 casos de uso detalhados** para comportamento, e os diagramas para estrutura; se houver divergência entre os próprios artefatos, aponte-a. Não substitua regras expressas no SRS por sugestões técnicas sem autorização.
7. **Proteja o isolamento entre usuários:** carrinho, endereços, listas, cartões simulados e pedidos pertencem ao cliente autenticado. Somente administradores podem realizar ações administrativas.
8. **Não confunda modelagem concluída com implementação concluída.** A coluna “Finalizado” de uma planilha antiga refere-se ao trabalho de levantamento/documentação, não comprova código pronto.
9. **Prefira incrementos pequenos e testáveis**, usando recursos nativos do Django **se a stack for ratificada**. Evite duplicar recursos já oferecidos pelo framework, como autenticação, ORM, migrations, formulários e administração.
10. **Antes de executar migrações destrutivas, apagar dados ou alterar contratos entre módulos**, avalie o impacto e exponha o risco.

---

## 1. Visão geral

O projeto é uma **aplicação web de comércio eletrônico inspirada na Amazon**, desenvolvida por um **grupo de cinco integrantes como trabalho de faculdade**. Não pertence à Amazon, não reproduz sua infraestrutura e não precisa ser implantado para uso comercial ou tráfego real.

O sistema permite navegar por um catálogo de **livros** e **produtos eletrônicos**, pesquisar e filtrar produtos, manter um carrinho, criar listas de desejos, cadastrar endereços, finalizar compras com **pagamento simulado**, consultar pedidos e acompanhar seus estados. Um **administrador** gerencia o catálogo e, conforme o escopo, atualiza estados de pedidos.

### Objetivos do trabalho

- Demonstrar os casos de uso e regras de negócio identificados na fase de Engenharia de Requisitos.
- Transformar diagramas UML e um modelo relacional em uma aplicação navegável, com persistência.
- Facilitar colaboração e divisão de tarefas entre cinco pessoas.
- Manter código legível, funcional e interessante para portfólio, **sem complexidade desnecessária**.

### Fora de escopo

- Marketplace com vendedores externos, logística física verdadeira e integrações comerciais da Amazon.
- Processamento real de cartão, cobrança PIX, reembolso bancário e armazenamento de dados financeiros sensíveis.
- Integração real com transportadoras ou emissão de etiquetas de frete.
- Arquitetura distribuída/microsserviços e infraestrutura de produção.
- Qualquer funcionalidade não levantada explicitamente, salvo aprovação do grupo.

---

## 2. Tecnologias: decisões e propostas atuais

**Confirmado pelo grupo:** preferência por **Python**, aplicação simples e **sem Docker**. **Proposta recente do assistente, ainda não ratificada expressamente:** Django, Django Templates, Bootstrap, MySQL e Django ORM. Este documento adota a proposta como **base de trabalho provisória**, não como obrigação imutável.

| Responsabilidade | Base sugerida | Observações |
|---|---|---|
| Backend / aplicação web | **Python + Django** | Aplicação monolítica e modular. |
| Interface web | **Django Templates + HTML/CSS/JavaScript** | Não há necessidade de SPA nem de API REST para todas as telas. |
| CSS | **Bootstrap** | Complementar com CSS simples quando necessário. |
| Banco de dados | **MySQL** | Relacional, conforme diagrama de tabelas. |
| Persistência | **Django ORM** | Usar migrations do Django; evitar escrever toda a camada de acesso em SQL manual. |
| Usuários / sessões | **Autenticação nativa do Django** | Adaptar ao perfil Cliente/Administrador sem duplicar credenciais desnecessariamente. |
| Consulta de CEP | **Serviço HTTP de CEP, como ViaCEP** | Única integração externa do produto atualmente prevista. |
| Testes | **Django TestCase** | Priorizar regras de negócio, permissões e fluxos críticos. |
| Execução | **Local, `venv` e `pip`** | Sem Docker. |
| Controle de versão | **Git + GitHub** | Trabalho colaborativo. |

Não há decisão atual de usar Celery, DRF, React, Node.js, Tailwind ou hospedagem em nuvem. Docker foi explicitamente dispensado. Não adicionar essas dependências por iniciativa própria.

### Diretriz arquitetural

**Monólito Django organizado por responsabilidade de domínio**, com um único projeto, banco relacional e páginas renderizadas no servidor.

Exemplo **ilustrativo**, não uma estrutura já existente nem uma exigência rígida:

```text
projeto-amazon/
├── manage.py
├── requirements.txt
├── config/               # settings, URLs gerais
├── accounts/             # autenticação, perfis, endereços
├── catalog/              # produtos, livros, eletrônicos, categorias
├── cart/                 # carrinho e itens
├── wishlist/             # listas de desejos
├── orders/               # pedidos, itens, status, histórico
├── payments/             # simulação de cartão e PIX
├── templates/            # templates HTML
├── static/               # CSS, JS, imagens locais
└── README.md
```

Essa separação é **uma opção de organização**. Antes de gerar apps, conferir o que já existe no repositório. Não é obrigatório criar um app por entidade/classe UML.

### Fluxo típico

```text
Navegador (HTML/Bootstrap)
          ↕ formulários e requisições HTTP
Django (views, forms, regras de negócio, autenticação)
          ↕ Django ORM
        MySQL

Django ── HTTP/JSON ──> API externa de CEP

Pagamentos e estados de entrega: lógica SIMULADA dentro do Django
```

---

## 3. Perfis e permissões

### Cliente

Usuário que pode consultar produtos e suas categorias, manter seu carrinho e listas de desejos, cadastrar endereços, realizar pedidos simulados e consultar suas próprias compras.

- É necessário estar autenticado para executar operações pessoais que assim exigem os casos de uso.
- Um cliente não pode consultar nem modificar carrinho, endereços, listas, cartões ou pedidos de outro cliente.
- A navegação pública do catálogo é uma escolha prática; verificar a necessidade de autenticação nas operações com base nos casos de uso.

### Administrador

Usuário com permissão para cadastrar/gerenciar produtos e categorias e atualizar o status dos pedidos conforme as regras de negócio.

- Permissões devem ser verificadas no backend, não apenas escondendo botões.
- Pode ser representado inicialmente pelo sistema de permissões/grupos (`is_staff`, grupos) do Django, em vez de criar um segundo mecanismo de login.
- O painel Django Admin pode auxiliar a manutenção, mas não substitui necessariamente as telas que o trabalho exigir demonstrar.

**Observação de modelagem:** alguns diagramas usam uma superclasse `Usuario` especializada em `Cliente` e `Administrador`. No Django, essa herança deve ser **adaptada**, não copiada literalmente se isso duplicar o usuário de autenticação do framework.

---

## 4. Áreas funcionais

| Área | Responsabilidades |
|---|---|
| Catálogo | Produtos, livros, eletrônicos, categorias/subcategorias, busca, filtros, detalhes, estoque, avaliações. |
| Conta e endereços | Perfil do cliente, endereços, endereço padrão, consulta por CEP. |
| Carrinho | Adição, alteração de quantidade, remoção, subtotal, total, validação de disponibilidade. |
| Listas de desejos | Criar, consultar, editar, excluir e associar produtos; nome e privacidade. |
| Pedidos | Finalizar compra, itens e valores, consultar pedidos e detalhes, estados, histórico, tipo de entrega. |
| Pagamentos | Escolher forma de pagamento, cartão e PIX **simulados**, atualizar status. |
| Administração | Cadastrar e gerenciar produtos/categorias, atualizar estados de pedidos. |

Os **11 casos de uso detalhados** estão listados na próxima seção. A planilha de funcionalidades contém outros casos levantados, nem todos completamente especificados ou necessariamente obrigatórios na primeira entrega.

---

## 5. Casos de uso detalhados (UC01–UC11)

Fonte da conferência mais recente: arquivo `Descrição de casos de uso - IHC(1).pdf`. Os identificadores abaixo respeitam o documento e **não devem ser renumerados** apenas porque a implementação foi reorganizada.

| UC | Nome | Ator | Comportamento essencial |
|---|---|---|---|
| **UC01** | Cadastrar Produto | Administrador | Cadastrar produto do tipo Livro ou Eletrônico, com categoria e atributos específicos; validar campos e preço. |
| **UC02** | Filtrar Produtos (Eletrônicos) | Cliente | Filtrar por faixa de preço e fabricante; o SRS v1.1 também prevê avaliação média e prazo estimado de entrega. Filtros de livros por idioma/autor aparecem em outros artefatos, não como escopo detalhado do UC02. |
| **UC03** | Navegar por Categorias e Subcategorias | Cliente | Percorrer hierarquia de categorias e listar produtos; apresentar mensagem para categoria sem produtos. |
| **UC04** | Consultar Carrinho de Compras | Cliente | Exibir itens, quantidades, valores unitários, subtotais e total; contemplar estado vazio. |
| **UC05** | Remover Produto do Carrinho | Cliente | Confirmar remoção de um item e recalcular total; cancelar remoção não modifica o carrinho. |
| **UC06** | Cadastrar Endereço | Cliente | Consultar CEP, preencher campos de localização, informar número/complemento/tipo e opção de endereço padrão. |
| **UC07** | Consultar Detalhes do Pedido | Cliente | Exibir itens, valores, status, datas, endereço/entrega quando aplicável e ações permitidas pelo estado. |
| **UC08** | Criar Lista de Desejos | Cliente | Criar lista nomeada com configuração de privacidade, vinculada ao usuário. |
| **UC09** | Realizar Pagamento por Cartão | Cliente | Selecionar cartão cadastrado ou informar dados fictícios, validar e simular autorização/recusa. |
| **UC10** | Consultar Pedidos | Cliente | Listar seus pedidos, incluindo status e valores, do mais recente para o mais antigo. |
| **UC11** | Adicionar Produto ao Carrinho | Cliente | Informar quantidade, verificar estoque e adicionar ou incrementar quantidade do produto existente. |

### Funcionalidades adicionais já levantadas

O levantamento atualizado `Funcionalidades - Amazon - Página1(3).pdf` também menciona, entre outras:

- Consultar/alterar dados do cliente; consultar/alterar/remover endereços.
- Buscar produtos por palavras-chave e visualizar seus detalhes.
- Consultar/alterar/excluir listas de desejos; adicionar/remover produtos dessas listas.
- Alterar a quantidade de produtos no carrinho e **finalizar compra**.
- Selecionar endereço e tipo de entrega (`PADRAO`, `EXPRESSA`, `AGENDADA`).
- Selecionar forma de pagamento, simular PIX, escolher cartão e parcelas.
- Acompanhar/cancelar pedidos, consultar histórico e alterar status (administrador/sistema).
- Cadastrar categorias e definir relações entre categoria e subcategoria.

**Atenção:** a existência dessas funcionalidades na planilha **não significa** que todas possuem descrição de fluxo completa ou que devam ser implementadas simultaneamente. Validar prioridades com o grupo/professor.

---

## 6. Modelo de domínio e entidades

A nomenclatura deriva dos diagramas UML de classes e do projeto relacional. **O diagrama de domínio não é uma especificação literal de models Django**; relações e nomes das tabelas podem ser implementados de forma idiomática, preservando o comportamento.

### 6.1. Catálogo

- **`Produto`**: entidade geral do catálogo; nome, descrição, preço unitário, quantidade em estoque, categoria. Pode participar de carrinhos, pedidos, avaliações e listas de desejos.
- **`Livro`**: especialização de Produto; ISBN, número de páginas, idioma, autor(es) e editora.
- **`Eletronico` / `Eletrônico`**: especialização de Produto; modelo, garantia (meses) e fabricante.
- **`Categoria`**: classificação de produtos; pode possuir categoria pai e subcategorias (hierarquia).
- **`Autor`**: nome e, no diagrama, biografia; associado a livros.
- **`Editora`**: editora associada a livros.
- **`Fabricante`**: fabricante associado a eletrônicos.
- **`Idioma`**: aparece como enum no domínio e como tabela no modelo relacional. Decidir como representá-lo no Django.
- **`Avaliacao`**: avaliação de produto por cliente; nota entre 1 e 5, título/comentário e datas de criação/atualização no diagrama.

### 6.2. Contas, endereços e desejos

- **`Usuario`**: conceito geral de autenticação no diagrama; adaptar ao `User` do Django.
- **`Cliente`**: perfil/ator de compras, associado a endereço(s), carrinho, listas de desejos, avaliações e pedidos.
- **`Administrador`**: perfil/ator de gestão.
- **`Endereco`**: CEP, logradouro, número, complemento, bairro, cidade, estado e cliente proprietário. **UC06 exige uma opção de endereço padrão**, mas o quadro `Endereco` no modelo relacional apresentado não explicita um campo `padrao`; é uma lacuna entre regra de negócio e diagrama de tabelas que precisa de solução aprovada.
- **`TipoEndereco`**: identificação do tipo de endereço; aparece no modelo relacional.
- **`ListaDeDesejos`**: nome, data de criação, opção de privacidade e cliente proprietário.
- **`ItemListaDeDesejos`**: tabela associativa explícita no modelo relacional entre lista e produto; no domínio a associação pode ser representada de outra maneira.

### 6.3. Carrinho e pedidos

- **`CarrinhoCompras`** (ou `Carrinho`, nome simplificado no modelo relacional): carrinho associado a um cliente.
- **`ItemCarrinho`**: associação carrinho–produto, com quantidade. Preço unitário aparece também no modelo relacional; confirmar se será armazenado ou calculado ao consultar.
- **`Pedido`**: cliente, data, status, valores dos produtos, frete e total, tipo de entrega e, quando aplicável, endereço e datas de envio/entrega.
- **`ItemPedido`**: produto comprado, quantidade, preço unitário **registrado no momento da compra** e subtotal.
- **`StatusPedido`**: conjunto de estados do pedido.
- **`TipoEntrega`**: `PADRAO`, `EXPRESSA` e `AGENDADA` exemplificados no levantamento/diagrama; evitar presumir cálculo real de frete ou agendamento de transportadora.
- **`Timestamp`**: classe/conceito auxiliar associada ao registro de mudanças de status no **diagrama de domínio** do Apêndice B do SRS; não é o nome da tabela relacional.
- **`HistoricoStatusPedido`**: **tabela efetiva no diagrama relacional apresentado**; possui `oid`, FK para `Pedido`, FK para `StatusPedido`, `dataAlteracao` e `observacao`. O requisito de histórico existe, mas deve-se alinhar a implementação à tabela de histórico de status em vez de criar automaticamente modelos `Timestamp` e `HistoricoPedido` distintos.
- **`Entrega`**: **ainda aparece como classe no diagrama de domínio anexado ao SRS v1.1**, apesar de a modelagem relacional não incluir uma tabela `Entrega` e de haver orientação posterior de simplificação/remover a classe. **Divergência documental a resolver**; não criar uma entidade nova apenas porque ela aparece no apêndice.

### 6.4. Pagamentos

- **`Pagamento`**: pagamento ligado a pedido, valor, data/status.
- **`PagamentoCartao`**: especialização, com número de parcelas e referência a cartão fictício.
- **`PagamentoPix`**: especialização, com código/identificador fictício e possível expiração.
- **`CartaoCredito`**: forma de pagamento simulada associada ao cliente. O **modelo relacional apresentado** contém atributo `numero` e `dataValidade`, mas a SRS 3.1 deixa claro o uso de **dados fictícios**. **Não persistir CVV ou números completos de cartões reais**, mesmo que a estrutura documental apresente um campo genérico de número.
- **`StatusPagamento`**: estados de processamento da simulação.

### 6.5. Relacionamentos conceituais importantes

- Um cliente pode possuir diversos endereços, pedidos, listas de desejos e avaliações.
- Um cliente possui um carrinho ativo para sua sessão/conta de compras (modelo exato a confirmar).
- Um carrinho contém `ItemCarrinho`, e cada item referencia um `Produto`.
- Um pedido contém `ItemPedido`, e cada item referencia um `Produto`.
- Um produto pertence a uma categoria e pode ser Livro ou Eletrônico.
- Categoria pode apontar para outra categoria pai, permitindo subcategorias.
- Livros são associados a autor(es), editora e idioma; eletrônicos a fabricante.
- Lista de desejos contém produtos por associação, podendo usar tabela intermediária.
- Pagamentos se associam a pedidos; a tabela `HistoricoStatusPedido` registra mudanças de status do pedido.
- O relacional prevê `Autor_Livro` como tabela de associação de livros com autores (relação potencialmente muitos-para-muitos), e `ItemListaDeDesejos` como associação lista-produto.

**Não inferir cardinalidades exatas apenas deste resumo.** Em caso de necessidade, consultar o diagrama correspondente e os casos de uso; algumas versões do material passaram por correções de multiplicidade.

---

## 7. Estados e regras de negócio

### 7.1. Estados documentados

**`StatusPedido`** no diagrama de classes:

```text
CRIADO
AGUARDANDO_PAGAMENTO
PAGAMENTO_APROVADO
EM_PREPARACAO
ENVIADO
ENTREGUE
CANCELADO
PAGAMENTO_RECUSADO
DEVOLVIDO
REEMBOLSADO
```

**`StatusPagamento`** no diagrama:

```text
PENDENTE
PROCESSANDO
APROVADO
RECUSADO
CANCELADO
REEMBOLSADO
```

**Observação:** estes são estados encontrados no modelo, **não uma máquina de estados plenamente especificada**. Não permitir transições arbitrárias. Regras de cancelamento, devolução, reembolso e transições válidas devem ser alinhadas antes de implementação completa.

### 7.2. Produto e catálogo

- Cada produto cadastrado é `Livro` ou `Eletronico`, e pertence a uma categoria existente.
- Livro possui ISBN, número de páginas, idioma, autor e editora; eletrônico possui modelo, garantia e fabricante.
- O preço deve ser **estritamente maior que R$ 0,00 e estritamente menor que R$ 10.000,00**, conforme **RN-02 do SRS v1.1** e RN2 do UC01. Há um fluxo alternativo (A5) do UC01 que sugere confirmar preços elevados; esta **contradição do UC01** deve ser sanada documentalmente, mas um agente não deve ignorar a restrição explícita do SRS.
- Não criar produto com campos obrigatórios inválidos.
- Na navegação por categoria, o UC03 prevê **até 50 produtos por página**, com paginação se houver mais.
- Filtros de preço exigem números válidos, mínimo não superior ao máximo. Fabricantes apresentados como filtro de eletrônicos devem corresponder aos produtos ativos/disponíveis, conforme UC02.

### 7.3. Carrinho

- Somente o dono pode consultar/alterar o carrinho.
- Quantidade de item adicionada deve ser **inteira positiva**, e não pode superar estoque disponível.
- Adicionar um produto que já está no carrinho deve incrementar a quantidade existente, com verificação do estoque total solicitado.
- `subtotal = preço_unitário × quantidade`; `total = soma(subtotais)`.
- Remover um produto retira **todas as unidades** desse produto do carrinho.
- Se o carrinho ficar vazio, total deve ser zero; a interface deve comunicar esse estado.
- Recalcular os totais após inclusão, remoção ou alteração de quantidade.

### 7.4. Endereços

- Consulta por CEP preenche logradouro, bairro, cidade e estado quando retornados pela API.
- Número é obrigatório; complemento é opcional; tipo de endereço deve ser informado.
- Cada cliente pode ter **no máximo um endereço padrão** por vez; definir outro substitui o anterior.
- É possível cadastrar endereço no perfil ou durante checkout de produtos físicos.
- **Pedido exclusivamente digital (ex.: e-book) não exige endereço nem entrega física.**

### 7.5. Pedidos

- Cliente visualiza apenas os próprios pedidos.
- Consulta exibe status, itens, quantidades, valores e datas pertinentes; listagem ordenada do mais recente ao mais antigo (UC10).
- Os detalhes e ações disponíveis dependem do status atual.
- Alterar endereço só pode ser permitido em pedido físico e em estágio compatível.
- Pedido exclusivamente digital não deve exibir endereço, tipo de entrega ou rastreamento físico.
- A opção **Avaliar Produto** é oferecida após conclusão da entrega, se ainda não avaliado (UC07); tratar o equivalente para digital como decisão pendente.
- **Comprar Novamente** cria nova intenção de compra, sem editar o pedido original.
- A opção de ver anúncio/recomprar depende da disponibilidade do produto no catálogo.
- Histórico de alterações de status deve preservar estados e datas quando essa funcionalidade for implementada.

### 7.6. Pagamentos simulados

- Pagamento cartão pode ser aprovado ou recusado ficticiamente.
- Somente um pagamento **aprovado** pode marcar a compra como paga.
- O valor registrado deve corresponder ao valor da compra confirmada.
- Pagamento recusado não deve ser mostrado como concluído.
- PIX é **fictício**: o SRS 3.3 prevê um **Gerador de PIX simulado** para código/QR Code e um **Banco/Provedor simulado** que confirme o pagamento. Essas são funções simuladas internamente, não serviços comerciais; códigos não podem disparar cobranças reais.
- **Não armazenar CVV, senhas bancárias ou dados reais completos de cartões.** Usar valores simulados e rótulos claros.

### 7.7. Listas de desejos

- Toda lista possui nome e configuração de privacidade.
- Toda lista pertence ao cliente autenticado.
- Privacidade deve ser respeitada nas consultas; como exposição/compartilhamento de listas públicas não está inteiramente especificado, não criar descoberta pública automaticamente.

### 7.8. Rastreabilidade com o SRS v1.1

O SRS contém **20 regras de negócio identificadas RN-01 a RN-20** (seção 5.5). Para qualquer alteração, verificar o texto exato do documento, sobretudo:

- **RN-01 a RN-05**: tipo, faixa de preço válida, categoria e dados obrigatórios de Livro/Eletrônico.
- **RN-06 a RN-08**: quantidade, estoque, subtotal e total do carrinho.
- **RN-09 a RN-11**: endereço padrão, número/complemento e compras exclusivamente digitais sem entrega física.
- **RN-12 a RN-13**: nome/privacidade da lista de desejos e autorização do pagamento antes de considerá-lo concluído.
- **RN-14 a RN-19**: pedidos próprios, ações conforme status, alteração de endereço, comprar novamente, avaliação após entrega e ordenação cronológica decrescente.
- **RN-20**: limite de **50 produtos por página** em subcategorias.

A seção **4 do SRS v1.1** detalha apenas **três conjuntos de RF** até a versão recebida: **RF-CAT-01 a RF-CAT-09** (gerenciamento do catálogo; prioridade **Alta**), **RF-FLT-01 a RF-FLT-08** (filtragem de eletrônicos; **Alta**) e **RF-CAR-01 a RF-CAR-09** (consulta ao carrinho; **Média**). **Não interpretar a ausência de outros RF detalhados na seção 4 como exclusão dos demais casos de uso ou funcionalidades.**

---

## 8. Fluxos de ponta a ponta relevantes

### 8.1. Consulta e adição ao carrinho

1. Cliente navega por categorias ou busca/filtra produtos.
2. Abre o detalhe do produto e informa quantidade.
3. O sistema verifica quantidade válida e estoque.
4. Adiciona ou incrementa `ItemCarrinho` do próprio cliente.
5. Atualiza e apresenta totais.

### 8.2. Finalização de compra (fluxo planejado)

1. Cliente autenticado acessa o carrinho.
2. Sistema verifica itens, quantidades, valores e disponibilidade.
3. Se houver produtos físicos, cliente escolhe endereço e tipo de entrega.
4. Cliente escolhe a forma de pagamento simulada (cartão ou PIX).
5. Sistema cria `Pedido` e respectivos `ItemPedido`, registra valores e executa simulação de pagamento.
6. Sistema exibe status atualizado; administração/simulação poderá evoluir o pedido por etapas.
7. Cliente consulta o pedido posteriormente em **Meus Pedidos**.

**Nota técnica (proposta, não regra documental fechada):** utilizar `transaction.atomic()` para manter consistentes criação de pedido, itens e ajustes de estoque; registrar preço e subtotal no `ItemPedido` para preservar histórico. Confirmar com o grupo em que momento estoque será reservado/baixado e se pedido não pago deve permanecer criado.

### 8.3. Cadastro de endereço

1. Cliente informa CEP.
2. Sistema consulta API externa e preenche campos retornados.
3. Cliente informa número, complemento opcional, tipo e preferência de padrão.
4. Sistema valida, vincula ao cliente e mantém apenas um padrão.
5. Em falha da API, apresentar erro compreensível sem registrar endereço incompleto indevidamente.

### 8.4. Consulta de pedido

1. Cliente acessa **Meus Pedidos** e vê somente seus pedidos.
2. Seleciona pedido e visualiza itens, quantidades, valor e status.
3. Para pedido físico, exibir endereço/entrega e acompanhamento quando aplicáveis.
4. Para pedido entregue, permitir ações pertinentes (ex.: avaliar ou comprar novamente).
5. Não apresentar ações incompatíveis com o status.

---

## 9. Interface e experiência do usuário

Há mockups iniciais, ainda sujeitos a ajustes. As principais telas levantadas são:

- **Home:** vitrine de produtos, pesquisa, acesso a categorias e carrinho.
- **Página de produto:** imagem, nome, preço, descrição, quantidade e adicionar ao carrinho.
- **Meu Carrinho:** itens, quantidades, totais e sequência da compra.
- **Meus Pedidos:** histórico/listagem e status.
- **Pop-up de Endereço:** seleção de endereços ou cadastro com CEP, número, complemento e tipo.
- **Pop-up de Pagamento:** escolha da forma e informações fictícias de cartão; considerar PIX.

Preferir templates reutilizáveis para cabeçalho, navegação, cartões de produto, formulários e mensagens. Manter a interface funcional e compreensível antes de investir em animações ou fidelidade estética elevada.

**Não pressupor telas de administração já desenhadas:** podem utilizar Django Admin ou uma interface simples conforme os requisitos de demonstração.

---

## 10. Recomendações para implementação e testes

Estas orientações são **propostas de engenharia** para cumprir os requisitos, não decisões adicionais já aprovadas pelo grupo.

### Convenções simples

- Preferir views, forms, templates, models, migrations e autenticação nativos do Django.
- Usar `DecimalField` para valores monetários, em vez de `float`/`double` literais dos diagramas.
- Declarar explicitamente chaves estrangeiras e restrições de integridade no ORM.
- Validar dados no servidor mesmo que haja validação JavaScript no navegador.
- Utilizar sessões e proteção CSRF do Django para formulários autenticados.
- Não guardar senha em texto puro; usar hashing do framework.
- Evitar hardcode de segredos e credenciais do MySQL; usar variáveis de ambiente quando adequado.
- Evitar criar APIs internas só para comunicar templates do Django com Django.

### Requisitos não funcionais documentados no SRS v1.1

Além das orientações técnicas acima, considerar como **requisitos do documento entregue**, e não apenas sugestões:

- **5.2 Safety / RNF-SAF-01 a RNF-SAF-07**: não confirmar compra incompleta; conferir itens/valores; informar falhas; evitar alterações incompatíveis com pedido; confirmar ações potencialmente prejudiciais; identificar pagamentos como simulações; preservar pedidos e pagamentos já registrados contra falhas/duplicações.
- **5.3 Security**: diferenciar Cliente e Administrador; aplicar autenticação/autorização efetivas; armazenar senhas com hash seguro; impedir acesso a recursos de outros clientes. O SRS também **exige criptografia em repouso para dados sensíveis (endereços, histórico de compras, perfil)**. O mecanismo concreto **não foi definido** e **não é fornecido automaticamente pelo Django ORM**: tratar como requisito com decisão técnica pendente, sem afirmar que já está atendido.
- **3.4 Communications**: o SRS exige **HTTPS quando houver transmissão de credenciais ou informações pessoais**. A configuração de ambiente local/de demonstração deve ser alinhada a essa exigência; não presumir que todo `runserver` local satisfaz HTTPS.
- **5.1 Performance**: **não há metas numéricas de desempenho definidas**, por falta de medições/infrastrutura. Não inventar SLA, latência obrigatória ou requisito de escala.
- **5.4 Qualidade**: usabilidade, confiabilidade, manutenibilidade, integridade, testabilidade e robustez.
- **6 Other Requirements**: compatibilidade com navegadores modernos, integridade de dados, proteção conforme LGPD quando aplicável, manutenção simples e permanência das simulações acadêmicas.

### Testes prioritários

1. Permissões: cliente A não consulta nem altera recursos do cliente B; cliente não cadastra produto.
2. Catálogo: campos obrigatórios e valores válidos; livro e eletrônico com seus dados específicos.
3. Carrinho: quantidade positiva, estoque insuficiente, adição repetida, remoção total, subtotal/total.
4. Endereço: CEP válido/inválido, falha externa, número obrigatório, exclusividade de endereço padrão.
5. Pedidos: criação de itens, totais, consulta apenas pelo dono, status e regras para produto digital.
6. Pagamento: aprovação/recusa simulada sem marcar pedido não pago como pago.
7. Listas de desejos: associação ao dono, nome e privacidade.

---

## 11. Divergências, pendências e decisões que um agente NÃO deve presumir

| Tema | Situação encontrada | Tratamento por agentes |
|---|---|---|
| **Preço máximo** | **SRS 1.1 RN-02 estabelece `0 < preço < 10.000`**. UC01 contém fluxo A5 de confirmação de preço alto, em conflito com RN2/RN3 e com SRS. | **Aplicar a regra explícita do SRS como base**. Registrar a inconsistência de A5 e solicitar alinhamento antes de aceitar exceção ao teto. |
| **`Entrega` como classe** | **O diagrama de domínio que está no Apêndice B do SRS 1.1 ainda mostra `Entrega`**, mas o diagrama relacional atual não apresenta tabela correspondente; houve também orientação de simplificação. | **Não fingir que o arquivo entregue já foi corrigido**; apontar a divergência. Preferir pedido/status/tipo de entrega apenas após alinhamento com o grupo/professor. |
| **Histórico do pedido** | O **domínio mostra `Timestamp`** como registro auxiliar; o **relacional mostra a tabela `HistoricoStatusPedido`** com FKs de pedido e status, data e observação. | Usar a nomenclatura relacional correta e não criar duplicatas; decidir como representar a informação no Django. |
| **Idioma** | Aparece como enum UML e tabela relacional. | Escolher representação na implementação apenas após alinhamento, ou registrar decisão explicitamente. |
| **Livros digitais** | Regras distinguem e-books (sem frete/endereço), mas modelo de Livro não explicita um indicador digital/físico. | Definir forma simples de representar natureza digital antes de implementar checkout. |
| **Pedidos mistos** | Regras cobrem pedidos exclusivamente digitais e físicos, mas não detalham mistura de ambos. | Não inventar política; definir com o grupo. |
| **Fluxo de estoque** | UC11 valida estoque no carrinho; momento da baixa/reserva na finalização não está integralmente definido. | Confirmar quando descontar estoque e como tratar pagamento recusado. |
| **Pagamento** | UC09 e o diagrama de casos de uso mostram Serviço de Autorização; o **SRS 1.1 o representa como serviço externo conceitual a ser simulado**, junto com gerador/confirmador PIX. | Implementar **simulação interna**, sem gateway comercial; preservar os nomes conceituais ao explicar os diagramas. |
| **Transporte** | Diagrama de casos de uso e Figura 1 do SRS 1.1 mostram transportadora como ator/caixa externa; o texto afirma que será **simulada**. | Não criar integração real com transportadora; registrar a diferença entre representação e implementação. |
| **Cadastro de cartão** | O modelo relacional inclui `CartaoCredito.numero` e `dataValidade`; o SRS exige dados fictícios para a simulação e proíbe incentivar o uso de cartão verdadeiro nas telas. | Não persistir CVV nem números reais completos; usar dados de teste/mascarados e sinalizar a simulação. |
| **UC04 carrinho vazio** | Pré-condição cita ao menos um produto, porém fluxo alternativo trata carrinho vazio. | Tratar carrinho vazio como estado legítimo da interface, registrando a inconsistência documental se necessário. |
| **Status e transições** | Enumeração foi levantada, mas não há máquina de estados fechada. | Não permitir saltos irrestritos; validar transições escolhidas com o grupo. |
| **Escopo da entrega inicial** | 11 UCs detalhados e dezenas de funcionalidades na planilha. | Priorizar fluxo principal demonstrável; consultar prioridades antes de expandir backlog. |
| **Endereço padrão ausente do relacional** | UC06 e RN-09 do SRS exigem **um endereço padrão por cliente**; a tabela `Endereco` apresentada não explicita atributo para isso. | Alinhar como persistir a preferência (`is_default` ou referência equivalente), sem modificar o diagrama por conta própria. |
| **Criptografia em repouso** | A seção 5.3 do SRS exige criptografar dados sensíveis, mas não especifica mecanismo; orientação mais recente de stack privilegia simplicidade. | Registrar decisão de desenho e testes. Não supor que Django/MySQL atendam automaticamente à exigência. |
| **Filtros de eletrônicos** | SRS 4.2 inclui **avaliação média e prazo de entrega** além de preço e fabricante; o UC02 é mais limitado e há estimativas de frete simuladas. | Implementar os filtros com o alcance decidido e documentar critérios de avaliação/prazo antes de inventar cálculo. |
| **Estrutura final Django** | Apps e diretórios ainda não foram definidos no código. | Primeiro inspecionar o repositório; depois adaptar a estrutura sugerida. |

### Regra de precedência para decisões contraditórias

1. **Exigências/correções explícitas do professor e decisões posteriores do grupo** sobre escopo e modo de implementação, quando estiverem documentadas.
2. **SRS versão 1.1 entregue** para requisitos declarados, regras de negócio, restrições e requisitos não funcionais; **UC01–UC11** para detalhes de fluxo.
3. **Diagrama relacional e diagrama de domínio anexados** para entidades/relacionamentos; reconhecer diferenças de nomenclatura e divergências entre versões.
4. **Diagrama de casos de uso** para atores/relacionamentos de análise (não assumir que ator externo simulado seja uma API real).
5. **Planilha de funcionalidades** como inventário e status **da especificação**, não da implementação.
6. **Código existente** orienta como aplicar as decisões concretas de implementação, mas não anula sozinho um requisito documental; divergência significativa precisa ser explicitada.
7. Se fontes ainda divergirem, registrar `TBD` e não inventar requisito.

---

## 12. Materiais de referência existentes na elaboração deste contexto

Os nomes abaixo identificam os materiais acadêmicos consultados/discutidos; **não pressupor que esses arquivos já estejam dentro do repositório de código**.

- `Software Requirements Specification(1).pdf` — **SRS do grupo, versão 1.1 aprovada, revisada em 03/11/2026**; contém Introdução, Descrição Geral **2.1–2.7**, Interfaces **3.1–3.4**, três módulos de requisitos funcionais na seção 4, requisitos não funcionais e regras RN-01–RN-20 nas seções 5–6 e **apêndices com diagramas, glossário e TBDs**. **Não é um template em branco.**
- `Descrição de casos de uso - IHC(1).pdf` — 11 UCs (UC01–UC11) com fluxos principais, alternativos, exceções e RN locais; seu texto contém algumas inconsistências que precisam ser registradas, não repetidas como regra final.
- `Funcionalidades - Amazon - Página1(3).pdf` — inventário amplo de funcionalidades, atores, classes e **status do levantamento**; não evidencia código pronto.
- `Diagrama de Casos de Uso Completo.drawio.pdf` — visão dos atores e dos casos de uso. Inclui **atores externos conceituais** para pagamento e transporte, cuja execução é simulada segundo o SRS.
- `Diagrama de tabelas .drawio.pdf` — modelo relacional apresentado, incluindo **`HistoricoStatusPedido`**, **`ItemListaDeDesejos`**, tabelas de pagamento e chaves PK/FK; apresenta pequenas lacunas em relação aos casos de uso, como endereço padrão.
- **Apêndice B do próprio SRS 1.1** — reproduz os diagramas de tabelas, casos de uso e domínio; no domínio ainda aparece uma classe `Entrega` e a classe `Timestamp`.
- **Figura 1 do SRS 1.1** — contexto modular com API CEP e serviços de pagamento/PIX/transporte **representados como externos, mas simulados** (exceto CEP).
- **Figura 2 do SRS 1.1** — mockups iniciais de Home, Página do Produto, Carrinho, Pedidos, endereço e pagamento.

**Importante:** o arquivo SRS 1.1 **não confirma Python, Django ou MySQL**: a escolha recente do grupo por **Python sem Docker** veio **depois** da documentação, e Django/MySQL permanecem propostas para implementação. Não alterar o histórico do documento original ao descrever essas escolhas.

---

## 13. Checklist para qualquer agente ao receber uma tarefa

Antes de alterar código, conferir:

- [ ] Qual UC, **RF/RN/RNF do SRS v1.1**, funcionalidade ou decisão recente fundamenta a alteração?
- [ ] A funcionalidade já existe? Qual app/model/view/template está envolvido?
- [ ] A solução é simples, usa Python, dispensa Docker e segue a stack Django + Templates + MySQL **caso esteja confirmada no repositório/grupo**?
- [ ] Os modelos e relacionamentos são compatíveis com os diagramas **e** com o código atual?
- [ ] Há autenticação, autorização e isolamento entre clientes onde necessário, observando as exigências de **HTTPS** e **criptografia em repouso** expressas no SRS?
- [ ] Pagamento e entrega permanecem simulados, sem dados reais sensíveis?
- [ ] O tratamento de erros preserva a consistência dos dados?
- [ ] Foram criados testes focados nos fluxos principais e alternativos relevantes?
- [ ] Quais decisões permaneceram `TBD` ou exigem alinhamento do grupo?

**Princípio final:** implementar o **menor conjunto de componentes possível** (prioritariamente Django, se confirmado) que cumpra o comportamento documentado, preservando as obrigações realmente assumidas no SRS e registrando requisitos conflitantes. O projeto deve parecer um e-commerce acadêmico bem construído, **não uma plataforma Amazon em produção**.
