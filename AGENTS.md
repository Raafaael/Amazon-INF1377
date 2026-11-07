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

As perguntas de identificação e seleção de tarefa **não contam** no limite de cinco perguntas da auditoria; esse limite diz respeito exclusivamente à **avaliação da implementação pelo integrante**.

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

Após a implementação, inicie uma **auditoria independente para cada tarefa**, seguindo integralmente a seção 5. Se houver várias tarefas semanais do mesmo integrante, **não misture as avaliações**: finalize uma auditoria antes de iniciar outra.

### Fase E — Documentar e encerrar

- Consolide a auditoria no arquivo Markdown definido na seção 6 e, quando possível/solicitado, gere a versão `.docx`.
- Apresente um resumo breve com o resultado, as pendências, os arquivos e os testes, **sem efetuar commit**.
- A auditoria não autoriza alterar o `TODO.md` nem declarar a tarefa formalmente entregue ao professor.

## 5. Protocolo de auditoria conversacional — máximo de cinco perguntas

**Objetivo:** reunir a percepção crítica do integrante sobre o código gerado pela IA, **por tarefa e por etapa relevante**, sem exigir que ele avalie o projeto inteiro de uma vez.

### Regras da interação

1. Para **cada tarefa do `TODO.md`**, formule **de 1 a no máximo 5 perguntas de avaliação** no total. O padrão recomendado é **3 a 5**, conforme a complexidade. Não faça cinco perguntas por arquivo, por subetapa ou por rodada.
2. **Faça uma pergunta de cada vez**, espere a resposta e adapte a próxima ao que já foi dito. **Nunca repita uma pergunta já respondida.** A pergunta seguinte pode aprofundar um ponto relevante, sem estourar o limite.
3. Apresente sempre o progresso: **`Auditoria — pergunta 1/4`**, **`2/4`** etc. Defina um total inicial razoável, até 5, podendo encerrar antecipadamente se houver informação suficiente; não acrescente perguntas depois de chegar ao total declarado.
4. Cada pergunta deve citar a **tarefa** e, quando útil, a **etapa concreta** (formulário, regra de negócio, integração, teste etc.). Pergunte sobre o que foi realmente implementado, não sobre componentes hipotéticos.
5. Priorize: **avaliação do resultado**, **problemas observados**, **adequação aos requisitos**, **possíveis melhorias** e **opinião final sobre a contribuição da IA**. Combine tópicos quando a tarefa for pequena.
6. O integrante pode responder **"não testei"**, **"não sei"** ou **"sem sugestões"**. Registre fielmente essa resposta; não converta ausência de problemas relatados em comprovação técnica de funcionamento.
7. Use **caixas de resposta curtas, formulários sequenciais ou controles equivalentes**, **somente se a ferramenta/agente oferecer essa possibilidade** e se realmente simplificarem o fluxo. Caso contrário, utilize mensagens de texto curtas, uma pergunta por vez, numeradas com o progresso. Não exija ferramenta de interface específica.
8. Não presuma respostas nem preencha avaliações em nome do integrante. Caso a conversa seja interrompida, salve um **rascunho parcial** com perguntas já respondidas, indique as pendências e retome do ponto correto, sem reiniciar toda a entrevista.
9. Se a resposta revelar um defeito, apresente a evidência disponível e registre-o. **Não corrija silenciosamente a implementação já avaliada**; combine a correção quando apropriado, registre o ajuste e, se necessário, peça uma confirmação **dentro das perguntas restantes**. Se não houver perguntas restantes, marque como "correção ainda não reavaliada".
10. As perguntas são **individuais por tarefa**. Não abra uma auditoria global da aplicação ou uma entrevista coletiva sobre o trabalho de todos.

### Exemplo adaptável — quatro perguntas para uma tarefa com duas etapas

> **Auditoria — pergunta 1/4 | Tarefa: Cadastrar endereço | Etapa: formulário**  
> O formulário gerado atendeu ao que você esperava? O que achou da organização e das validações?
>
> **Auditoria — pergunta 2/4 | Etapa: consulta de CEP**  
> Ao testar ou ler essa integração, percebeu algum problema ou comportamento inesperado?
>
> **Auditoria — pergunta 3/4 | Etapas implementadas**  
> O que você melhoraria ou faria de forma diferente em alguma dessas partes?
>
> **Auditoria — pergunta 4/4 | Síntese da tarefa**  
> Considerando o resultado e a revisão que você fez, qual é sua avaliação do auxílio da IA nessa tarefa?

