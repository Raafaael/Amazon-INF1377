# TODO.md — Semana 2 | Checkout, pedidos, pagamentos e entrega

> **Projeto:** Amazon — e-commerce acadêmico em Django  
> **Entrega:** Semana 2 — finalizar compra e acompanhar pedido  
> **Integrantes:** Breno, Rafael, Yuri, Pedro e Davi  
> **Período e prazo do professor:** a preencher pelo grupo  
> **Situação inicial desta semana:** a Semana 1 já forneceu catálogo, produtos, autenticação básica e carrinho; verificar o código integrado antes de editar.  
> **Documentos de referência:** `AGENTS.md`, `context.md`, SRS v1.1, diagramas e casos de uso pertinentes.  
> **Histórico:** o planejamento original, com os registros da Semana 1, está preservado separadamente em `TODO_semana_1_arquivado.md` (se esse arquivo for adicionado ao repositório).

## 1. Objetivo da Semana 2

Completar um **fluxo acadêmico de compra demonstrável**, a partir do carrinho implementado na Semana 1:

1. Cadastrar e selecionar **endereços**, com preenchimento por **ViaCEP**.
2. Escolher modalidade de **frete** e mostrar valor/prazo simulados.
3. Finalizar a compra com **cartão fictício ou PIX simulado**, incluindo **QR Code de demonstração**.
4. Criar e consultar **pedidos**, preservando itens, preços, totais e status.
5. Simular o **andamento da entrega**, com histórico compreensível para o usuário.

**Escopo da demonstração:** catálogo → carrinho → checkout → endereço/frete → pagamento simulado → pedido → acompanhamento. A compra deve ser fictícia, sem cobrança ou entrega real. A simulação pode usar valores fixos, booleanos e aleatoriedade controlada, desde que o resultado seja persistido e permaneça coerente.

**Não fazer nesta semana:** gateway bancário real, PIX cobravel, APIs de transportadoras, cálculo profissional de frete, cadastro completo de clientes, marketplace, cupons, devoluções/reembolsos reais, notificações externas, filas, microsserviços ou telas que não ajudem a demonstrar essa entrega. Não implementar sistemas complexos de anti-fraude ou estoque reservado.

### Tecnologias e limites

- Continuar **Python + Django + ORM + Django Templates + Bootstrap + JavaScript simples**, aproveitando o repositório da Semana 1. **Sem Docker** ou frontend separado.
- Preservar o banco de dados e as convenções realmente existentes; não trocar SQLite por MySQL por iniciativa própria. MySQL continua uma proposta para decisão do grupo.
- Reaproveitar a autenticação nativa do Django. Cliente acessa apenas seus próprios endereços, pagamentos e pedidos; alterações administrativas exigem autorização no backend.
- Valores monetários devem usar `Decimal`; formulários de alteração devem usar POST e CSRF. Validar dados no servidor mesmo quando houver máscara/JavaScript.
- **Simulações explícitas:** indicar na interface quando pagamento, prazo ou movimentação são fictícios. Não gerar QR Code que possa efetuar uma cobrança real. Não armazenar CVV ou número completo de cartão real; utilizar dados fictícios e guardar, quando necessário, somente informações mascaradas.
- A consulta **ViaCEP** é a integração HTTP externa simples prevista. Tratar CEP desconhecido, falha de rede e campos não retornados. Para demonstrações, utilizar dados pessoais fictícios.
- Requisitos gerais de segurança do `context.md` (inclusive o tema de proteção de dados em repouso e HTTPS ao transmitir dados pessoais) continuam válidos e exigem uma decisão técnica do grupo; não afirmar que estão atendidos automaticamente pelo Django ou pelo uso de dados fictícios.

## 2. Divisão das tarefas — todos podem começar em paralelo

| ID | Responsável | Entrega principal | Demonstração própria da tarefa |
|---|---|---|---|
| **T06** | **Breno** | Pedidos, itens, valores e histórico de status | Lista **Meus pedidos** e página de detalhes |
| **T07** | **Rafael** | Endereços, endereço padrão e ViaCEP | Página **Meus endereços** com cadastro/edição |
| **T08** | **Yuri** | Simulação de frete, prazo e andamento de entrega | **Simulador de frete** e linha do tempo de entrega |
| **T09** | **Pedro** | Pagamento simulado por cartão e PIX | Formulário com **máscaras** e **QR Code de PIX fictício** |
| **T10** | **Davi** | Checkout e composição das páginas de finalização | **Checkout em etapas** e confirmação do pedido |

