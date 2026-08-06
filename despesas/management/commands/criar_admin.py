from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Cria um usuário admin automaticamente se não existir'

    def handle(self, *args, **kwargs):
        User = get_user_model()
        username = 'admin'
        password = '123456' # Coloque a senha que você quiser aqui

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, password=password)
            self.stdout.write(self.style.SUCCESS(f'Usuário "{username}" criado com sucesso!'))
        else:
            self.stdout.write(self.style.WARNING(f'Usuário "{username}" já existe. Nenhuma ação necessária.'))