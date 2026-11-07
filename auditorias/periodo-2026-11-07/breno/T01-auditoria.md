# RELATÓRIO DE AUDITORIA DE DESENVOLVIMENTO ASSISTIDO POR IA

**Projeto:** Amazon — Sistema de Comércio Eletrônico  
**Integrante responsável:** Breno  
**Semana/período:** entrega semanal “Catálogo e Carrinho”, planejamento inicial de 07/11/2026 (`TODO.md`; não há número de semana definido)  
**Tarefa atribuída:** T01 — Inicializar o projeto Django: estrutura mínima e instruções de execução  
**Ferramenta de IA utilizada:** Codex  
**Data da auditoria:** 07/11/2026  
**Situação:** concluída — ajuste final ainda não reavaliado

## 1. Introdução e contextualização

Esta auditoria trata somente da base local do projeto Django produzida com auxílio de IA na T01. Seu objetivo é reunir a avaliação crítica de Breno sobre a implementação e confrontá-la com verificações técnicas observáveis. As quatro respostas da entrevista foram registradas.

## 2. Descrição da tarefa e implementação realizada

O `TODO.md` pede um projeto Django instalável e acessível no navegador, com `.venv`, dependências, apps vazios `catalog` e `cart`, Home provisória, Admin, login, diretórios de templates e arquivos estáticos, `.gitignore`, README e execução de `check`, `migrate` e `runserver`. O critério é permitir que outro integrante siga o README e abra `/` e `/admin/` antes das funcionalidades de catálogo e carrinho.

A IA criou `manage.py`, `config/`, `catalog/`, `cart/`, templates provisórios e `static/`; configurou URLs, autenticação padrão, SQLite local e `requirements.txt`; atualizou `README.md` e preservou as regras anteriores de `.gitignore`, acrescentando exclusão para `.env.*`. O ambiente `.venv` e o banco local foram criados e estão ignorados pelo Git. A IA não criou usuário administrador, pois `createsuperuser` requer credenciais escolhidas pelo integrante; posteriormente, Breno relatou acesso à Administração do Django.

## 3. Auditoria da implementação

### 3.1. Ambiente e documentação

**O que foi verificado:** análise técnica da IA: `.venv` criado; Django 5.2.19 instalado; README contém comandos de instalação e execução para Windows e Linux/macOS.  
**Avaliação do integrante:** as instruções ficaram claras, mas faltou orientar concretamente a criação de um superusuário comum e fácil para demonstração. Na avaliação final, explicou que as informações sobre `/admin/` e `/accounts/login/` pareciam pertencer apenas à seção Linux/macOS.  
**Problemas identificados:** explicação do superusuário pouco destacada e orientação de acesso posicionada de forma ambígua no README.  
**Sugestões de melhoria:** explicar a criação do superusuário e separar as orientações de acesso das seções de cada sistema operacional. A IA criou a seção comum “Criar o administrador e acessar a aplicação”, com exemplo de usuário `admin`, e-mail opcional e senha definida localmente. Essa correção final ainda não foi reavaliada pelo integrante.  
**Resultado:** aprovada com ressalvas; correção documental ainda não reavaliada.

### 3.2. Estrutura e rotas provisórias

**O que foi verificado:** análise técnica da IA: `python manage.py check` sem avisos; `python manage.py migrate` aplicou migrações padrão; `runserver --noreload 127.0.0.1:8000` respondeu por HTTP em `/` (200), `/admin/` (redirecionamento 302 para login do Admin), `/accounts/login/` (200) e `/carrinho/` (200).  
**Avaliação do integrante:** observou que a página inicial exibe “O catálogo será implementado na próxima etapa” e considerou que isso está dentro do esperado. Depois esclareceu que abriu `/admin/` e acessou a Administração do Django; abriu `/accounts/login/`, informou usuário e senha e chegou à página inicial. Relatou que está funcionando.  
**Problemas identificados:** nenhum problema relatado nas páginas e no fluxo de login que testou manualmente.  
**Sugestões de melhoria:** nenhuma informada para esta etapa.  
**Resultado:** aprovada para a Home provisória e para o acesso às rotas Admin e login, conforme os testes técnicos e o relato manual do integrante.

## 4. Síntese dos achados

| Etapa | Evidência/observação | Resultado | Pendência |
|---|---|---|---|
| Ambiente e README | Breno considerou as instruções claras, mas apontou falta de orientação destacada e comum aos sistemas para superusuário e rotas; IA reorganizou o README | Aprovada com ressalvas | Correção final ainda não reavaliada |
| Estrutura e rotas | IA executou `check`, `migrate`, servidor e requisições HTTP; Breno considerou a Home adequada e relatou acesso manual ao Admin e login | Aprovada | Nenhuma relatada para as rotas testadas |

## 5. Recomendações

**Observação de Breno:** explicar a criação de um superusuário simples para demonstração e posicionar Admin/login em seção aplicável a todos os sistemas operacionais. **Ajuste da IA:** o README agora reúne essas instruções em seção própria, sugere `admin` como usuário e orienta a definir a senha durante o comando. A correção final ainda não foi reavaliada. **Análise técnica da IA:** seguir o README em outro ambiente para verificar a reprodução da instalação. O banco MySQL continua pendente de decisão do grupo.

## 6. Conclusão e avaliação do uso da IA

Considerei as instruções claras e a mensagem provisória da Home adequada a esta etapa. Acessei a Administração do Django em `/admin/` e usei `/accounts/login/` para entrar e chegar à página inicial; esses acessos funcionaram para mim. Minha única sugestão de melhoria foi explicar melhor a criação do superusuário e separar a orientação das seções específicas de Windows e Linux/macOS, pois inicialmente entendi que as rotas eram próprias do sistema operacional. A IA reorganizou o README, mas não reavaliei essa versão final. Não expressei uma opinião separada sobre a contribuição geral da IA além dessas observações.

**Parecer final:** T01 funcional nos acessos verificados, com ressalva documental corrigida pela IA e ainda não reavaliada por Breno.

---
**Responsável pela avaliação:** Breno  
**Elaboração:** relatório estruturado com auxílio de IA a partir das evidências e respostas do integrante.
