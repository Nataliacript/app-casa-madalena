from django.db import models

class Despesa(models.Model):
    data = models.DateField()
    origem = models.CharField(max_length=100)
    categoria = models.CharField(max_length=100)
    subcategoria = models.CharField(max_length=100)
    numero = models.CharField(max_length=50, blank=False, null=False)
    valor = models.DecimalField(max_digits=10, decimal_places=2) # Ideal para dinheiro
    info = models.TextField(blank=False, null=False)
    descricao = models.TextField(blank=False, null=False)

    def __str__(self):
        return f"{self.categoria} - {self.valor}"


# MODELO PARA GUARDAR OS ARQUIVOS EXCEL

class ArquivoResultado(models.Model):
    nome = models.CharField(max_length=200) 
    arquivo = models.FileField(upload_to='resultados/') 
    data_upload = models.DateTimeField(auto_now_add=True) 
    
    # Vai guardar algo como "Resumo, Dados Gerais"
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

    def __str__(self):
        return f"{self.product} - {self.total}"


class ConfigProduto(models.Model):
    arquivo = models.FileField(upload_to='config_extras/')

class ConfigOrigem(models.Model):
    arquivo = models.FileField(upload_to='config_extras/')