**Regra de trabalho:** as cinco tarefas podem começar sobre a base integrada da Semana 1. Cada integrante implementa a lógica **e a interface simples de seu módulo**, sem deixar todas as telas para Davi. Davi fica com a composição do checkout e o estilo compartilhado, não com a responsabilidade de construir todas as interfaces dos outros.

**Dependências de integração, não de início:** inicialmente, cada integrante testa seu módulo com objetos/valores de demonstração e um contrato combinado. Assim que os módulos reais estiverem disponíveis, a interface passa a utilizá-los; não manter dados simulados como se fossem pedidos ou pagamentos efetivos. Não exigir que todos terminem para começar a própria tarefa. As integrações cruzadas são revisadas pelo grupo ao final da semana.

### 2.1. Contratos mínimos para evitar retrabalho

Estas são **interfaces lógicas sugeridas**, e não APIs REST obrigatórias nem funções já existentes. Antes de codificar, conferir o repositório e manter nomes compatíveis com o que estiver sendo implementado.

| Responsável | Entrada principal | Saída/contrato para a integração |
|---|---|---|
| **Breno** | Usuário, itens do carrinho, endereço de entrega quando necessário, frete e modalidade | `Pedido` com ID, itens/preços congelados, total e status; serviço de criação e consulta de pedidos |
| **Rafael** | Usuário e dados/CEP do endereço | Endereços válidos do usuário; identificador de endereço selecionável e dados para exibição |
| **Yuri** | CEP, tipo de entrega e, para acompanhamento, pedido/status atual | Cotação com `valor`, `prazo_dias`, `tipo`; transições simuladas de status e informações de acompanhamento |
| **Pedro** | Referência do pedido, valor e modalidade cartão/PIX | Resultado com status `PENDENTE`, `APROVADO` ou `RECUSADO`; dados fictícios de confirmação/QR |
| **Davi** | Dados fornecidos pelos quatro módulos | Formulários e navegação que orquestram o fluxo sem duplicar as regras de negócio |

**Acordos simples de integração:**

1. Reutilizar `catalog.Produto` e o carrinho da Semana 1; **não duplicar** usuário, produto, carrinho ou autenticação.
2. Os apps sugeridos são `orders` (Breno), `addresses` (Rafael), `shipping` (Yuri) e `payments` (Pedro). O checkout pode ser implementado em `checkout` (Davi) ou por views próprias, conforme o padrão existente; **cada um confirma nomes e rotas no código real**. Não criar um app por tabela sem necessidade.
3. Evitar imports obrigatórios de um app ainda inexistente no início da tarefa. Testes e protótipos podem usar doubles/mocks locais; a integração deve substituir essas dependências antes da demonstração.
4. Um pedido guarda o **preço unitário do momento da compra**, os valores de frete/total e, quando necessário, os dados do endereço utilizados na compra. Mudanças posteriores no produto ou endereço não devem reescrever o pedido histórico.
5. **Uma única fonte para status/histórico do pedido:** Breno define o modelo/serviço de atualização; Yuri utiliza esse contrato para simular a entrega, evitando criar uma tabela paralela `Entrega` somente para rastreamento. O modelo relacional de referência usa `HistoricoStatusPedido`.
6. O pagamento só altera o pedido para pago quando a simulação informar **aprovação**. Uma recusa não pode aparecer como compra aprovada; PIX pendente continua pendente até simular confirmação.
7. O checkout deve utilizar serviços de pedidos, endereço, frete e pagamento em vez de reproduzir suas validações. Cada integrante conserva suas páginas próprias de demonstração.
8. Arquivos compartilhados (`config/urls.py`, `config/settings.py`, `requirements.txt`, `templates/base.html`, CSS global e migrations de apps de terceiros) exigem cuidado: acrescentar apenas o necessário, preservar mudanças existentes e coordenar integrações. Cada responsável edita principalmente seu app/templates próprios.
9. Simulações aleatórias podem acontecer **na ação de gerar uma cotação/resultado**, não a cada carregamento de página. Persistir o resultado escolhido. Para testes e demonstração, permitir cenários **determinísticos** (ex.: forçar aprovação/recusa), sem depender do sorteio.
10. A opção de **livro digital/e-book** está citada nas regras do SRS, mas o modelo existente pode não distinguir físico de digital. Verificar o que foi realmente modelado; não presumir que todo livro é digital. Se ainda não houver indicador, registrar essa decisão para integração e não exigir endereço/frete em pedido comprovadamente exclusivamente digital.

