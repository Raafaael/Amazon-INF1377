"""Cria um pedido a partir do carrinho, sem depender do checkout."""

from uuid import uuid4

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError

from orders.models import Pedido
from orders.services import criar_pedido


class Command(BaseCommand):
    help = 'Cria um pedido de demonstração a partir do carrinho existente do usuário.'

    def add_arguments(self, parser):
        parser.add_argument('usuario', help='Nome de usuário já cadastrado e com itens no carrinho.')
        parser.add_argument('--chave', help='Chave para reenvios da mesma intenção (padrão: pedido-demo-1).')
        parser.add_argument('--novo', action='store_true', help='Cria outra intenção de demonstração com uma chave nova.')

    def handle(self, *args, **options):
        usuario = get_user_model().objects.filter(username=options['usuario']).first()
        if usuario is None:
            raise CommandError('Usuário não encontrado.')
        if options['novo'] and options['chave']:
            raise CommandError('Use --novo ou --chave, não as duas opções juntas.')
        chave = (f'pedido-demo-{uuid4().hex}' if options['novo']
                 else options['chave'] or 'pedido-demo-1')
        existia = Pedido.objects.filter(usuario=usuario, chave_checkout=chave).exists()
        try:
            pedido = criar_pedido(usuario, chave)
        except ValidationError as erro:
            raise CommandError(' '.join(erro.messages)) from erro
        self.stdout.write(self.style.SUCCESS(
            f'Pedido #{pedido.pk} ({"já existente" if existia else "novo"}): '
            f'{pedido.get_status_display()} — R$ {pedido.total:.2f}. '
            'Veja /pedidos/ após entrar com esta conta.'
        ))
        if existia:
            self.stdout.write('Para criar outro pedido com os itens atuais do carrinho, use --novo.')
