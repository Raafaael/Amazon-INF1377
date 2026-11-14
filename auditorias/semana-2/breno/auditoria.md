# RELATÓRIO DE AUDITORIA DE DESENVOLVIMENTO ASSISTIDO POR IA

**Projeto:** Amazon — Sistema de Comércio Eletrônico  
**Integrante responsável:** Breno  
**Semana/período:** Semana 2 (prazo ainda a preencher no `TODO.md`)  
**Tarefa atribuída:** T06 — Pedidos e consulta do histórico de compras  
**Ferramenta de IA utilizada:** Codex  
**Data da auditoria:** 14/11/2026  
**Situação:** concluída — T06 aprovada com ressalvas; integração entre módulos pendente

## 1. Introdução e contextualização

Esta auditoria registra a implementação de T06 solicitada por Breno: criar e consultar pedidos simulados, seus itens, valores e histórico de status. Reúne testes técnicos da IA e as observações de Breno em duas rodadas de avaliação, incluindo três revisões solicitadas após os primeiros testes manuais.

## 2. Descrição da tarefa e implementação realizada

O `TODO.md` pede modelos de pedido/item/histórico, criação a partir do carrinho com validação e chave contra duplicação, preço congelado, serviço de status, páginas de lista/detalhe próprias, isolamento entre usuários, dados de demonstração e contratos para os demais integrantes.

A IA criou `orders/` (models, serviço, views, URLs, Admin, migração, testes, comando `criar_pedido_demo` e `CONTRATO.md`), `templates/orders/` e acrescentou as ligações mínimas em `config/settings.py`, `config/urls.py`, `templates/base.html` e `README.md`. Marcou os nove itens da T06 no `TODO.md` após verificar o comportamento técnico. A integração do checkout, pagamento e frete permanece sob as tarefas T08–T10.

**Verificação técnica da IA:** `python manage.py check` sem problemas; `python manage.py makemigrations --check --dry-run` sem alterações; `python manage.py migrate` aplicou `addresses.0001_initial` e `orders.0001_initial`; `python manage.py test` passou com 131 testes antes das revisões, e `python manage.py test orders` passou com 19 testes após as revisões. `git diff --check` não apontou problemas. Não foi feita avaliação visual no navegador pela IA.

## 3. Auditoria da implementação

### 3.1. Criação e reenvio do pedido de demonstração

**Critério esperado:** registrar pedido a partir de carrinho válido e não duplicá-lo ao reutilizar a mesma chave.  
**O que foi verificado:** testes automatizados da IA cobrem criação, carrinho vazio, estoque insuficiente, valores inválidos, execução repetida do comando e chave por usuário.  
**Avaliação do integrante:** Breno executou o roteiro e observou que o comando gera o pedido, que aparece em `/pedidos/` como “Aguardando pagamento”, enquanto o item continua no carrinho. Considerou pouco prático depender de um comando e gostaria de finalizar a compra pela interface e abrir “Meus pedidos”, mesmo num fluxo simples. Não informou explicitamente se repetiu o comando para conferir a ausência de duplicatas.  
**Problemas identificados:** a permanência do item no carrinho foi observada por Breno e confirmada pela leitura do serviço; é a decisão provisória documentada para pedido ainda não pago, não uma falha inesperada de execução. A ação “Finalizar compra” está desativada no template atual do carrinho.  
**Sugestões de melhoria:** disponibilizar um caminho de finalização na interface e definir quando limpar o carrinho; encaminhar a composição do checkout à T10 e a decisão de limpeza à integração com pagamento.  
**Resultado:** aprovada com ressalvas quanto à criação e consulta técnica; experiência de finalização ainda pendente.

### 3.2. Dados preservados e consulta própria

**Critério esperado:** preservar nome/preço/endereço/total da compra e exibir apenas pedidos próprios, mais recentes primeiro, com detalhes e histórico.  
**O que foi verificado:** testes automatizados da IA cobrem snapshots, soma com `Decimal`, ordem, estado vazio, login, 404 para pedido alheio e conteúdo do detalhe.  
**Avaliação do integrante:** Breno abriu “Ver detalhes”, achou a página resumida e clara, disse que os dados lhe pareceram corretos e gostou da implementação. Sugeriu exibir os itens e suas imagens também na listagem de pedidos, e tornar o nome de cada produto clicável para voltar ao catálogo enquanto estiver disponível.  
**Problemas identificados:** a listagem original não mostrava os itens; não houve relato de valores incorretos. O catálogo atual não armazena fotos nem dispõe de campo `ativo`; usa ícones ilustrativos e permite abrir o detalhe de produto sem estoque.  
**Sugestões de melhoria:** itens e imagens na listagem; link do nome para o produto. A revisão abaixo atende à listagem e ao link, usando a ilustração existente; fotos reais dependem do catálogo.  
**Resultado:** aprovada com ressalva de fotos reais ausentes no catálogo; revisão visual reavaliada positivamente em 3.4.

### 3.3. Transições e histórico

