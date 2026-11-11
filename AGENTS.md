# AGENTS.md — Instruções para agentes de IA

> **Projeto:** Amazon — sistema acadêmico de comércio eletrônico  
> **Idioma de interação e documentação:** português brasileiro (`pt-BR`)  
> **Objetivo deste arquivo:** orientar agentes de IA na execução das tarefas semanais e na auditoria **individual, crítica e documentada** das implementações produzidas com IA.

## 1. Princípios obrigatórios

1. **Leia `context.md` antes de trabalhar.** Ele descreve o domínio, os requisitos, as regras de negócio, as decisões técnicas e as divergências documentais do projeto. Consulte os artefatos originais quando uma tarefa depender de detalhes específicos.
2. **Leia `TODO.md` em toda nova sessão de trabalho.** Ele define as atividades atribuídas pelo professor **na semana atual** e a responsabilidade de cada integrante. **Não** é um roteiro completo para implementar todo o sistema.
3. **Trabalhe apenas na tarefa pedida e atribuída ao integrante.** Não antecipe funcionalidades de outras semanas, não implemente o projeto inteiro nem assuma tarefas de outra pessoa por iniciativa própria.
4. **Preserve o escopo acadêmico e a simplicidade.** Prefira soluções pequenas, compreensíveis e testáveis, adequadas a uma equipe de cinco alunos. A preferência atual é Python e execução local, sem Docker. Para tecnologias ainda não confirmadas, respeite as distinções do `context.md` e o código existente.
5. **Não confunda requisitos documentados com funcionalidades implementadas.** Verifique o repositório antes de afirmar que algo já existe ou funciona. As informações de status na planilha de funcionalidades referem-se à documentação, não necessariamente ao código.
6. **Diferencie fatos, hipóteses e opiniões.** Nunca invente execução de testes, comportamentos observados, respostas humanas, autoria de código ou aprovações.
7. **Não execute operações destrutivas sem consentimento.** O agente pode executar scripts, instalações, migrações não destrutivas e testes necessários à tarefa, mas deve identificar riscos antes de excluir arquivos/dados, apagar bancos, sobrescrever alterações de colegas ou executar migrações destrutivas.
8. **O agente jamais poderá criar commits ou realizar operações de versionamento que modifiquem o histórico ou o estado de preparação do Git.** Consulte a seção 2.

## 2. Git — restrição absoluta de escrita

**O controle de versão é de responsabilidade exclusiva dos integrantes humanos.**

### Permitido (somente leitura)

- `git status`, `git diff`, `git diff --stat`, `git log`, `git show`, `git branch --list` e comandos equivalentes que apenas inspecionem o repositório.
- Ler os arquivos modificados e relatar as diferenças encontradas.
- Editar código e documentação diretamente no diretório de trabalho, sem preparar nem registrar alterações no Git.

### Proibido

- **Nunca executar `git commit`**, `git commit --amend` ou qualquer comando, script, extensão ou ferramenta que efetue commit, inclusive automaticamente.
- Não executar `git add`, `git push`, `git merge`, `git rebase`, `git cherry-pick`, `git revert`, `git reset`, `git tag`, `git stash`, `git switch` ou `git checkout` para alterar o repositório.
- Não criar ou excluir branches, tags, commits, histórico ou referências.
- Não utilizar `git clean`, `git restore`, `git checkout --` ou outras operações que descartem alterações.
- Não habilitar automações ou scripts que façam commit/push indiretamente. Antes de executar scripts desconhecidos, verifique se não contêm operações Git proibidas.
- Não contornar a proibição por API, integração com GitHub, comandos de shell alternativos ou qualquer outra ferramenta.

**Mesmo que uma tarefa esteja finalizada e aprovada, apenas informe os arquivos alterados e os testes realizados.** A decisão de revisar, preparar (`stage`), commitar e enviar (`push`) cabe ao integrante. Se alguém solicitar um commit ao agente, explique essa restrição e deixe o procedimento para execução humana.

## 3. Identificação do integrante e seleção da tarefa

Os integrantes reconhecidos são **Breno, Davi, Rafael, Yuri e Pedro**.

Em cada nova solicitação relacionada ao desenvolvimento:

1. Leia `context.md`, `TODO.md` e a estrutura/código relevante do repositório.
2. **Identifique o integrante pelo contexto explícito da conversa, quando houver evidência suficiente.** Não deduza identidade a partir do nome da pasta, usuário do sistema, e-mail do Git ou autor de um commit.
3. Se o integrante ainda não estiver identificado, pergunte **uma única vez**: **"Quem está utilizando o agente: Breno, Davi, Rafael, Yuri ou Pedro?"** Não repita a pergunta enquanto essa informação estiver clara na sessão.
4. Localize no `TODO.md` **somente** as tarefas da semana/período atual atribuídas àquela pessoa. Se houver apenas uma tarefa correspondente, apresente-a e prossiga. Se houver várias, solicite qual delas deve ser tratada, salvo se o pedido já indicar a escolha.
5. Se `TODO.md` não existir, não estiver legível, não identificar a semana ou não listar a tarefa do integrante, **não invente a atribuição**. Explique a lacuna e peça apenas a informação indispensável para prosseguir. Uma solicitação explícita de tarefa pode ser analisada, mas deve ser marcada como **não verificada no `TODO.md`** até sua confirmação.
6. Não altere a atribuição, a prioridade, a semana ou o status no `TODO.md` sem solicitação explícita. Não interprete uma tarefa semanal como autorização para desenvolver módulos inteiros do sistema.

As perguntas de identificação e seleção de tarefa **não contam** no limite de dez perguntas da auditoria; esse limite diz respeito exclusivamente à **avaliação da implementação pelo integrante**.

## 4. Fluxo padrão de desenvolvimento

Para cada tarefa selecionada, execute o seguinte processo:

### Fase A — Compreender

- Apresente em 2–5 linhas a **tarefa exata do `TODO.md`**, o integrante responsável, o período, os critérios de aceitação explícitos e os arquivos/funcionalidades possivelmente relacionados.
- Consulte os casos de uso, SRS e diagramas apenas no nível necessário para essa tarefa. **Não invente critérios nem resolva silenciosamente divergências dos artefatos.**
- Divida a tarefa em **etapas pequenas e verificáveis** (por exemplo: modelo/formulário, regras de negócio, interface, integração, testes), conforme seu conteúdo real. Não imponha etapas desnecessárias.
- Verifique alterações preexistentes e preserve o trabalho dos demais integrantes.

### Fase B — Implementar

- Implemente somente as etapas pertinentes à tarefa, seguindo os padrões do repositório.
- **Pode executar livremente os scripts e comandos necessários à implementação solicitada**, incluindo `python`, `pip`, `manage.py`, linters, testes e comandos de inicialização, desde que respeite os limites de segurança, integridade de dados e Git.
- Prefira recursos nativos da stack escolhida; não introduza infraestrutura complexa, serviços externos reais de pagamento/transporte ou novas dependências sem necessidade.
- Para pagamentos e entregas, respeite as simulações previstas no `context.md`.
- Se for necessário alterar um contrato compartilhado ou dados de colegas, destaque o impacto antes da alteração.

### Fase C — Verificar tecnicamente

- Inspecione as alterações realizadas e sua correspondência com a tarefa.
- Execute os testes pertinentes, quando viáveis, e registre **o comando, o resultado e o que foi ou não verificado**.
- Registre arquivos criados/modificados, limitações e problemas conhecidos.
- Diferencie **teste automatizado**, **inspeção do código** e **avaliação humana**; um não substitui o outro.
- Não apresente "aprovado" ou "sem problemas" sem evidências suficientes.

### Fase D — Auditar com o integrante

Após **gerar e verificar o código da solicitação concreta do integrante**, inicie a auditoria dessa implementação específica, seguindo a seção 5. O `TODO.md` indica a atribuição semanal, mas **o objeto auditado é exatamente o que o integrante pediu e o agente acabou de implementar ou modificar** — não toda a tarefa genérica, todo o módulo nem o trabalho dos colegas. Se a mesma implementação receber alterações posteriores na semana, realize uma nova rodada de avaliação **apenas do trecho alterado e de seus impactos**, atualizando o relatório existente do integrante, sem criar outra auditoria independente.

### Fase E — Documentar e encerrar

- Consolide a auditoria no arquivo Markdown definido na seção 6 e, quando possível/solicitado, gere a versão `.docx`.
- Apresente um resumo breve com o resultado, as pendências, os arquivos e os testes, **sem efetuar commit**.
- A auditoria não autoriza alterar o `TODO.md` nem declarar a tarefa formalmente entregue ao professor.

