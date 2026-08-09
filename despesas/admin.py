from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Despesa, ArquivoResultado, Extra, ConfigProduto, ConfigOrigem, Perfil

admin.site.register(Despesa)
admin.site.register(ArquivoResultado)
admin.site.register(Extra)
admin.site.register(ConfigProduto)
admin.site.register(ConfigOrigem)

class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False
    verbose_name_plural = 'Permissões de Acesso'

class CustomUserAdmin(UserAdmin):
    inlines = (PerfilInline, )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_tipo')
    def get_tipo(self, instance):
        return instance.perfil.get_tipo_display()
    get_tipo.short_description = 'Tipo de Acesso'

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)