**Critério esperado:** registrar cada mudança permitida com data, impedir salto para entregue sem pagamento/envio e impedir atualização livre pelo cliente.  
**O que foi verificado:** testes automatizados da IA cobrem aprovação, recusa, sequência de entrega, cronologia, bloqueio de saltos e autorização administrativa. Não existe rota de mudança de status para clientes.  
**Avaliação do integrante:** Breno observou o estado inicial “Aguardando pagamento” na interface, mas não relatou teste manual das demais transições. Considera suficiente uma indicação textual clara para status de pagamento.  
**Problemas identificados:** nenhum confirmado nos testes automatizados; integração com pagamentos e entrega ainda não exercitada entre módulos nem avaliada manualmente por Breno.  
**Sugestões de melhoria:** não foram feitas sugestões sobre a lógica das transições; manter status de pagamento textual e claro na interface.  
**Resultado:** inconclusiva quanto à avaliação humana das transições; verificada tecnicamente por testes automatizados.

### 3.4. Revisão 1 — 14/11/2026 — itens e links nas páginas de pedidos

**Pedido específico:** após examinar os detalhes, Breno pediu os itens já na listagem, uma imagem para cada produto e o nome clicável para voltar à página do produto.  
**Implementação adicional da IA:** a listagem e o detalhe passaram a reutilizar `templates/orders/_item.html`, com nome histórico, quantidade/preço histórico, subtotal, ícone ilustrativo do tipo e link para `catalog:product_detail`. A consulta faz pré-carregamento de itens/produtos. Nenhum model do catálogo foi alterado.  
**Verificação técnica:** `python manage.py test orders` passou com 17 testes; novo teste cobre itens, ícone e link nas duas telas, inclusive produto sem estoque. `python manage.py check` e `git diff --check` passaram.  
**Limitação:** não há fotos reais ou indicador `ativo` no catálogo. O link aponta para o produto que ainda existe; ausência de estoque não bloqueia sua página.  
**Avaliação humana da revisão:** Breno atualizou as páginas, disse que a listagem ficou visualmente muito melhor e confirmou que o link abre a página do produto corretamente.  
**Resultado:** aprovada com ressalva de fotos reais não disponíveis no catálogo.

### 3.5. Revisão 2 — 14/11/2026 — novo pedido no comando de demonstração

**Problema relatado por Breno:** depois de usar `criar_pedido_demo` uma vez, tentou registrar outro pedido com item no carrinho e não conseguiu; o comando devolvia o primeiro pedido sem indicar claramente que a chave padrão `pedido-demo-1` já existia.  
**Causa confirmada pela IA:** o serviço é idempotente por `(usuário, chave_checkout)`, e o comando reutilizava sempre a mesma chave padrão. O serviço já permitia informar `--chave` diferente, mas a operação de nova intenção não estava evidente.  
**Correção implementada:** o comando agora informa “já existente” quando reutiliza a chave e oferece `--novo` para criar outra intenção com os itens atuais; `README.md` e `orders/CONTRATO.md` foram atualizados. A idempotência da chave padrão foi preservada.  
**Verificação técnica:** `python manage.py test orders` passou com 18 testes, incluindo criação de segundo pedido com `--novo`; `python manage.py check` e `git diff --check` passaram.  
**Avaliação humana da correção:** Breno informou que `--novo` funcionou pelo que pôde observar, mas ainda considera confuso depender de `criar_pedido_demo`. Não detalhou a contagem de pedidos após o comando.  
**Resultado:** aprovada com ressalvas quanto à clareza do fluxo de demonstração; não substitui checkout pela interface.

### 3.6. Revisão 3 — 14/11/2026 — itens no resumo do detalhe

**Problema relatado por Breno:** em “Ver detalhes”, o resumo trazia apenas “Itens” com um valor agregado; o rótulo sugeria uma lista de produtos e valores que não aparecia naquele quadro. A lista completa estava em outra seção da página.  
**Correção implementada:** o resumo agora repete de forma compacta o nome, a quantidade e o subtotal de cada produto, seguido de “Subtotal dos itens”, frete quando houver e total.  
**Verificação técnica:** `python manage.py test orders` passou com 19 testes, incluindo detalhe de pedido com dois produtos e conferência dos itens no resumo; `python manage.py check` e `git diff --check` passaram.  
**Avaliação humana da correção:** Breno abriu o detalhe atualizado e disse que o resumo ficou bem melhor, mais claro e bem implementado. Perguntou qual é a diferença entre subtotal e total; a IA esclareceu que subtotal soma os produtos e total adiciona o frete, sendo iguais quando o pedido de demonstração não informa frete.  
**Avaliação final do integrante sobre o subtotal:** após a explicação, Breno disse que faz sentido manter subtotal e total, pois o frete será integrado.  
**Resultado:** aprovada; subtotal mantido conforme preferência expressa.

## 4. Síntese dos achados

