# Ajuste posterior à auditoria da T02 — imutabilidade do tipo

**Integrante:** Rafael  
**Tarefa:** T02 — Modelos e cadastro de produtos  
**Relação com a auditoria:** complemento ao `T02-auditoria.md`; as respostas e o parecer originais não foram alterados.

Após a auditoria, a análise técnica da IA identificou que `Produto.save()` impedia criar um produto genérico, mas ainda permitia alterar `tipo` ao atualizar um objeto `Produto` já existente. Isso poderia deixar `tipo=ELETRONICO` em um registro cujo filho continuasse sendo `Livro`.

**Ajuste realizado:** `Produto.save()` agora rejeita a troca de `tipo` ao atualizar pelo objeto pai. A edição de outros campos, como `estoque`, continua permitida. Foi criado um teste para a tentativa de troca e o contrato do catálogo foi atualizado. A proteção é da aplicação; `QuerySet.update()` e carregamento bruto de fixtures não passam por `save()`.

**Verificação técnica da IA:** `python manage.py test catalog.tests.test_models.TipoEConsistenciaTests` aprovou 7 testes; `python manage.py test` aprovou 36 testes. `python manage.py check` não apontou problemas e `python manage.py makemigrations --check --dry-run` não detectou mudanças pendentes. A Home respondeu HTTP 200. Nenhum teste manual do Admin foi realizado para este ajuste, pois a mudança é no model.

**Avaliação humana do ajuste:** ainda não realizada. **Situação:** correção implementada e verificada por testes automatizados; ainda não reavaliada pelo integrante.
