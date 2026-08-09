from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from despesas.models import Perfil

class Command(BaseCommand):
    help = 'Cria um usuário admin e GARANTE que o perfil existe'

    def handle(self, *args, **kwargs):
        User = get_user_model()
        username = 'natalia'
        password = 'App2024*' # Ou a senha que você colocou lá

        # Tenta buscar o usuário. Se não existir, cria.
        user, created = User.objects.get_or_create(
            username=username, 
            defaults={'is_staff': True, 'is_superuser': True}
        )
        
        if created:
            user.set_password(password)
            user.save()

        # A MAGICA ESTÁ AQUI: Força a criação do Perfil, mesmo que o usuário já exista!
        Perfil.objects.get_or_create(
            usuario=user, 
            defaults={'tipo': 'admin'}
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Usuário "{username}" criado com sucesso!'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Perfil do usuário "{username}" garantido com sucesso!'))