| Etapa | Evidência/origem | Resultado | Pendência |
|---|---|---|---|
| Criação e reenvio | Testes da IA; Breno observou pedido aguardando pagamento e item ainda no carrinho | Aprovada com ressalvas | Finalização pela interface e limpeza após pagamento |
| Dados e consulta | Testes da IA; Breno achou os detalhes claros e aprovou a listagem/links revisados | Aprovada com ressalvas | Fotos reais dependem do catálogo |
| Status e histórico | Testes de transições e autorização da IA; Breno viu o estado inicial | Inconclusiva na avaliação humana das transições | Integração T08/T09 |
| Revisão de interface | 17 testes de `orders` e reteste positivo de Breno | Aprovada com ressalvas | Fotos reais dependem do catálogo |
| Revisão do comando | 18 testes de `orders`; Breno disse que funcionou, mas ainda achou o comando confuso | Aprovada com ressalvas | Checkout pela interface em T10 |
| Revisão do resumo | 19 testes de `orders`; Breno considerou o quadro mais claro e optou por manter o subtotal | Aprovada | Conferir valores com frete após integração |

## 5. Recomendações

Na integração, Davi deve reutilizar a mesma chave de checkout em reenvios; Pedro deve chamar a transição de pagamento somente após resultado simulado; Yuri deve avançar entrega pela sequência documentada. O serviço não limpa carrinho nem baixa estoque: o grupo precisa combinar esse momento. O catálogo ainda não distingue e-books; não inferir automaticamente entrega física ou digital. Estas são recomendações técnicas da IA, não observações de Breno.

**Observações de Breno fora da implementação T06:** a ação “Finalizar compra” ainda desativada e o item que permanece no carrinho prejudicam a sensação de conclusão; ele propôs um fluxo simples pela interface. Também questionou o botão “Atualizar” do **carrinho** e prefere quantidade mínima 1, removendo a instrução “Zero remove o item”. A inspeção da IA confirmou que ambos estão em `templates/cart/detail.html`, não na página de pedidos. Esses ajustes pertencem ao carrinho/checkout e não foram feitos durante esta auditoria de T06. A permanência do carrinho até aprovação é uma sugestão registrada no `TODO.md` para evitar perda de itens em recusa ou PIX pendente; a decisão final exige integração.

**Sugestão de Breno para T06:** manter os detalhes claros e acrescentar itens, imagens e links para os produtos. A IA implementou a listagem de itens e os links com ilustrações existentes; Breno retestou e aprovou a melhoria visual e os links. Fotos reais e noção de produto `ativo` dependem de decisão/estrutura do catálogo.

**Achado adicional de Breno em T06:** a chave fixa do comando impedia criar um segundo pedido de demonstração pela mesma invocação. A IA tornou `--novo` uma opção explícita e esclareceu a mensagem de pedido já existente; Breno disse que a opção funcionou pelo que pôde observar, mas o comando continua confuso como forma de criar pedidos. A solução de interface pertence à T10.

**Achado de Breno no resumo:** o rótulo “Itens” acompanhava só um valor agregado, sem nomes e valores naquele quadro. A IA incluiu os itens; Breno retestou e disse que o resultado ficou mais claro e bem implementado. Ele perguntou por que subtotal e total aparecem juntos; após a explicação de que coincidem na demonstração sem frete, preferiu mantê-los para a integração futura do frete.

**Avaliação final de Breno:** considerou que a IA cumpriu a tarefa, de complexidade relativamente baixa, com clareza e precisão. Avaliou que a primeira versão carecia de referências visuais comuns a aplicações de comércio eletrônico, como ícones, imagens e links, e que a criação inicial pelo comando foi difícil de compreender. Destacou a importância de explicar os cálculos em “Meus pedidos” e “Detalhes”; para o status de pagamento, entende que texto claro basta. As revisões melhoraram a interface, mas fotos reais e checkout permanecem dependentes de outras partes do projeto.

## 6. Conclusão e avaliação do uso da IA

Considero que a IA realizou a T06 com clareza e precisão, de acordo com o que foi pedido para uma tarefa relativamente simples. Gostei dos detalhes e da melhora na listagem, nos links e no resumo. No início, achei confuso criar pedidos pelo comando de demonstração; a opção para um novo pedido funcionou pelo que observei, mas ainda prefiro uma finalização pela interface. Senti falta, na primeira versão, de uma visualização mais intuitiva, com ícones, imagens e links, como em outras aplicações de comércio eletrônico. A revisão visual melhorou bastante. Para os cálculos, considero importante mostrar claramente cada item, o subtotal e o total; manteria o subtotal porque o frete será integrado. Para o status de pagamento, um texto claro é suficiente. No geral, considero boa a aplicação da IA nesta tarefa, com essas ressalvas visuais e de usabilidade.

**Parecer final:** T06 aprovada com ressalvas de apresentação e usabilidade; transições além do estado inicial ainda não foram avaliadas manualmente, e a integração com checkout, pagamento, frete e fotos reais depende de outros módulos.

---
**Responsável pela avaliação:** Breno  
**Elaboração:** relatório estruturado com auxílio de IA a partir das evidências e respostas do integrante.
