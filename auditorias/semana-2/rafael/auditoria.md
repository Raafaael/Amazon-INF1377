# RELATÓRIO DE AUDITORIA DE DESENVOLVIMENTO ASSISTIDO POR IA

**Projeto:** Amazon — Sistema de Comércio Eletrônico  
**Integrante responsável:** Rafael  
**Semana/período:** Semana 2 — Checkout, pedidos, pagamentos e entrega (`TODO.md`)  
**Tarefa atribuída:** T07 — Endereços, endereço padrão e ViaCEP  
**Ferramenta de IA utilizada:** Claude Code (Claude Opus 5.5)  
**Data da auditoria:** 13/11/2026  
**Situação:** concluída — rodada inicial e Revisão 1 avaliadas; o acesso direto por URL de outro usuário e a seleção para o checkout continuam sem verificação humana

## 1. Introdução e contextualização

O projeto é um e-commerce acadêmico em Django. Na Semana 2, o grupo monta o fluxo de compra. A T07 entrega o cadastro de endereços do cliente, com endereço padrão e preenchimento pelo ViaCEP. Esses endereços serão usados pelo checkout (T10) e pelos pedidos (T06).

A IA planejou a tarefa, implementou e testou o código. O plano passou por revisões antes da implementação. Esta auditoria registra a verificação feita por Rafael no navegador e a compara com os testes automatizados.

## 2. Descrição da tarefa e implementação realizada

**Solicitação (`TODO.md`, T07).** A tarefa pede:
- o model `Endereco`;
- cadastro, listagem, edição e endereço padrão exclusivo;
- preenchimento pelo ViaCEP, com tratamento de CEP inválido, inexistente, resposta incompleta e falha do serviço;
- a página **Meus endereços** com máscara `00000-000`;
- validação do número obrigatório e isolamento entre usuários;
- seleção de endereço para o checkout;
- testes com ViaCEP simulado;
- documentação para pedido e checkout.

Referências: UC06, RN-09 a RN-11.

**Decisões de Rafael no planejamento:**
- tipo de endereço como opções Casa/Trabalho;
- quando o ViaCEP falha, preenchimento manual permitido;
- link "Meus endereços" no menu, condicionado a acerto com Davi.

**Implementação produzida pela IA:**

| Arquivo | O que contém |
|---|---|
| `addresses/models.py` | `Endereco`, com padrão único por usuário: `save()` desmarca os outros padrões e há uma constraint no banco |
| `addresses/cep.py` | normalização única do CEP |
| `addresses/viacep.py` | consulta com `urllib`, timeout e erros próprios |
| `addresses/forms.py` | cadastro e `SelecaoEnderecoForm` para o checkout |
| `addresses/views.py`, `addresses/urls.py` | lista, novo, editar, excluir, tornar padrão e o endpoint JSON de CEP |
| `templates/addresses/` | `lista.html`, `form.html` e `_selecao.html` |
| `addresses/static/addresses/enderecos.js` | máscara e preenchimento automático |
| `addresses/admin.py` | cadastro no Admin |
| `addresses/tests/` | 37 testes |
| `addresses/CONTRATO.md` | contrato para checkout e pedidos |
| `config/settings.py`, `config/urls.py` | uma linha cada |
| `templates/base.html` | link "Meus endereços" no menu, só para usuário logado; adicionado após a auditoria, a pedido de Rafael, sem acerto prévio com Davi registrado |

## 3. Auditoria da implementação

### 3.1. Consulta de CEP e preenchimento automático

**Critério esperado:** com um CEP válido, preencher logradouro, bairro, cidade e UF; aplicar a máscara `00000-000`; manter os campos editáveis.  
**O que foi verificado:** o integrante digitou `01001000` em `/enderecos/novo/`. A IA, separadamente, rodou testes com o ViaCEP simulado e uma consulta real (`01001-000` → Praça da Sé / Sé / São Paulo / SP).  
**Avaliação do integrante:** a máscara foi aplicada corretamente e os campos foram preenchidos, continuando editáveis. Considerou bom que número e complemento não sejam preenchidos, como esperado.  
**Problemas identificados:** nenhum relatado.  
**Sugestões de melhoria:** nenhuma.  
**Resultado:** aprovada.

### 3.2. CEP inexistente e cadastro manual

**Critério esperado:** mensagem clara para CEP não encontrado e possibilidade de preencher os campos à mão e salvar.  
**O que foi verificado:** o integrante digitou `99999999`, viu a mensagem e cadastrou o endereço à mão. A IA testou automaticamente as respostas 400, 404 e 503 e o salvamento manual depois de uma falha simulada do serviço.  
**Avaliação do integrante:** apareceu "CEP não encontrado. Verifique o número informado e tente novamente, ou preencha o endereço manualmente." Os campos do teste anterior continuaram preenchidos e sem alteração, o que considerou correto. O endereço preenchido à mão foi cadastrado e apareceu em "Meus endereços".  
**Problemas identificados:** **achado técnico da IA**: com os campos anteriores mantidos, era possível salvar o CEP `99999-999` junto com o logradouro de outro CEP.  
**Sugestões de melhoria:** o integrante sugeriu limpar os campos quando o CEP não for encontrado, se esse for o padrão de outros sites. A IA consultou o exemplo oficial do ViaCEP, que limpa os campos quando o CEP é inválido ou não encontrado.  
**Encaminhamento:** correção implementada. Os campos são limpos para CEP inválido ou não encontrado, e **não** são limpos quando o serviço está fora do ar. Na Revisão 1, o integrante retestou: "Quando o CEP é válido ele preenche os campos, se for inválido ele limpa tudo". A limpeza com o serviço fora do ar não foi testada manualmente.  
**Resultado:** problema apontado pela IA → correção aplicada → reteste do integrante: **aprovada**.

