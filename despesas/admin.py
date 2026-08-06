from django.contrib import admin
from .models import Despesa, ArquivoResultado

# Mostra a tabela de despesas no admin (bônus!)
admin.site.register(Despesa)

# Mostra os arquivos de resultado no admin
admin.site.register(ArquivoResultado)