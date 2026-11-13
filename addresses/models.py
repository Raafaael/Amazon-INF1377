"""Endereços do cliente (T07).

Referências: UC06, RN-09 (um endereço padrão por cliente), RN-10 (número
obrigatório, complemento opcional); diagrama de tabelas (Endereco).
Consulte addresses/CONTRATO.md para o uso pelo checkout e pelos pedidos.
"""

from django.conf import settings
from django.db import models, transaction
from django.db.models import Q

from .cep import normalizar_cep, validar_cep


class Endereco(models.Model):
    class Tipo(models.TextChoices):
        # Enum TipoEndereço do diagrama UML.
        CASA = 'CASA', 'Casa'
        TRABALHO = 'TRABALHO', 'Trabalho'

    class UF(models.TextChoices):
        AC = 'AC', 'Acre'
        AL = 'AL', 'Alagoas'
        AP = 'AP', 'Amapá'
        AM = 'AM', 'Amazonas'
        BA = 'BA', 'Bahia'
        CE = 'CE', 'Ceará'
        DF = 'DF', 'Distrito Federal'
        ES = 'ES', 'Espírito Santo'
        GO = 'GO', 'Goiás'
        MA = 'MA', 'Maranhão'
        MT = 'MT', 'Mato Grosso'
        MS = 'MS', 'Mato Grosso do Sul'
        MG = 'MG', 'Minas Gerais'
        PA = 'PA', 'Pará'
        PB = 'PB', 'Paraíba'
        PR = 'PR', 'Paraná'
        PE = 'PE', 'Pernambuco'
        PI = 'PI', 'Piauí'
        RJ = 'RJ', 'Rio de Janeiro'
        RN = 'RN', 'Rio Grande do Norte'
        RS = 'RS', 'Rio Grande do Sul'
        RO = 'RO', 'Rondônia'
        RR = 'RR', 'Roraima'
        SC = 'SC', 'Santa Catarina'
        SP = 'SP', 'São Paulo'
        SE = 'SE', 'Sergipe'
        TO = 'TO', 'Tocantins'

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='usuário',
        on_delete=models.CASCADE,
        related_name='enderecos',
    )
    cep = models.CharField('CEP', max_length=9, validators=[validar_cep])
    logradouro = models.CharField('logradouro', max_length=100)
    numero = models.CharField('número', max_length=20)
    complemento = models.CharField('complemento', max_length=50, blank=True)
    bairro = models.CharField('bairro', max_length=50)
    cidade = models.CharField('cidade', max_length=50)
    estado = models.CharField('estado (UF)', max_length=2, choices=UF.choices)
    tipo = models.CharField('tipo de endereço', max_length=10, choices=Tipo.choices)
    padrao = models.BooleanField('endereço padrão', default=False)
    criado_em = models.DateTimeField('criado em', auto_now_add=True)
    atualizado_em = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'endereço'
        verbose_name_plural = 'endereços'
        ordering = ['-padrao', '-criado_em', '-id']
        constraints = [
            # RN-09. Funciona no SQLite (e PostgreSQL); o MySQL não suporta
            # índice condicional e o Django ignora esta constraint nele. Nesse
            # caso vale só a garantia da aplicação, em save().
            models.UniqueConstraint(
                fields=['usuario'],
                condition=Q(padrao=True),
                name='addresses_um_padrao_por_usuario',
                violation_error_message='Já existe um endereço padrão para este usuário.',
            ),
        ]

    def __str__(self):
        return self.texto_formatado

    def save(self, *args, **kwargs):
        # save() não chama full_clean(): normaliza (e rejeita) o CEP aqui também.
        self.cep = normalizar_cep(self.cep)
        with transaction.atomic():
            if (
                self._state.adding
                and not self.padrao
                and not Endereco.objects.filter(usuario_id=self.usuario_id, padrao=True).exists()
            ):
                # Decisão de Rafael: quem ainda não tem padrão (ex.: primeiro
                # endereço) recebe este endereço como padrão automaticamente.
                self.padrao = True
            if self.padrao:
                # Garante no máximo um padrão por usuário (UC06 A1).
                (Endereco.objects
                 .filter(usuario_id=self.usuario_id, padrao=True)
                 .exclude(pk=self.pk)
                 .update(padrao=False))
            super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Exclui; se era o padrão, promove o endereço restante mais recente.

        O endereço promovido (ou None) fica em `self.novo_padrao`.
        Observação: exclusões em massa por queryset não passam por aqui.
        """
        with transaction.atomic():
            era_padrao = self.padrao
            usuario_id = self.usuario_id
            resultado = super().delete(*args, **kwargs)
            self.novo_padrao = None
            if era_padrao:
                substituto = (Endereco.objects
                              .filter(usuario_id=usuario_id)
                              .order_by('-criado_em', '-id')
                              .first())
                if substituto:
                    substituto.definir_como_padrao()
                    self.novo_padrao = substituto
        return resultado

    def definir_como_padrao(self):
        self.padrao = True
        self.save(update_fields=['padrao', 'atualizado_em'])

    @property
    def texto_formatado(self):
        partes = [f'{self.logradouro}, {self.numero}']
        if self.complemento:
            partes.append(self.complemento)
        return (
            f'{" - ".join(partes)} — {self.bairro}, {self.cidade}/{self.estado} '
            f'— CEP {self.cep}'
        )

    def dados_para_pedido(self):
        """Cópia dos dados para o pedido gravar no momento da compra.

        O pedido deve copiar estes valores; assim, editar ou excluir o
        endereço depois não altera o pedido histórico.
        """
        return {
            'cep': self.cep,
            'logradouro': self.logradouro,
            'numero': self.numero,
            'complemento': self.complemento,
            'bairro': self.bairro,
            'cidade': self.cidade,
            'estado': self.estado,
            'tipo': self.tipo,
        }

    @classmethod
    def do_usuario(cls, usuario):
        """Endereços do usuário, com o padrão primeiro."""
        return cls.objects.filter(usuario=usuario)

    @classmethod
    def padrao_do_usuario(cls, usuario):
        """Endereço padrão do usuário, ou None."""
        return cls.objects.filter(usuario=usuario, padrao=True).first()

    @classmethod
    def obter_do_usuario(cls, usuario, endereco_id):
        """Busca segura por id: levanta Endereco.DoesNotExist se não for do usuário."""
        return cls.objects.get(usuario=usuario, pk=endereco_id)
