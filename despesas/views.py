from django.shortcuts import render, redirect
from django.http import HttpResponse
import pandas as pd
import json
from .models import Despesa, ArquivoResultado, Extra, ConfigProduto, ConfigOrigem
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required



@login_required(login_url='/login/')
def listar_despesas(request):
    despesas = Despesa.objects.all() 
    return render(request, 'lista_despesas.html', {'despesas': despesas})

@login_required(login_url='/login/')
def criar_despesa(request):
    if request.method == 'POST':
        data = request.POST.get('data')
        valor = request.POST.get('valor')
        origem = request.POST.get('origem')
        categoria = request.POST.get('categoria')
        subcategoria = request.POST.get('subcategoria')
        numero = request.POST.get('numero')
        info = request.POST.get('info')
        descricao = request.POST.get('descricao')
        
        Despesa.objects.create(
            data=data, valor=valor, origem=origem, categoria=categoria,
            subcategoria=subcategoria, numero=numero, info=info, descricao=descricao
        )
        # Pega o valor do botão que foi clicado
        acao = request.POST.get('acao')
        
        if acao == 'salvar_novo':
            # Se clicou no azul, recarrega a própria página de novo lançamento
            return redirect('criar_despesa')
        else:
            # Se clicou no verde (ou apertou Enter), volta para a página inicial
            return redirect('home')
    
   
    
    return render(request, 'novo_lancamento.html')

@login_required(login_url='/login/')
def excluir_despesa(request, id):
    despesa = Despesa.objects.get(id=id)
    despesa.delete()
    return redirect('home')

@login_required(login_url='/login/')
def editar_despesa(request, id):
    # 1. Vai no banco de dados e busca a despesa exata com aquele ID
    despesa = Despesa.objects.get(id=id)
    
    # 2. Se o usuário acabou de clicar no botão "Salvar Alterações" (POST)
    if request.method == 'POST':
        despesa.data = request.POST.get('data')
        despesa.valor = request.POST.get('valor')
        despesa.origem = request.POST.get('origem')
        despesa.categoria = request.POST.get('categoria')
        despesa.subcategoria = request.POST.get('subcategoria')
        despesa.numero = request.POST.get('numero')
        despesa.info = request.POST.get('info')
        despesa.descricao = request.POST.get('descricao')
        
        # Salva as alterações no banco de dados (UPDATE)
        despesa.save()
        
        # Volta para a lista
        return redirect('home')
    
    # 3. Se for apenas entrar na página (GET), manda o HTML com os dados dessa despesa
    return render(request, 'editar_lancamento.html', {'despesa': despesa})


def tela_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            # Se errar a senha, recarrega a página com erro
            return render(request, 'login.html', {'erro': 'Usuário ou senha incorretos!'})
    return render(request, 'login.html')

def deslogar(request):
    logout(request)
    return redirect('tela_login') 

@login_required(login_url='/login/')
def tela_exportar(request):
    return render(request, 'exportar_excel.html')

@login_required(login_url='/login/')
def exportar_excel(request):
    # 1. Puxa todos os dados do banco
    dados = Despesa.objects.all().values('data', 'origem', 'categoria', 'subcategoria', 'numero', 'valor', 'info', 'descricao')
    
    # 2. Transforma em uma tabela do Pandas
    df = pd.DataFrame(dados)
    
    # 3. Prepara a resposta do navegador como um arquivo de download
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="minhas_despesas.xlsx"'
    
    # 4. Salva o Pandas dentro do arquivo do navegador
    df.to_excel(response, index=False, engine='openpyxl')
    
    # 5. Entrega o arquivo
    return response