---

## T06 — Breno · Pedidos e consulta do histórico de compras

**Estado:** [ ] Não iniciado  
**Prioridade:** alta  
**Base já disponível:** modelos de produtos, carrinho e autenticação da Semana 1  
**Referências:** UC07 (detalhes), UC10 (consultar pedidos), regras de pedidos no `context.md`, modelo relacional (`Pedido`, `ItemPedido`, `StatusPedido`, `HistoricoStatusPedido`).

**Objetivo:** permitir que uma compra simulada seja registrada de forma consistente e consultada pelo próprio usuário, com uma interface de histórico simples e útil.

**Checklist**

- [ ] Criar o app/módulo de pedidos e os models necessários de **`Pedido`**, **`ItemPedido`** e histórico de status, aproveitando a nomenclatura do modelo relacional quando adequado.
- [ ] Registrar cliente, data, estado, itens, quantidades, preço unitário registrado na compra, subtotal de itens, frete e total; informações de entrega são opcionais quando não se aplicam.
- [ ] Criar serviço simples para gerar um pedido a partir dos itens do carrinho, validando carrinho não vazio, quantidades e disponibilidade, sem duplicar o pedido em uma submissão repetida do mesmo checkout.
- [ ] Preservar os preços do pedido mesmo quando o preço do `Produto` mudar depois; calcular valores com `Decimal`.
- [ ] Disponibilizar atualização de status por um serviço controlado e registro de **histórico** (data, novo estado e observação quando aplicável); restringir transições incoerentes.
- [ ] Criar a página **Meus pedidos** (mais recentes primeiro) com identificador, data, valor e situação, e a página **Detalhes do pedido** com itens, totais, tipo/endereço de entrega quando aplicáveis e histórico.
- [ ] Garantir que um cliente não veja o pedido de outro. Não permitir alteração arbitrária de status por clientes.
- [ ] Criar dados/testes de demonstração para consultar pedidos sem depender da implementação pronta do checkout, do pagamento ou do frete.
- [ ] Documentar para Pedro e Yuri como consultar o pedido e atualizar o status; documentar para Davi como criar o pedido no fluxo de checkout.

**Critério de conclusão:** é possível criar um pedido de demonstração consistente, consultar uma listagem e detalhes próprios e observar seu histórico; modelos e serviços ficam preparados para a finalização real da Semana 2.

**Limite:** não implementar simulador de cartão/PIX, ViaCEP, cálculo de frete ou telas de checkout. Não inventar uma logística profissional nem implementar devoluções e reembolsos nesta semana.

---

## T07 — Rafael · Endereços, endereço padrão e ViaCEP

**Estado:** [ ] Não iniciado  
**Prioridade:** alta  
**Base já disponível:** usuário autenticado Django  
**Referências:** UC06, RN-09 a RN-11 e requisitos de privacidade/endereço do `context.md`.

**Objetivo:** permitir que cada usuário cadastre e selecione endereços de entrega, com consulta de CEP e uma interface própria que possa ser reutilizada no checkout.

**Checklist**

- [ ] Criar o model **`Endereco`** associado ao usuário, com CEP, logradouro, número, complemento opcional, bairro, cidade, estado, tipo e indicador de endereço padrão (ou outra representação simples equivalente).
- [ ] Implementar cadastro, listagem, edição e seleção de endereço padrão, com exclusividade: **no máximo um padrão por usuário**.
- [ ] Utilizar **ViaCEP** para preencher automaticamente os campos disponíveis depois da consulta de um CEP válido. Permitir que o usuário complete os campos não retornados.
- [ ] Tratar CEP com formato inválido, CEP inexistente, resposta incompleta e falha/indisponibilidade do serviço, com mensagens claras.
- [ ] Criar a página **Meus endereços** com cartões/listagem e formulário organizado, incluindo máscara simples `00000-000` para o CEP. A máscara não substitui validação no servidor.
- [ ] Validar o número obrigatório e o complemento opcional; impedir consulta, alteração ou exclusão de endereços pertencentes a outro usuário.
- [ ] Disponibilizar para o checkout a listagem dos endereços do usuário e a escolha de um endereço existente; preparar ligação simples para criar um novo endereço quando necessário.
- [ ] Criar testes com respostas ViaCEP simuladas para não depender da internet; verificar endereço padrão e isolamento entre usuários.
- [ ] Documentar a estrutura do endereço utilizada pelo pedido e pelo checkout, sem exigir que esses módulos estejam prontos para testar o cadastro.

