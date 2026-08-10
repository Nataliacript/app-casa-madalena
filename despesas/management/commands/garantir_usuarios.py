from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from despesas.models import Perfil

class Command(BaseCommand):
    help = 'Garante que todos os usuários do sistema existem'

    def handle(self, *args, **kwargs):
        User = get_user_model()
        
        # A LISTA DE USUÁRIOS DO SISTEMA
        # Quando quiser um novo, é só adicionar uma linha aqui embaixo!
        usuarios = [
            {'username': 'admin', 'password': 'Flordodia10', 'tipo': 'admin', 'staff': True, 'superuser': True},
            {'username': 'reception', 'password': 'Madalena10', 'tipo': 'extras'},
            {'username': 'natalia', 'password': 'Render2024*', 'tipo': 'admin', 'staff': True, 'superuser': True},
            # {'username': 'joao', 'password': 'senha_segura', 'tipo': 'despesas'}, # Exemplo futuro
        ]

        for u in usuarios:
            # Tenta buscar o usuário. Se não existir, cria.
            user, criado = User.objects.get_or_create(
                username=u['username'],
                defaults={'is_staff': u.get('staff', False), 'is_superuser': u.get('superuser', False)}
            )
            
            if criado:
                user.set_password(u['password'])
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Usuário '{u['username']}' criado com sucesso!"))
            else:
                self.stdout.write(self.style.WARNING(f"Usuário '{u['username']}' já existe. Pulando..."))

            # Garante que o perfil de permissão existe
            Perfil.objects.get_or_create(
                usuario=user, 
                defaults={'tipo': u['tipo']}
            )