@login_required(login_url='/login/')
def resultado_page(request):
    arquivos_salvos = ArquivoResultado.objects.all().order_by('-data_upload')
    tabela_html = ""
    arquivo_selecionado = None
    abas_disponiveis = [] # Lista para guardar os nomes das abas
    aba_selecionada = None

    # 1. Se o usuário enviou um novo arquivo (POST)
    if request.method == 'POST' and 'arquivo_excel' in request.FILES:
        arquivo = request.FILES['arquivo_excel']
        
        # NOVO: Pega o texto digitado no campo de abas liberadas
        abas_escolhidas = request.POST.get('abas_liberadas', '')
        
        # Salva no banco junto com o arquivo
        ArquivoResultado.objects.create(nome=arquivo.name, arquivo=arquivo, abas_liberadas=abas_escolhidas)
        return redirect('resultado_page')

    # 2. Se o usuário clicou em um arquivo (GET com ?arquivo_id=X)
    arquivo_id = request.GET.get('arquivo_id')
    if arquivo_id:
        try:
            arquivo_obj = ArquivoResultado.objects.get(id=arquivo_id)
            arquivo_selecionado = arquivo_obj
            
            # MAGIA AQUI: Lê o Excel
            xls = pd.ExcelFile(arquivo_obj.arquivo.path)
            
            # NOVO: Em vez de xls.sheet_names, usamos a lista que você digitou, se existir.
            if arquivo_obj.abas_liberadas:
                # Pega o texto, corta nas vírgulas, tira os espaços nas pontas
                abas_disponiveis = [aba.strip() for aba in arquivo_obj.abas_liberadas.split(',') if aba.strip()]
            else:
                # Se você deixou em branco, ele mostra todas como precaução
                abas_disponiveis = xls.sheet_names



            # Verifica se o usuário clicou em alguma aba específica (?aba=NomeDaAba)
            aba_requisitada = request.GET.get('aba')
            
            # Se ele clicou numa aba, usa ela. Senão, usa a primeira aba como padrão.
            if aba_requisitada in abas_disponiveis:
                aba_selecionada = aba_requisitada
            else:
                aba_selecionada = abas_disponiveis[0]

            # Agora sim, ele lê os dados APENAS da aba selecionada
            df = pd.read_excel(arquivo_obj.arquivo.path, sheet_name=aba_selecionada)
            df = df.fillna('')
            tabela_html = df.to_html(classes='table table-bordered', index=False)
            
        except Exception as e:
            tabela_html = f"<p style='color:red;'>Erro ao ler o arquivo: {e}</p>"

    return render(request, 'resultado.html', {
        'arquivos_salvos': arquivos_salvos,
        'tabela_html': tabela_html,
        'arquivo_selecionado': arquivo_selecionado,
        'abas_disponiveis': abas_disponiveis,
        'aba_selecionada': aba_selecionada
    })

@login_required(login_url='/login/')
def listar_extras(request):
    extras = Extra.objects.all().order_by('-data')
    return render(request, 'lista_extras.html', {'extras': extras})

@login_required(login_url='/login/')
def novo_extra(request):
    produtos_json = "[]"
    origens_json = "[]"

    # Tenta ler o último Excel de Produtos enviado
    config_prod = ConfigProduto.objects.all().order_by('-id').first()
    if config_prod:
        try:
            df_prod = pd.read_excel(config_prod.arquivo.path)
            # Transforma em formato de chave-valor: {"Produto A": 10.5, "Produto B": 5.0}
            dict_produtos = dict(zip(df_prod.iloc[:, 0], df_prod.iloc[:, 1]))
            produtos_json = json.dumps(dict_produtos)
        except:
            pass

    # Tenta ler o último Excel de Origens enviado
    config_orig = ConfigOrigem.objects.all().order_by('-id').first()
    if config_orig:
        try:
            df_orig = pd.read_excel(config_orig.arquivo.path)
            origens_json = json.dumps(df_orig.iloc[:, 0].tolist())
        except:
            pass

    if request.method == 'POST':
        # 1. Pega os valores e garante que viram números (float)
        amount = float(request.POST.get('amount') or 0)
        unitary_value = float(request.POST.get('unitary_value') or 0)
        
        # 2. Faz a conta mágica
        total_calculado = amount * unitary_value

        # 3. Salva no banco de dados já com o total calculado
        Extra.objects.create(
            data=request.POST.get('data'),
            product=request.POST.get('product'),
            amount=amount,
            unitary_value=unitary_value,
            total=total_calculado,
            origin=request.POST.get('origin')
        )
        return redirect('listar_extras')

  
    return render(request, 'novo_extra.html', {'produtos_json': produtos_json, 'origens_json': origens_json})

@login_required(login_url='/login/')
def upload_config_extras(request):
    if request.method == 'POST':
        if 'arquivo_produtos' in request.FILES:
            ConfigProduto.objects.create(arquivo=request.FILES['arquivo_produtos'])
        if 'arquivo_origens' in request.FILES:
            ConfigOrigem.objects.create(arquivo=request.FILES['arquivo_origens'])
    return redirect('novo_extra')