### 3.3. Endereço padrão

**Critério esperado:** no máximo um padrão por usuário; trocar o padrão desmarca o anterior; excluir o padrão informa o usuário.  
**O que foi verificado:** o integrante usou "Tornar padrão" e excluiu o endereço padrão. A IA testou a troca, a exclusividade (também no banco) e a exclusão.  
**Avaliação do integrante:** o selo passa para o endereço clicado e o padrão fica à frente (mais à esquerda). Sobre a mensagem de exclusão ("…Ele era o seu endereço padrão; escolha outro como padrão, se desejar."), não a achou tão boa para o usuário e estranhou o ";", embora fique claro que é possível escolher outro padrão.  
**Problemas identificados:** texto da mensagem pouco natural (achado do integrante).  
**Sugestões de melhoria:** mensagem sem ";", simples de entender de imediato.  
**Encaminhamento:** a primeira correção ("Endereço excluído. Agora você não tem um endereço padrão. Se quiser, escolha outro.") não chegou a ser vista pelo integrante, porque o servidor estava com `--noreload`. Ela foi substituída na Revisão 1 pela promoção automática de um novo padrão, com a mensagem "Endereço excluído. Seu endereço padrão agora é [logradouro], [número].". O integrante confirmou que a mensagem informou o novo padrão.  
**Resultado:** problema relatado → correção aplicada (Revisão 1) → reteste do integrante: **aprovada**.

### 3.4. Isolamento entre usuários

**Critério esperado:** nenhum usuário consulta, altera ou exclui endereços de outro.  
**O que foi verificado:** o integrante entrou com outro usuário e abriu "Meus endereços". A tentativa de acesso direto pela URL resultou em `ERR_NAME_NOT_RESOLVED`, um erro do navegador causado pela URL sem o servidor (`http://127.0.0.1:8000`), e não uma resposta da aplicação. A IA testou automaticamente que editar, excluir e tornar padrão o endereço de outro usuário retornam 404 sem alterar dados.  
**Avaliação do integrante:** na aba de endereços do outro usuário não aparece nenhum endereço cadastrado pelo primeiro.  
**Problemas identificados:** nenhum relatado. O bloqueio por URL direta **não foi verificado pelo integrante**; foi verificado apenas pelo teste automatizado.  
**Sugestões de melhoria:** nenhuma informada.  
**Resultado:** aprovada com ressalvas (acesso direto por URL não verificado manualmente).

### 3.5. Seleção para o checkout e contrato

**Critério esperado:** disponibilizar ao checkout a lista e a escolha de endereços do usuário e a ligação para cadastrar um novo endereço com retorno.  
**O que foi verificado:** apenas pela IA: testes do `SelecaoEnderecoForm`, do partial `_selecao.html` e do `next` seguro (inclusive após POST inválido e no Cancelar).  
**Avaliação do integrante:** não avaliada; não houve pergunta específica.  
**Problemas identificados:** não avaliado.  
**Sugestões de melhoria:** —  
**Resultado:** não avaliada / inconclusiva.

### Revisão 1 — 13/11/2026: padrão automático, link no menu e servidor desatualizado

**Pedido do integrante.** Depois da auditoria, Rafael relatou três pontos:
- o link "Meus endereços" não aparecia;
- a mensagem de exclusão ainda tinha ";";
- o primeiro endereço cadastrado já deveria ser o padrão.

**Diagnóstico (análise técnica da IA).** Os arquivos já continham o link e a mensagem nova. O servidor em uso na porta 8000 tinha sido iniciado com `runserver --noreload`, que não recarrega código nem templates. A orientação foi reiniciar o servidor sem essa opção. Os dois primeiros pontos **ainda não foram reavaliados** depois do reinício.

**Decisão do integrante.** Entre as opções apresentadas, escolheu "Primeiro + promover ao excluir".

**Implementação da IA:**
- `Endereco.save()` define como padrão o endereço cadastrado quando o usuário ainda não tem um padrão;
- `Endereco.delete()` promove o endereço restante mais recente quando o padrão é excluído;
- o Admin exclui um endereço por vez, para aplicar essa regra também lá;
- as mensagens passaram a ser:
  - "Endereço cadastrado com sucesso e definido como seu endereço padrão.";
  - "Endereço excluído. Seu endereço padrão agora é [logradouro], [número].".

Com isso, a mensagem sem ";" pedida na rodada inicial foi substituída por esta.