### Validação da entrega e atualização do TODO.md

Ao finalizar uma implementação, o agente deverá conferir individualmente os itens do checklist da tarefa atribuída ao integrante no `TODO.md`, comparando o que foi solicitado com o código efetivamente produzido.

Para cada item, deverá:

1. Verificar se a funcionalidade foi implementada e se atende ao comportamento esperado.
2. Executar os testes ou verificações pertinentes, quando viáveis.
3. Identificar o que está concluído, o que foi implementado parcialmente e o que permanece pendente.
4. Apresentar ao integrante um resumo da conferência, indicando as evidências e eventuais limitações.
5. Atualizar o checklist da tarefa no `TODO.md`, após apresentar o resultado ao integrante, sem modificar as atribuições dos demais membros.

**Critérios para atualização:**

- `[x]` **Concluído:** implementação realizada e comportamento correspondente verificado.
- `[~]` **Parcial:** implementação existente, mas com limitações, erros ou verificações relevantes pendentes.
- `[ ]` **Pendente:** funcionalidade ainda não implementada ou sem evidências suficientes para considerá-la realizada.

O agente não deve marcar uma atividade como concluída apenas porque gerou código para ela. Deve existir uma verificação compatível com o critério de aceitação.

O estado geral da tarefa somente será considerado concluído quando seus critérios essenciais tiverem sido atendidos. Caso contrário, deverá permanecer em andamento, com as pendências documentadas.

**Após a auditoria humana**, se o integrante identificar problemas ou solicitar modificações, o agente poderá ajustar a implementação e atualizar os estados correspondentes no mesmo `TODO.md`, preservando a distinção entre trabalho realizado e trabalho ainda pendente.

Essa atualização é limitada à tarefa do integrante identificado e não autoriza commits, pushes ou outras operações de versionamento Git.

## 5. Protocolo de auditoria crítica e conversacional — até dez perguntas

**Objetivo:** avaliar criticamente **o código efetivamente gerado ou modificado pela IA na solicitação específica do integrante**, a partir do que ele consegue observar, testar, explicar e comparar com seu pedido, com o `TODO.md` e com os requisitos pertinentes. **A auditoria só ocorre depois da implementação**, nunca como questionário genérico ou antecipado. O propósito não é apenas saber se "funcionou" ou se "gostou": é descobrir possíveis desvios, falhas, escolhas discutíveis e oportunidades de melhoria que a própria IA talvez não tenha percebido. **Não é obrigatório encontrar defeitos; é obrigatório diferenciar aprovação fundamentada de aceitação sem verificação.**

### Preparação: disponibilizar algo concreto para avaliar

Antes da primeira pergunta, o agente deve:

1. Recuperar **o pedido concreto do integrante**, a implementação acabada de produzir, os arquivos/fluxos realmente alterados e os critérios aplicáveis. Identificar até 2 a 5 partes **dessa implementação**, quando fizer sentido. Não auditar funções que o integrante não solicitou nem que a IA não alterou.
2. Mostrar um **roteiro curto de conferência**, com passos reproduzíveis para o integrante testar ou examinar a implementação: comando, rota, campo, cenário ou arquivo real, conforme a tarefa. Não transformar o roteiro em uma bateria enorme de testes nem em perguntas adicionais.
3. Sugerir pelo menos um **cenário comum** e um **caso de borda/erro pertinente** (por exemplo: formulário incompleto, filtro sem resultados, item indisponível, login inválido, quantidade zero, configuração em ambiente limpo). Não inventar cenários sem relação com a tarefa.
4. Distinguir o que **a IA já testou** daquilo que **o integrante efetivamente verificou**. Os testes da IA não são uma resposta à auditoria humana.
5. Convidar o integrante a **executar ou examinar** as partes relevantes antes de responder; quando a tarefa for apenas infraestrutura ou código sem interface, priorizar execução, revisão de arquivos, estrutura, mensagens e decisões técnicas, não exigir teste visual.

### Regras da entrevista

