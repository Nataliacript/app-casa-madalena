from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Despesa(models.Model):
    data = models.DateField()
    origem = models.CharField(max_length=100)
    # Categoria e Subcategoria no modelo principal tornam-se opcionais para retrocompatibilidade
    categoria = models.CharField(max_length=100, blank=True, null=True)
    subcategoria = models.CharField(max_length=100, blank=True, null=True)
    numero = models.CharField(max_length=50, blank=False, null=False)
    valor = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) # Valor total consolidado
    supplier = models.CharField(max_length=200, blank=True, null=True) # Novo campo Fornecedor
    info = models.TextField(blank=True, null=True)
    descricao = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.data} - {self.supplier or self.origem} - $ {self.valor}"


class ItemDespesa(models.Model):
    """Modelo relacional para os subitens/linhas da despesa"""
    despesa = models.ForeignKey(Despesa, on_delete=models.CASCADE, related_name='itens')
    categoria = models.CharField(max_length=100)
    subcategoria = models.CharField(max_length=100)
    quantidade = models.FloatField(default=1.0)
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.categoria} / {self.subcategoria} - $ {self.subtotal}"


# MODELO PARA GUARDAR OS ARQUIVOS EXCEL

class ArquivoResultado(models.Model):
    nome = models.CharField(max_length=200) 
    arquivo = models.FileField(upload_to='resultados/') 
    data_upload = models.DateTimeField(auto_now_add=True) 
    
    # Guarda nomes das abas separados por vírgula ("Resumo, Dados Gerais")
    abas_liberadas = models.TextField(blank=True, null=True, help_text="Nomes das abas separados por vírgula")

    def __str__(self):
        return self.nome


class Extra(models.Model):
    data = models.DateField()
    product = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    unitary_value = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    origin = models.CharField(max_length=100)
    description = models.TextField(blank=False, null=False)

    def __str__(self):
        return f"{self.product} - {self.total}"


class ConfigProduto(models.Model):
    arquivo = models.FileField(upload_to='config_extras/')

class ConfigOrigem(models.Model):
    arquivo = models.FileField(upload_to='config_extras/')


class Perfil(models.Model):
    OPCOES_DE_PERFIL = (
        ('admin', 'Administrador'),
        ('despesas', 'Financeiro (Despesas)'),
        ('extras', 'Operacional (Apenas Extras)'),
    )
    
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=15, choices=OPCOES_DE_PERFIL, default='despesas')

    def __str__(self):
        return f"{self.usuario.username} - {self.get_tipo_display()}"


class MoneyBoxExpense(models.Model):
    data = models.DateField()
    origem = models.CharField(max_length=100)
    # Categoria e Subcategoria no modelo principal tornam-se opcionais para retrocompatibilidade
    categoria = models.CharField(max_length=100, blank=True, null=True)
    subcategoria = models.CharField(max_length=100, blank=True, null=True)
    numero = models.CharField(max_length=50, blank=False, null=False)
    valor = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) # Valor total consolidado
    supplier = models.CharField(max_length=200, blank=True, null=True) # Novo campo Fornecedor
    info = models.TextField(blank=True, null=True)
    descricao = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.data} - {self.supplier or self.origem} - $ {self.valor}"


class ItemMoneyBoxExpense(models.Model):
    """Modelo relacional para os subitens/linhas da despesa"""
    despesa = models.ForeignKey(MoneyBoxExpense, on_delete=models.CASCADE, related_name='itens')
    categoria = models.CharField(max_length=100)
    subcategoria = models.CharField(max_length=100)
    quantidade = models.FloatField(default=1.0)
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.categoria} / {self.subcategoria} - $ {self.subtotal}"




class FamilyFriend(models.Model):
    name = models.CharField(max_length=200)
    bed_number = models.CharField(max_length=20, null=True, blank=True)
    payment_date = models.DateField()
    check_in = models.DateField()
    check_out = models.DateField()
    amount_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    nights = models.IntegerField()
    adults = models.IntegerField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} - Quarto {self.bed_number}"