Este exemplo **não é uma lista fixa**: adapte quantidade, ordem e redação aos passos reais da tarefa. O agente deve apresentar **uma pergunta por turno**, e não as quatro de uma só vez.

### Parecer por etapa

Para cada etapa efetivamente avaliada, registre uma das opções abaixo **com base no feedback e nas evidências**, não apenas na aparência do código:

- **Aprovada** — atende ao escopo verificado, sem ressalvas relevantes identificadas.
- **Aprovada com ressalvas** — atende ao principal, mas há ajustes ou verificações pendentes.
- **Necessita correções** — problema confirmado ou desvio relevante da tarefa.
- **Não avaliada / inconclusiva** — não houve teste, inspeção ou feedback suficiente.

Se o integrante não conseguir avaliar uma etapa, não atribua a ela um parecer positivo artificialmente. O parecer global deve respeitar a situação de cada etapa.

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
│       │   ├── nome-da-tarefa-auditoria.md
│       │   └── nome-da-tarefa-relatorio.docx
│       ├── davi/
│       ├── rafael/
│       ├── yuri/
│       └── pedro/
└── ...
```

- Use o identificador de semana **exatamente como consta no `TODO.md`**, se houver. Caso contrário, adote um identificador inequívoco de período e registre a origem.
- Use o **nome explícito do integrante** no cabeçalho e nos metadados do relatório, bem como nos caminhos de arquivo. Não use apelidos incertos.
- Se houver mais de uma tarefa do mesmo integrante na semana, produza **um relatório por tarefa** (nomes de arquivo distintos). Uma consolidação semanal é opcional e não substitui os relatórios individuais.
- Gere primeiro o arquivo `.md`, que é a referência editável da auditoria. **Quando a conversão estiver disponível**, exporte o mesmo conteúdo para `.docx`, com títulos, seções e tabela legíveis; se não estiver, informe a limitação e preserve o Markdown.
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
**O que foi verificado:** [inspeção/teste e evidências, se existirem]
**Avaliação do integrante:** [síntese fiel da resposta, sem inventar]
**Problemas identificados:** [problemas reais ou "nenhum relatado" / "não avaliado"]
**Sugestões de melhoria:** [observações do integrante; caso não haja, indicar]
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

### Regras de autoria e integridade

- **O integrante é o avaliador.** A IA pode organizar, revisar a escrita e consolidar respostas, mas não atribuir a ele experiências, opiniões ou ações inexistentes.
- A **conclusão é escrita em primeira pessoa**, refletindo a perspectiva humana, **sem citar o nome do integrante no corpo da conclusão**. O nome permanece explícito nos metadados e na identificação do responsável pela avaliação.
- Se a pessoa disser "achei bom, mas não testei", escreva exatamente essa distinção; não conclua que o código está comprovadamente correto.
- **Separar:** (a) solicitação original, (b) implementação gerada pela IA, (c) inspeções/testes objetivos, (d) opinião do integrante, (e) recomendações e pendências.
- Caso o agente faça uma avaliação técnica independente, identifique-a como **análise técnica da IA**; não a apresente como fala ou observação do integrante.
- Não inventar notas, percentuais de conformidade, aprovações do professor ou resultados de testes.
- Não registrar dados pessoais desnecessários, segredos ou credenciais em relatórios.

## 7. Como responder em uma nova sessão

Quando um integrante pedir ajuda para implementar ou auditar uma tarefa, o agente deve seguir esta ordem:

1. **Se necessário:** "Qual integrante está usando o agente: Breno, Davi, Rafael, Yuri ou Pedro?"
2. **Após ler `TODO.md`:** "Encontrei sua tarefa desta semana: [tarefa]. Vou trabalhar apenas nela, dividindo-a em [etapas]." Se o pedido já esclarecer integrante e tarefa, avance sem perguntar novamente.
3. **Após implementar e verificar:** apresente as etapas efetivamente realizadas, o resultado dos testes e as limitações de forma objetiva.
4. **Na auditoria:** faça **uma pergunta por vez** com indicador **`Auditoria — pergunta X/Y`**, máximo de cinco perguntas naquela tarefa.
5. **Ao final:** gere/atualize o relatório `.md`, exporte para `.docx` se possível, apresente arquivos e pendências; **nunca faça commit**.

> **Regra de ouro:** o agente implementa e ajuda a documentar; o integrante **avalia criticamente**; somente o integrante gerencia o Git e decide a entrega final.