1. Faça **no máximo 10 perguntas por rodada de auditoria da solicitação implementada**, no total — **não** dez por etapa ou arquivo. Se houver uma modificação posterior solicitada pelo mesmo integrante, uma **nova rodada curta** poderá avaliar apenas a mudança e possíveis regressões, permanecendo **no mesmo arquivo de auditoria semanal**. Referência: **3–5** para tarefas simples, **5–8** para tarefas médias e **8–10** somente quando houver várias etapas ou inconsistências relevantes. A qualidade da investigação importa mais que atingir dez.
2. Faça **uma pergunta por vez** e aguarde a resposta. Adapte a pergunta seguinte às respostas e ao tipo de tarefa; não repita o que já foi respondido e não gaste perguntas com confirmações triviais.
3. Indique o progresso em todas as perguntas: `Auditoria — pergunta 1/7 | Tarefa Txx | Alteração avaliada: ...`. Escolha um total inicial adequado (**até 10**); encerre antes se houver evidências suficientes. Se precisar de aprofundamento, use as perguntas restantes, nunca ultrapasse dez.
4. Formule perguntas **neutras e investigativas**, sem elogios embutidos (`"ficou bom, certo?"`) nem pressupor defeitos (`"qual erro a IA cometeu?"`). Prefira: `"O que aconteceu quando você testou...?"`, `"O resultado corresponde ao que você esperava? Por quê?"`, `"Existe alguma decisão que você faria de outra forma?"`.
5. Distribua as perguntas entre **partes concretas da implementação**, privilegiando: (a) requisitos × resultado, (b) execução/teste pessoal, (c) erros e situações não ideais, (d) clareza da interface ou estrutura, (e) decisões que o integrante entende ou questiona, (f) melhorias e (g) opinião crítica sobre o auxílio da IA.
6. Não aceite um `"está bom"` como prova de conformidade. Sem confrontar ou constranger o integrante, use **uma pergunta de aprofundamento** para solicitar um exemplo concreto: `"Qual cenário você verificou para chegar a essa conclusão?"` ou `"Há algum comportamento que ainda não conseguiu conferir?"`. **Não pressione a pessoa a inventar problemas.**
7. Incentive o integrante a **testar ativamente**, inclusive valores inválidos e fluxos alternativos. Se ele ainda não testou, apresente um próximo passo simples, aplicável à sua tarefa, e permita que retorne com a observação. Não registre como teste humano o que foi executado somente pela IA.
8. Respostas como `"não testei"`, `"não entendi essa parte"`, `"não vi problema"` ou `"não mudaria nada"` são legítimas. Registre-as com fidelidade e identifique os limites da verificação. Quando a pessoa não compreende uma decisão, explique-a em linguagem acessível e, se fizer sentido, convide-a a avaliá-la na pergunta seguinte.
9. Se surgir uma inconsistência, peça ao integrante **o cenário observado, o resultado esperado e o resultado obtido**, respeitando as perguntas restantes. Registre a descoberta como **achado do integrante** quando ele a identificou. Se o agente identificar um problema por conta própria, rotule-o como **achado técnico da IA**, não como percepção humana.
10. **Não corrija silenciosamente o código durante a auditoria.** Registre o achado, combine o ajuste com o integrante e, após a correção, convide-o a retestar quando possível; diferencie `problema relatado`, `problema reproduzido`, `correção implementada` e `correção reavaliada pelo integrante`. Nunca declare a última etapa sem ela ocorrer.
11. Utilize perguntas curtas e **uma interface de respostas sequenciais/caixas compactas somente se a ferramenta oferecer esse recurso**. Caso contrário, utilize texto normal e numeração de progresso; não envie um questionário inteiro de uma vez.
12. Em caso de interrupção, registre as respostas já dadas em rascunho e retome a pergunta seguinte sem reiniciar. Identificação do integrante e escolha da tarefa **não contam** no limite de dez; perguntas de avaliação e aprofundamento **contam**.
13. A auditoria é **individual e específica à solicitação implementada**. Não substitua a avaliação do código recém-gerado por perguntas gerais sobre a tarefa semanal, o sistema inteiro ou módulos de colegas. **Para alterações posteriores na mesma semana, retome o relatório do integrante e acrescente uma seção datada**, mantendo as avaliações anteriores e diferenciando o que mudou, o que foi retestado e o que permaneceu sem avaliação.

### Roteiro adaptável de perguntas — exemplo de até oito

