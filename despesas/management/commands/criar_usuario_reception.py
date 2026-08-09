from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from despesas.models import Perfil

class Command(BaseCommand):
    help = 'Cria o usuário bandit com acesso a Extras'

    def handle(self, *args, **kwargs):
        User = get_user_model()
        
        # Cria o usuário (se já existir, não faz nada)
        user, created = User.objects.get_or_create(
            username='reception', 
            defaults={'is_staff': False, 'is_superuser': False}
        )
        
        if created:
            user.set_password('Madalena10')
            user.save()
            self.stdout.write(self.style.SUCCESS('Usuário bandit criado com sucesso!'))
        else:
            self.stdout.write(self.style.WARNING('Usuário bandit já existe.'))

        # Garante que ele tem o perfil de Extras
        perfil, _ = Perfil.objects.get_or_create(
            usuario=user, 
            defaults={'tipo': 'extras'}
        )
        self.stdout.write(self.style.SUCCESS('Perfil de Extras garantido!'))