**Critério de conclusão:** o usuário cadastra um endereço com preenchimento por CEP, edita seus dados, define um padrão e consegue selecioná-lo por uma interface própria; falhas da consulta externa são tratadas adequadamente.

**Limite:** não criar cadastro completo de usuários, cálculo de frete nem checkout. Não solicitar dados pessoais reais para a demonstração.

---

## T08 — Yuri · Frete fictício e acompanhamento de entrega

**Estado:** [ ] Não iniciado  
**Prioridade:** alta  
**Base já disponível:** CEP e modalidades do domínio; pedido pode ser representado por dados fictícios nos testes iniciais  
**Referências:** tipos de entrega `PADRAO`, `EXPRESSA`, `AGENDADA`; estados e histórico de pedido; simulação de transporte prevista no `context.md`.

**Objetivo:** oferecer uma escolha de frete interessante para a demonstração e um acompanhamento visual da evolução de uma entrega, **sem transportadora real**.

**Checklist**

- [ ] Implementar um serviço de cotação fictícia que receba o CEP (quando aplicável) e a modalidade e devolva **valor em reais e prazo estimado em dias**.
- [ ] Oferecer modalidades **Padrão**, **Expressa** e **Agendada**; para a agendada, permitir selecionar/mostrar uma data futura de entrega simulada, sem criar agendamento externo.
- [ ] Usar uma lógica simples e explicável para cotação (tabela fixa por modalidade ou aleatoriedade controlada); evitar retornar valores diferentes ao apenas recarregar a página.
- [ ] Criar um pequeno **simulador de frete** com CEP, opções de entrega e comparação dos valores/prazos, utilizando Bootstrap e templates do Django.
- [ ] Implementar a evolução fictícia do pedido após pagamento aprovado, por exemplo **EM_PREPARACAO → ENVIADO → ENTREGUE**, com datas coerentes e sem saltos incoerentes ou entrega anterior ao envio.
- [ ] Criar uma **linha do tempo de acompanhamento** com status atual, eventos e previsão; disponibilizar avanço de estado por botão de simulação com permissão administrativa ou por mecanismo demonstrativo protegido, nunca por alteração livre de qualquer cliente.
- [ ] Integrar o registro de status pelo contrato definido por Breno quando estiver disponível. Até lá, testar com pedidos fictícios/mocks, sem manter uma implementação paralela de `HistoricoStatusPedido` ou criar tabela `Entrega` desnecessária.
- [ ] Registrar os valores/prazos escolhidos no pedido durante a integração e não sortear novamente depois da confirmação.
- [ ] Criar testes de cotação, modalidade, cronologia, autorização e transições válidas, com resultados determinísticos.

**Critério de conclusão:** o usuário consegue visualizar e comparar modalidades de frete, e um pedido de demonstração pode avançar por estados simulados com uma linha do tempo consistente.

**Limite:** não integrar Correios/transportadoras, mapas, rastreio real, cálculo de peso/dimensão ou APIs de previsão de chegada. Não criar uma entidade de entrega adicional sem necessidade do modelo existente.

---

## T09 — Pedro · Pagamento simulado com cartão e PIX (QR Code)

**Estado:** [ ] Não iniciado  
**Prioridade:** alta  
**Base já disponível:** usuário autenticado, valor fictício da compra; pedido pode ser mock nos testes iniciais  
**Referências:** UC09, regras de pagamentos simulados e `Pagamento`, `PagamentoCartao`, `PagamentoPix` do `context.md`.

**Objetivo:** simular as duas modalidades de pagamento de maneira convincente e segura para uma demonstração acadêmica, com interface própria e sem transação financeira real.

**Checklist**

