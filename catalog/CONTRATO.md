# Contrato do app `catalog` (T02 — Rafael)

Este documento descreve os models do catálogo para quem vai **usá-los** nesta entrega: Yuri (T03, vitrine/filtros), Pedro (T04, carrinho) e Davi (T05, templates). O código está em [`models.py`](models.py) e [`admin.py`](admin.py).

Referências: UC01, SRS v1.1 RF-CAT-01 a 09, RN-01 a RN-05, diagrama de tabelas.

## Models e campos

| Model | Campos | Relações / acessos |
|---|---|---|
| `Categoria` | `nome`, `descricao` (opcional), `pai` (pode ser nulo) | `categoria.subcategorias.all()`, `categoria.produtos.all()`. `str()` mostra o caminho: `Livros > Ficção`. |
| `Produto` | `nome`, `descricao` (até 500), `preco` (`Decimal`, 2 casas), `estoque` (inteiro ≥ 0), `categoria`, `tipo` (`Produto.Tipo.LIVRO` / `Produto.Tipo.ELETRONICO`) | `produto.livro` / `produto.eletronico`, `produto.especializacao()`, `produto.em_estoque` |
| `Livro(Produto)` | todos os de `Produto` + `isbn`, `numero_paginas`, `idioma`, `editora`, `autores` (M2M) | `Idioma.livros`, `Editora.livros`, `Autor.livros` |
| `Eletronico(Produto)` | todos os de `Produto` + `modelo`, `garantia_meses`, `fabricante` | `fabricante.eletronicos.all()` |
| `Idioma`, `Autor`, `Editora`, `Fabricante` | `nome` (+ `biografia` em Autor, `descricao` em Fabricante) | entidades de apoio |

- `Livro` e `Eletronico` usam **herança multi-tabela**: a PK de um Livro é a mesma do seu Produto. **O carrinho deve apontar para `catalog.Produto`** (`ForeignKey('catalog.Produto', ...)`), que vale para os dois tipos.
- `produto.especializacao()` devolve o objeto `Livro` ou `Eletronico` correspondente (ou `None` se, por inconsistência, não houver).
- `produto.em_estoque` é `estoque > 0`. Indica **só disponibilidade**. **Não** significa "ativo/publicado".
- Preço: use o `Decimal` diretamente, sem converter para `float`. Subtotal = `produto.preco * quantidade`.
- Ordenação padrão de `Produto`: `nome`, `id` (estável para paginação).

## Consultas recomendadas

```python
from django.db.models import Q

from catalog.models import Produto, Eletronico, Categoria, Fabricante

# Vitrine com os dados específicos já carregados
Produto.objects.select_related('categoria', 'livro', 'eletronico')

# Por tipo
Produto.objects.filter(tipo=Produto.Tipo.ELETRONICO)

# Por categoria e suas subcategorias diretas
Produto.objects.filter(Q(categoria=cat) | Q(categoria__pai=cat))

# Filtros do UC02
Produto.objects.filter(preco__gte=minimo, preco__lte=maximo)
Produto.objects.filter(eletronico__fabricante=fabricante)

# Fabricantes que têm eletrônicos com estoque (parte de estoque do RF-FLT-03)
Fabricante.objects.filter(eletronicos__estoque__gt=0).distinct()

# Categorias principais
Categoria.objects.filter(pai__isnull=True)
```

## Regras garantidas

| Regra | Onde é garantida |
|---|---|
| Preço **> R$ 0,00 e < R$ 10.000,00**, com até 2 casas (RN-02) | Validador do campo (formulários/`full_clean()`) **e** `CheckConstraint` no banco |
| Estoque ≥ 0 | `PositiveIntegerField` (formulário e banco) |
| Campos obrigatórios gerais e específicos (RF-CAT-02/04/05, RN-03 a RN-05) | Validação do model/Admin |
| Livro com ao menos um autor | **Só no formulário do Admin** (o banco não valida M2M) |
| Todo produto é Livro ou Eletrônico (RN-01) | **Na aplicação**: `Produto.save()` recusa criar um `Produto` genérico e impede alterar `tipo` ao atualizar pelo objeto pai. O Admin só cadastra pelas telas de Livro/Eletrônico. A `CheckConstraint` do banco restringe só o *valor* de `tipo`, não a existência da linha filha. Operações em massa como `QuerySet.update()` não passam por `save()`. |
| Categoria não pode ser pai de si mesma nem formar ciclo | `Categoria.clean()` |
| Categoria, Idioma, Editora e Fabricante em uso não podem ser excluídos | `on_delete=PROTECT` |

Atualizar um produto que já existe pelo objeto `Produto` (por exemplo, ajustar `estoque`) é permitido.

## Administração (Django Admin)

- Cadastro/edição/exclusão: **Catálogo → Livros** e **Catálogo → Eletrônicos**. O botão "+" ao lado de Idioma, Editora, Autores e Fabricante cadastra o item que faltar (UC01 A4).
- **Catálogo → Produtos** é só consulta (lista os dois tipos, com link para a tela do tipo).
- Só usuários `is_staff` acessam o Admin.

## Dados de demonstração

```bash
python manage.py migrate
python manage.py loaddata catalogo_demo
```

São 6 categorias (Livros > Ficção/Tecnologia; Eletrônicos > Celulares/Notebooks), 3 livros e 3 eletrônicos fictícios. Um livro tem **estoque 0** ("Web Basics"), para testar o estado indisponível.

**Atenção:** a fixture usa PKs fixas (1–6). Use-a só em um **banco local de demonstração**, de preferência recém-migrado. Recarregá-la **sobrescreve** registros com as mesmas PKs, inclusive alterações feitas no Admin.

## Pendências e divergências registradas

- **Campo "ativo" não existe.** RF-FLT-03/UC02 e UC03 falam em produtos/categorias "ativos", mas o diagrama de tabelas não tem esse atributo. **Decisão pendente** do grupo/Yuri. Um produto esgotado continua no catálogo e aparece como indisponível. Estoque não é critério de publicação.
- **Imagem do produto não modelada** (não está no diagrama de tabelas). O Davi usa placeholder; um `ImageField` exigiria a dependência Pillow.
- **ISBN:** unicidade e formato não são definidos pelos artefatos. Hoje é só texto obrigatório (até 30 caracteres).
- **Garantia:** aceita 0 meses. Os artefatos não definem um mínimo.
- **UC01 A5 × RN-02:** o fluxo A5 do UC01 sugere confirmar preços acima do limite, o que contradiz RN2/RN3 do próprio UC01 e a RN-02 do SRS. Foi aplicada a regra do SRS: **preços fora da faixa são rejeitados, sem confirmação**. A divergência precisa ser corrigida na documentação.
- Avaliações, inventário de vendedores e telas públicas não fazem parte da T02.