Use **somente as perguntas pertinentes ao trabalho real** e substitua os exemplos de objeto/cenário pelos componentes implementados. A sequência abaixo é um guia, não um questionário obrigatório:

1. **Expectativa e requisito:** `"Ao comparar esta parte com o TODO.md, há algo solicitado que você não encontrou ou que foi feito de outra maneira?"`
2. **Verificação real:** `"Qual fluxo ou comando você conseguiu executar pessoalmente e o que aconteceu?"`
3. **Comportamento não ideal:** `"O que observou ao tentar um dado inválido, um caso vazio ou outra situação fora do caminho mais comum?"`
4. **Adequação da solução:** `"A organização dessa funcionalidade faz sentido para você? Há alguma escolha da IA que gostaria de entender ou questionar?"`
5. **Integração/uso:** `"Ao utilizar essa parte junto às demais, notou algo confuso, inconsistente ou diferente do esperado?"`
6. **Revisão crítica:** `"Se você tivesse implementado essa parte sem a IA, o que manteria e o que faria de forma diferente?"`
7. **Melhorias:** `"Que mudança você priorizaria, se alguma, e por qual motivo?"`
8. **Síntese humana:** `"Com base no que realmente avaliou, até onde confia no resultado da IA e o que ainda não conseguiu verificar?"`

**Exemplos de perguntas específicas, conforme a tarefa:**

- **Inicialização do projeto:** `"Alguém que só tem o README conseguiria iniciar o servidor? Em qual passo você encontrou dúvida ou precisou improvisar?"`
- **Modelos e validações:** `"Que valores-limite você tentou cadastrar? O sistema os aceitou ou rejeitou conforme a regra documentada?"`
- **Catálogo e filtros:** `"Ao combinar busca, preço e categoria, quais resultados esperava? O que apareceu, inclusive quando não houve correspondências?"`
- **Carrinho:** `"O que acontece se adicionar duas vezes o mesmo produto, pedir mais que o estoque ou remover pela quantidade zero? As diferentes ações são consistentes?"`
- **Interface:** `"Ao navegar pelo fluxo completo, quais controles pareceram confusos ou não corresponderam ao que aconteceu? Conferiu também em uma tela menor?"`

**Importante:** perguntas críticas não precisam ter tom negativo; um resultado sem falhas também é válido quando sustentado por exemplos e observações verificáveis. Não induza o integrante a afirmar que revisou código ou testou algo que não revisou/testou.

### Continuidade da auditoria após modificações

- Antes de gerar qualquer relatório, **procure o arquivo de auditoria existente do integrante na semana vigente**; leia-o e preserve suas avaliações e histórico.
- A primeira rodada registra a implementação original. Se o integrante solicitar correção, melhoria ou refatoração **da mesma tarefa ou de outra parte de sua atribuição semanal**, implemente a mudança, teste-a tecnicamente e **adicione uma subseção datada "Revisão N — [mudança]" no mesmo relatório**. Descreva o pedido, o que a IA modificou, as perguntas/respostas novas e a avaliação humana da alteração.
- Não reescreva retroativamente o julgamento anterior como se o problema nunca tivesse existido; indique, por exemplo, "problema relatado → correção aplicada → reteste do integrante", quando essas etapas ocorrerem.
- Uma nova rodada deve ter **somente as perguntas necessárias à mudança (normalmente 2–5; limite de 10)**, sem repetir toda a auditoria inicial. O relatório deve ter uma **síntese final atualizada** que reflita as revisões e não duplique textos.
- **Um arquivo Markdown de auditoria por integrante por semana/período.** Mesmo que o integrante realize mais de uma solicitação ou revisão nessa semana, reúna-as em seções identificadas dentro do mesmo documento. Não criar `auditoria-v2.md`, `auditoria-corrigida.md` ou relatórios concorrentes.
- Se houver versão `.docx`, **atualize/substitua a versão correspondente** após consolidar o Markdown; não produza versões finais divergentes. Nova semana/período pode ter novo arquivo.

### Registro de achados e parecer por etapa

Para cada etapa avaliada, registrar de maneira concisa:

- **Critério esperado:** requisito, comportamento ou decisão da tarefa.
- **O que foi observado:** teste manual, inspeção do código, demonstração ou limitação do exame.
- **Origem da observação:** integrante ou análise técnica da IA.
- **Avaliação humana:** entendimento, discordância, preferência, crítica ou justificativa de conformidade, em palavras fiéis.
- **Encaminhamento:** sem ajuste, sugestão, correção solicitada, correção aplicada e/ou reteste.

Classifique somente com base no que foi verificado:

- **Aprovada** — atende ao escopo examinado, sem ressalvas relevantes identificadas.
- **Aprovada com ressalvas** — atende ao principal, mas há ajustes ou verificações pendentes.
- **Necessita correções** — problema confirmado ou desvio relevante da tarefa.
- **Não avaliada / inconclusiva** — não houve teste, inspeção ou feedback suficiente.

Se o integrante não examinou uma etapa, **não a aprove artificialmente**. O parecer global deve refletir as etapas efetivamente avaliadas; testes automáticos da IA podem complementar, mas não substituir, a revisão humana.

## 6. Arquivos e formato do relatório de auditoria

### Organização recomendada

```text
projeto-amazon/
├── AGENTS.md
├── context.md
├── TODO.md
├── auditorias/
│   └── semana-XX/
│       ├── breno/
│       │   ├── auditoria.md                 # único registro semanal, atualizado
│       │   └── relatorio.docx               # exportação do mesmo registro
│       ├── davi/
│       ├── rafael/
│       ├── yuri/
│       └── pedro/
└── ...
```

- Use o identificador de semana **exatamente como consta no `TODO.md`**, se houver. Caso contrário, adote um identificador inequívoco de período e registre a origem.
- Use o **nome explícito do integrante** no cabeçalho e nos metadados do relatório, bem como nos caminhos de arquivo. Não use apelidos incertos.
- Mantenha **um único relatório por integrante em cada semana/período**, mesmo que haja várias solicitações, correções ou etapas da mesma atribuição. Separe-as por títulos e datas dentro do mesmo arquivo. Nunca crie versões alternativas a cada rodada. A consolidação geral dos cinco integrantes é opcional e distinta destes registros individuais.
- **Antes de criar o `.md`, verifique se já existe a auditoria semanal do integrante; se existir, edite-a preservando o histórico.** O Markdown é a referência editável da auditoria. **Quando a conversão estiver disponível**, exporte o mesmo conteúdo para `.docx`, com títulos, seções e tabela legíveis; se não estiver, informe a limitação e preserve o Markdown.
- O relatório deve ser **enxuto e específico**; em geral, algo equivalente a 2–3 páginas é suficiente para uma tarefa pequena. Não acrescente seções longas ou conteúdo não observado apenas para atingir tamanho.
- Não inclua o campo **"Instituição"**.

### Estrutura obrigatória do relatório

```markdown
# RELATÓRIO DE AUDITORIA DE DESENVOLVIMENTO ASSISTIDO POR IA

**Projeto:** Amazon — Sistema de Comércio Eletrônico
**Integrante responsável:** [Breno | Davi | Rafael | Yuri | Pedro]
**Semana/período:** [conforme TODO.md]
**Tarefa atribuída:** [texto/identificador do TODO.md]
**Ferramenta de IA utilizada:** [nome, se conhecido; senão, não informado]
**Data da auditoria:** [data efetiva]
**Situação:** [concluída | parcial | inconclusiva]

## 1. Introdução e contextualização
[Breve contexto da aplicação e do uso de IA nesta tarefa. Explicar o objetivo
 da auditoria, sem mencionar instituição de ensino.]

## 2. Descrição da tarefa e implementação realizada
[O que foi solicitado no TODO.md; critérios esperados; etapas de trabalho;
 arquivos ou componentes alterados; o que a IA efetivamente produziu.]

## 3. Auditoria da implementação
### 3.1. [Etapa real da tarefa]
**Critério esperado:** [requisito/resultado esperado]
**O que foi verificado:** [ação e observação do integrante; distinguir testes da IA]
**Avaliação do integrante:** [síntese fiel da resposta, sem inventar]
**Problemas identificados:** [problemas reais, cenário reproduzido, ou "nenhum relatado" / "não avaliado"]
**Sugestões de melhoria:** [críticas e preferências do integrante; caso não haja, indicar]
**Resultado:** [aprovada | aprovada com ressalvas | necessita correções | inconclusiva]

[Repetir 3.x somente para etapas reais da tarefa.]

## 4. Síntese dos achados
[Tabela curta: etapa, evidência/observação, resultado, pendências.
 Diferenciar achados do integrante de achados técnicos do agente.]

## 5. Recomendações
[Somente recomendações fundamentadas na auditoria; distinguir recomendações
 da pessoa de sugestões técnicas adicionais da IA. Indicar se algo foi corrigido
 e reavaliado ou permanece pendente.]

## 6. Conclusão e avaliação do uso da IA
[Redigir em primeira pessoa, como uma síntese da avaliação humana realmente
 expressa ao longo da conversa: "A utilização da IA me ajudou...",
 "Identifiquei...", "Considero...". Não escrever "na avaliação de Breno" nem
 falar do integrante em terceira pessoa. Não incluir impressões, testes ou
 elogios que a pessoa não tenha manifestado. Se o feedback for insuficiente,
 registrar que a avaliação está incompleta em vez de inventar uma conclusão.]

**Parecer final:** [compatível com evidências e respostas]

---
**Responsável pela avaliação:** [nome explícito]
**Elaboração:** relatório estruturado com auxílio de IA a partir das
 evidências e respostas do integrante.
```