- [ ] Criar lógica/modelos mínimos para registrar **modalidade, valor, status, referência do pedido e resultado simulado**, sem duplicar o total da compra de forma inconsistente.
- [ ] Implementar pagamento por **cartão fictício**, com formulário de número de demonstração, nome, validade e CVV apenas para validação transitória; incluir **máscaras de entrada** para número e validade e indicação clara de ambiente de simulação.
- [ ] Validar o formato dos dados no servidor. **Nunca salvar CVV, número completo de cartão real ou credenciais bancárias**; guardar, se necessário, somente bandeira fictícia e últimos quatro dígitos para exibição.
- [ ] Simular cartão **aprovado ou recusado**, usando booleano/aleatoriedade controlada ou opção de cenário de teste, com mensagem explicando o resultado.
- [ ] Implementar **PIX fictício** com identificador/código de demonstração e **QR Code gerado localmente** (por exemplo, com dependência Python pequena como `qrcode`, se necessária). O conteúdo do QR deve ser uma referência **não pagável**, rotulada como `PIX SIMULADO`, e não uma cobrança PIX real.
- [ ] Disponibilizar ações de **Simular pagamento PIX** e, se pertinente, de cancelamento/expiração simulada, atualizando o status apenas por ação explícita.
- [ ] Criar uma página/componente próprio para demonstrar **Cartão** e **PIX**, com feedback de pagamento aprovado, recusado ou pendente; oferecer partial/form reutilizável no checkout de Davi.
- [ ] Respeitar a regra: somente pagamento aprovado permite marcar pedido como pago; valor registrado deve coincidir com o do pedido; não aprovar recusa nem confirmar PIX automaticamente ao mostrar o QR.
- [ ] Criar testes para aprovação, recusa, PIX pendente e confirmado, valores e dados inválidos, permissões e persistência do resultado; testes reproduzíveis sem depender de sorteio.
- [ ] Documentar para Breno e Davi a chamada de processamento e os possíveis resultados, sem exigir que o checkout ou o model final do pedido estejam concluídos para iniciar.

**Critério de conclusão:** uma pessoa consegue simular cartão aprovado/recusado e gerar um QR Code PIX **exclusivamente demonstrativo**, confirmar o pagamento fictício por ação própria e visualizar resultados persistentes.

**Limite:** não integrar bancos/gateways, não aceitar cartão real, não gerar QR PIX cobrável, não implementar assinatura de webhook, antifraude ou parcelas complexas.

---

## T10 — Davi · Checkout em etapas e confirmação da compra

**Estado:** [ ] Não iniciado  
**Prioridade:** alta  
**Base já disponível:** Home, página de produto, login, `base.html` e carrinho da Semana 1  
**Referências:** fluxos de finalização da compra, telas do SRS e operações de carrinho/pedidos/endereço/pagamento descritas no `context.md`.

**Objetivo:** transformar o carrinho da Semana 1 em um fluxo de compra compreensível e navegável, com interface consistente e sem concentrar em um só integrante as telas dos demais módulos.

**Checklist**

- [ ] Implementar o acesso **Finalizar compra** no carrinho somente para usuário autenticado e com itens válidos.
- [ ] Criar um **checkout simples em etapas**, por exemplo: **1. Endereço → 2. Entrega → 3. Pagamento → 4. Confirmação**, com indicação visual de progresso; não criar uma SPA nem um wizard complexo.
- [ ] Reutilizar a seleção/cadastro de endereço de Rafael, a cotação de frete de Yuri, o formulário de cartão/PIX de Pedro e a criação do pedido de Breno por contratos simples, sem duplicar a lógica nos templates.
- [ ] Mostrar um **resumo do pedido** durante a finalização: produtos, quantidades, subtotal, frete e total. Revalidar esses dados no servidor antes de confirmar.
- [ ] Exibir os campos e resultados adequados ao método de pagamento escolhido: cartão de demonstração com máscara, ou PIX com QR fictício; não recriar o simulador de Pedro.
- [ ] Criar tela de **confirmação/resultado** com identificador do pedido e seu estado correto: pagamento aprovado, recusado ou PIX pendente. Não declarar compra paga antes da aprovação.
- [ ] Garantir que atualizar a página, voltar uma etapa ou reenviar o formulário não crie pedidos duplicados nem altere valores já confirmados.
- [ ] Tratar carrinho vazio, usuário não autenticado, endereço não selecionado, indisponibilidade de estoque e falha de pagamento com mensagens claras.
- [ ] Manter o layout consistente com a Semana 1, usando templates reutilizáveis, Bootstrap e CSS simples. Ajustar apenas a navegação compartilhada necessária para acessar checkout/pedidos.
- [ ] Criar testes simples do fluxo e de autorização, inicialmente com serviços simulados/mocks enquanto os outros módulos são desenvolvidos e, na integração final, usando os serviços reais.

**Critério de conclusão:** a partir de um carrinho com produtos, o cliente consegue percorrer as etapas, visualizar valores, escolher uma modalidade de pagamento simulada, concluir ou receber o status apropriado e acessar o pedido gerado.