**Limitação registrada:** desmarcar "padrão" ao editar o endereço padrão deixa o usuário sem padrão.

**Testes da IA:** `python manage.py test` executou 116 testes, todos OK. Foram incluídos casos de primeiro cadastro, promoção ao excluir, exclusão de endereço não padrão e mensagens.

**Perguntas da rodada curta (2):** (1) link no menu e padrão automático; (2) limpeza dos campos com CEP não encontrado.  
**Avaliação do integrante:**
- Depois de reiniciar o servidor, o link "Meus endereços" apareceu.
- O primeiro endereço cadastrado virou padrão, com a mensagem de aviso.
- Ao excluir o padrão, o segundo endereço foi promovido, e a mensagem indicou qual era o novo padrão. Resposta: "tudo isso que você perguntou deu certo".
- Sobre o CEP: "Quando o CEP é válido ele preenche os campos, se for inválido ele limpa tudo".

**Problemas identificados:** nenhum relatado nesta rodada.  
**Resultado:** aprovada.

## 4. Síntese dos achados

| Etapa | Evidência/observação | Origem | Resultado | Pendência |
|---|---|---|---|---|
| Consulta de CEP | Máscara e preenchimento corretos no navegador | Integrante | Aprovada | — |
| CEP inexistente | Mensagem clara e cadastro manual salvo; os campos antigos permaneciam (achado da IA) e passaram a ser limpos, com reteste do integrante | Integrante + achado técnico da IA | Aprovada | — |
| Endereço padrão | Troca correta; mensagem de exclusão criticada e substituída pela promoção automática (Revisão 1), com reteste | Integrante | Aprovada | — |
| Revisão 1 (link e padrão automático) | Link visível após reiniciar o servidor; primeiro endereço padrão; promoção ao excluir | Integrante | Aprovada | Desmarcar "padrão" na edição deixa o usuário sem padrão (limitação registrada) |
| Isolamento | Listagem isolada verificada; URL direta só por teste automatizado | Integrante + IA | Aprovada com ressalvas | Testar a URL completa de outro usuário |
| Seleção/contrato | Só testes automatizados | IA | Inconclusiva | Validar na integração com o checkout |

Testes automatizados: `python manage.py test` executou 116 testes (43 do `addresses`), todos OK, depois da Revisão 1.

## 5. Recomendações

**Do integrante:**
- usar uma mensagem simples, sem ";", ao excluir o endereço padrão (substituída pela promoção automática; retestada);
- limpar os campos quando o CEP não for encontrado, se esse for o padrão (confirmado no exemplo oficial do ViaCEP; aplicada e retestada);
- tornar padrão o primeiro endereço e promover outro ao excluir o padrão (Revisão 1; aplicada e retestada).

**Sugestões técnicas adicionais da IA:**
- retestar acessando `http://127.0.0.1:8000/enderecos/<id>/editar/` com outro usuário (deve resultar em 404);
- avisar Davi sobre o link "Meus endereços" já adicionado ao `base.html` (arquivo compartilhado), para evitar link duplicado ou conflito de merge;
- executar o servidor de desenvolvimento sem `--noreload`, para que alterações de código e templates apareçam;
- decidir em grupo a regra de compra só digital (RN-11), a proteção de dados em repouso/HTTPS e a garantia de padrão único caso o banco mude para MySQL.

## 6. Conclusão e avaliação do uso da IA

No navegador, a máscara do CEP e o preenchimento automático funcionaram, com os campos continuando editáveis. Gostei de número e complemento ficarem em branco. Com um CEP inexistente, a mensagem apareceu e consegui cadastrar o endereço preenchendo os dados à mão. A troca do endereço padrão funcionou como eu esperava. Não achei boa a mensagem ao excluir o endereço padrão, por causa do ";", e pedi uma versão mais simples. Também sugeri limpar os campos quando o CEP não é encontrado, se esse fosse o padrão. Na conta de outro usuário, não apareceram os meus endereços.

Depois da auditoria, notei que o link "Meus endereços" e a mensagem nova não apareciam, e que o primeiro endereço deveria ser o padrão. Escolhi que o primeiro endereço vire padrão e que outro seja promovido quando o padrão for excluído. Depois de reiniciar o servidor, tudo o que testei deu certo: o link apareceu, o primeiro endereço virou padrão com aviso, a exclusão promoveu o outro endereço e informou qual era o novo padrão, e com CEP inválido os campos foram limpos. Não registrei uma avaliação geral sobre o auxílio da IA nesta tarefa, então esta conclusão se limita aos testes que fiz.

**Parecer final:** T07 aprovada nos fluxos verificados pelo integrante: consulta de CEP, cadastro manual, endereço padrão (inclusive automático), isolamento da listagem e link no menu. Não foram verificados manualmente o acesso direto por URL de outro usuário (coberto por teste automatizado) e a seleção para o checkout (a validar na integração com a T10).

---
**Responsável pela avaliação:** Rafael  
**Elaboração:** relatório estruturado com auxílio de IA a partir das evidências e respostas do integrante.