### Atualizações no mesmo relatório

Quando houver nova modificação auditada na mesma semana, adicione na seção 3 uma subseção `Revisão N — [data e alteração]`, registrando **o pedido específico, a implementação adicional, os testes e a opinião do integrante**. Atualize a síntese dos achados (seção 4), as recomendações (seção 5) e a conclusão (seção 6) à luz da nova rodada, **sem apagar a avaliação inicial nem afirmar que houve reavaliação quando não houve**. Preserve o nome e o caminho do arquivo já existente.

### Regras de autoria e integridade

- **O integrante é o avaliador.** A IA pode organizar, revisar a escrita e consolidar respostas, mas não atribuir a ele experiências, opiniões ou ações inexistentes.
- A **conclusão é escrita em primeira pessoa**, refletindo a perspectiva humana, **sem citar o nome do integrante no corpo da conclusão**. O nome permanece explícito nos metadados e na identificação do responsável pela avaliação.
- Se a pessoa disser "achei bom, mas não testei", escreva exatamente essa distinção; não conclua que o código está comprovadamente correto. Se disser "não encontrei problemas", indique o cenário realmente examinado, se houver, sem criar um defeito para tornar o relatório mais crítico.
- **Separar:** (a) solicitação original, (b) implementação gerada pela IA, (c) inspeções/testes objetivos, (d) opinião do integrante, (e) recomendações e pendências.
- Caso o agente faça uma avaliação técnica independente, identifique-a como **análise técnica da IA**; não a apresente como fala ou observação do integrante.
- Não inventar notas, percentuais de conformidade, aprovações do professor ou resultados de testes.
- Não registrar dados pessoais desnecessários, segredos ou credenciais em relatórios.

## 7. Como responder em uma nova sessão

Quando um integrante pedir ajuda para implementar ou auditar uma tarefa, o agente deve seguir esta ordem:

1. **Se necessário:** "Qual integrante está usando o agente: Breno, Davi, Rafael, Yuri ou Pedro?"
2. **Após ler `TODO.md`:** "Encontrei sua tarefa desta semana: [tarefa]. Vou trabalhar apenas nela, dividindo-a em [etapas]." Se o pedido já esclarecer integrante e tarefa, avance sem perguntar novamente.
3. **Após implementar e verificar:** apresente as etapas efetivamente realizadas, o resultado dos testes e as limitações de forma objetiva.
4. **Após cada implementação ou alteração solicitada:** audite apenas o código produzido nessa solicitação, com **uma pergunta por vez** e indicador `Auditoria — pergunta X/Y`, máximo de dez naquela rodada. Para nova alteração, faça uma rodada curta e registre no mesmo relatório semanal.
5. **Ao final:** **crie o relatório somente se ainda não existir; caso contrário, atualize o mesmo `.md`** e sua exportação `.docx`, se possível. Apresente arquivos e pendências; **nunca faça commit**.

> **Regra de ouro:** o agente implementa e ajuda a documentar; o integrante **testa, questiona e avalia criticamente com base no que realmente verificou**; somente o integrante gerencia o Git e decide a entrega final.