**Limite:** não assumir para si cadastro de endereço, cálculo de frete, motor de pagamentos ou models de pedido — essas funcionalidades pertencem aos outros responsáveis. Não criar telas futuras ou exigir integrações externas reais.

---

## 3. Integração e demonstração final da Semana 2

A implementação de cada T06–T10 é responsabilidade do respectivo integrante. **A integração final é uma verificação coletiva**, não uma sexta tarefa que deve ser executada integralmente por Davi ou Breno.

**Roteiro mínimo de demonstração:**

- [ ] No Admin, há produtos suficientes para colocar no carrinho; o cliente consegue fazer login.
- [ ] O cliente cadastra um endereço, consulta um CEP no ViaCEP e define seu endereço padrão.
- [ ] O cliente coloca produtos no carrinho e inicia o checkout.
- [ ] O checkout apresenta o endereço e opções de frete com prazo e total coerentes.
- [ ] Com cartão fictício, é possível demonstrar **uma aprovação e uma recusa** sem realizar cobrança real.
- [ ] Com PIX, aparece **QR Code fictício**, o pagamento fica inicialmente pendente e somente uma ação de simulação o confirma.
- [ ] A compra gera um pedido com itens, quantidades, preços registrados, frete e total corretos; atualizações de página não duplicam pedido.
- [ ] A consulta **Meus pedidos** exibe somente os pedidos do cliente e abre os detalhes.
- [ ] A entrega pode evoluir por estados válidos e apresenta linha do tempo/data coerentes; um pedido não pago não pode aparecer como entregue.
- [ ] Os principais formulários respondem corretamente a valores inválidos, falta de estoque e acesso de outro usuário.
- [ ] Executar `python manage.py check`, `python manage.py test` e migrações aplicáveis; corrigir falhas relacionadas à integração.
- [ ] As interfaces relevantes são navegáveis em desktop e em uma tela menor, sem botões que simulem funcionalidades não implementadas como se fossem reais.

### Decisões pequenas a registrar pelo grupo durante a integração

- **Quando criar e limpar o pedido/carrinho:** adotar um fluxo consistente que não perca itens em uma recusa e não duplique pedidos. Sugestão acadêmica: criar pedido `AGUARDANDO_PAGAMENTO` quando o usuário confirma o checkout; registrar resultado e limpar o carrinho somente após aprovação, evitando reutilizar a mesma intenção de checkout. Para PIX pendente, preservar pedido pendente e não limpá-lo como compra paga.
- **Frete e prazos:** valores podem ser tabelados ou sorteados, mas a cotação escolhida fica registrada e as datas são coerentes. A modalidade `AGENDADA` representa um agendamento fictício.
- **Dados digitais:** não exigir endereço/frete para compra comprovadamente apenas de e-book; se o projeto não diferencia digital e físico, apontar a lacuna e alinhar antes de criar uma regra arbitrária.
- **Histórico e status:** manter um único modelo/serviço de histórico de pedidos e só permitir transições compatíveis com a simulação adotada.
- **Segurança:** nenhuma transação real, dados reais de cartão, CVV persistido ou dados de terceiros acessíveis. Documentar decisões sobre proteção de dados pessoais do SRS sem alegar conformidade não verificada.

## 4. Orientações finais para agentes

1. Identificar o integrante e sua tarefa **T06–T10** no período vigente. Ler `AGENTS.md`, `context.md` e verificar o código existente; **não** selecionar as tarefas antigas T01–T05.
2. Implementar apenas o módulo solicitado, incluindo a **interface própria** e os testes pertinentes. Respeitar os contratos compartilhados e não antecipar funções atribuídas a outro integrante.
3. Scripts, migrações não destrutivas e testes são permitidos conforme `AGENTS.md`. **Não realizar `git add`, `git commit`, `git push`, merges, troca de branches ou operações que alterem o histórico/estado do Git.**
4. Seguir o fluxo de avaliação e documentação definido em `AGENTS.md`, utilizando o **mesmo relatório individual** ao receber alterações posteriores nesta semana. Não reproduzir protocolos paralelos no `TODO.md`.
5. **Estados:** `[ ]` não iniciado, `[~]` em andamento, `[x]` concluído após verificação. Não alterar marcações ou atribuições sem solicitação do integrante/grupo.

> **Princípio da entrega:** um e-commerce acadêmico simples, funcional e demonstrável, com módulos pequenos desenvolvidos em paralelo e integrações simuladas coerentes — sem infraestrutura profissional desnecessária.
