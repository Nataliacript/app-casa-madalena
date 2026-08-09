from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Despesa, ArquivoResultado, Extra, ConfigProduto, ConfigOrigem, Perfil

# 1. Registra seus modelos normais
admin.site.register(Despesa)
admin.site.register(ArquivoResultado)
admin.site.register(Extra)
admin.site.register(ConfigProduto)
admin.site.register(ConfigOrigem)

# 2. Cria a "Caixinha" do Perfil para colocar dentro da tela do Usuário
class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False
    verbose_name_plural = 'Permissões de Acesso'

# 3. Personaliza a tela de Usuário do Django para incluir nossa caixinha
class CustomUserAdmin(UserAdmin):
    inlines = (PerfilInline, )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_tipo')
    
    # Adiciona a coluna na listagem de usuários para você ver o tipo de cara lá de cima
    def get_tipo(self, instance):
        return instance.perfil.get_tipo_display()
    get_tipo.short_description = 'Tipo de Acesso'

# 4. "Desregistra" o User antigo do Django e "Registra" o nosso novo
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)