from django.shortcuts import render, redirect
from django.http import HttpResponse
import pandas as pd
import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
import openpyxl
from openpyxl.utils import get_column_letter
from datetime import datetime, date
from .models import Despesa, ItemDespesa, MoneyBoxExpense, ItemMoneyBoxExpense, ArquivoResultado, Extra, ConfigProduto, ConfigOrigem, MoneyBoxExpense, FamilyFriend 
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db import transaction


@login_required(login_url='/login/')
def listar_despesas(request):
    # NOVA REGRA DO PORTEIRO DO DINHEIRO: Só natalia e admin podem ver as despesas originais.
    if request.user.username not in ['admin', 'natalia']:
        return redirect('listar_extras')
        
    # O prefetch_related carrega os itens vinculados em uma única consulta, otimizando a listagem
    despesas = Despesa.objects.all().prefetch_related('itens').order_by('-data')
    total_geral = despesas.aggregate(total=Sum('valor'))['total'] or 0
    return render(request, 'lista_despesas.html', {'despesas': despesas, 'total_geral': total_geral})


@login_required(login_url='/login/')
def criar_despesa(request):
    if request.method == 'POST':
        data = request.POST.get('data')
        origem = request.POST.get('origem')
        numero = request.POST.get('numero')
        info = request.POST.get('info')
        descricao = request.POST.get('descricao')
        supplier = request.POST.get('supplier')  # Novo campo

        # Listas de dados capturadas do formulário dinâmico
        categorias = request.POST.getlist('categoria[]')
        subcategorias = request.POST.getlist('subcategoria[]')
        quantidades = request.POST.getlist('quantidade[]')
        valores_unitarios = request.POST.getlist('valor_unitario[]')

        # Transação atômica: se houver falha na gravação de algum item, nada é salvo no banco
        with transaction.atomic():
            # Cria a despesa principal zerada primeiro para vincular os itens
            despesa = Despesa.objects.create(
                data=data,
                origem=origem,
                numero=numero,
                info=info,
                descricao=descricao,
                supplier=supplier,
                valor=0
            )

            total_despesa = 0
            
            # Loop para registrar cada subitem vindo do formulário
            for i in range(len(categorias)):
                cat = categorias[i]
                subcat = subcategorias[i]
                qtd = float(quantidades[i]) if quantidades[i] else 1.0
                v_unit = float(valores_unitarios[i]) if valores_unitarios[i] else 0.0
                
                subtotal = qtd * v_unit
                total_despesa += subtotal

                ItemDespesa.objects.create(
                    despesa=despesa,
                    categoria=cat,
                    subcategoria=subcat,
                    quantidade=qtd,
                    valor_unitario=v_unit,
                    subtotal=subtotal
                )

            # Atualiza o valor total consolidado na despesa pai
            despesa.valor = total_despesa
            # Define categoria/subcategoria do cabeçalho com base no primeiro item para compatibilidade
            if categorias:
                despesa.categoria = categorias[0]
                despesa.subcategoria = subcategorias[0]
            despesa.save()

        acao = request.POST.get('acao')
        if acao == 'salvar_novo':
            return redirect('criar_despesa')
        else:
            return redirect('home')
    
    return render(request, 'novo_lancamento.html')


@login_required(login_url='/login/')
def excluir_despesa(request, id):
    despesa = get_object_or_404(Despesa, id=id)
    despesa.delete()
    return redirect('home')


@login_required(login_url='/login/')
def editar_despesa(request, id):
    despesa = get_object_or_404(Despesa, id=id)

    if request.method == 'POST':
        data = request.POST.get('data')
        origem = request.POST.get('origem')
        numero = request.POST.get('numero')
        info = request.POST.get('info')
        descricao = request.POST.get('descricao')
        supplier = request.POST.get('supplier')

        categorias = request.POST.getlist('categoria[]')
        subcategorias = request.POST.getlist('subcategoria[]')
        quantidades = request.POST.getlist('quantidade[]')
        valores_unitarios = request.POST.getlist('valor_unitario[]')

        with transaction.atomic():
            despesa.data = data
            despesa.origem = origem
            despesa.numero = numero
            despesa.info = info
            despesa.descricao = descricao
            despesa.supplier = supplier

            # Deleta os subitens antigos para recriar os atualizados
            despesa.itens.all().delete()

            total_despesa = 0

            for i in range(len(categorias)):
                cat = categorias[i]
                subcat = subcategorias[i]
                qtd = float(quantidades[i]) if quantidades[i] else 1.0
                v_unit = (
                    float(valores_unitarios[i]) if valores_unitarios[i] else 0.0
                )

                subtotal = qtd * v_unit
                total_despesa += subtotal

                ItemDespesa.objects.create(
                    despesa=despesa,
                    categoria=cat,
                    subcategoria=subcat,
                    quantidade=qtd,
                    valor_unitario=v_unit,
                    subtotal=subtotal,
                )

            despesa.valor = total_despesa
            if categorias:
                despesa.categoria = categorias[0]
                despesa.subcategoria = subcategorias[0]
            despesa.save()

        return redirect('home')

    # --- REQUISIÇÃO GET (Carregamento da página) ---
    itens_queryset = despesa.itens.all()
    itens_lista = []

    if itens_queryset.exists():
        for item in itens_queryset:
            itens_lista.append(
                {
                    'categoria': item.categoria or '',
                    'subcategoria': item.subcategoria or '',
                    'quantidade': float(item.quantidade or 1),
                    'valor_unitario': float(item.valor_unitario or 0.0),
                }
            )
    else:
        # Se for um registro antigo do banco sem subitens
        itens_lista.append(
            {
                'categoria': despesa.categoria or '',
                'subcategoria': despesa.subcategoria or '',
                'quantidade': 1.0,
                'valor_unitario': float(despesa.valor or 0.0),
            }
        )

    # Converte explicitamente a lista serializada em string JSON
    itens_json_str = json.dumps(itens_lista)

    return render(
        request,
        'editar_lancamento.html',
        {
            'despesa': despesa,
            'itens_json': itens_json_str,
        },
    )


def tela_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            
            # NOVO: Redireciona automaticamente se for de Extras
            if user.perfil.tipo == 'extras':
                return redirect('listar_extras')
            return redirect('home')
        else:
            return render(request, 'login.html', {'erro': 'Usuário ou senha incorretos!'})
    return render(request, 'login.html')

def deslogar(request):
    logout(request)
    return redirect('tela_login') 

@login_required(login_url='/login/')
def exportar_excel(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Despesas Detalhadas"

    # Cabeçalho do arquivo Excel
    ws.append(
        [
            "ID Despesa",
            "Data",
            "Origem",
            "Fornecedor",
            "Nº Nota",
            "Mês/Ano Ref",
            "Categoria",
            "Subcategoria",
            "Qtd",
            "Valor Unitário",
            "Subtotal Item",
            "Descrição/Obs",
        ]
    )

    # Busca todas as despesas trazendo os itens pré-carregados da tabela relacionada
    despesas = (
        Despesa.objects.all().prefetch_related("itens").order_by("-data")
    )

    for despesa in despesas:
        # Acessa a lista de objetos do relacionamento 'itens'
        itens_relacionados = despesa.itens.all()

        if itens_relacionados.exists():
            for item in itens_relacionados:
                # Conversão de tipos para evitar erros entre float e Decimal
                qtd = float(item.quantidade or 0)
                valor_unitario = float(item.valor_unitario or 0)

                # Se o objeto item tiver o campo 'subtotal', usa ele; caso contrário calcula
                if hasattr(item, "subtotal") and item.subtotal is not None:
                    subtotal = float(item.subtotal)
                else:
                    subtotal = qtd * valor_unitario

                ws.append(
                    [
                        despesa.id,
                        (
                            despesa.data.strftime("%d/%m/%Y")
                            if despesa.data
                            else ""
                        ),
                        despesa.origem or "",
                        despesa.supplier or "",
                        despesa.numero or "",
                        despesa.info or "",
                        getattr(item, "categoria", ""),
                        getattr(item, "subcategoria", ""),
                        qtd,
                        valor_unitario,
                        subtotal,
                        despesa.descricao or "",
                    ]
                )
        else:
            # Caso a despesa não possua subitens cadastrados
            valor_total = float(getattr(despesa, "valor_total_geral", 0) or 0)
            ws.append(
                [
                    despesa.id,
                    despesa.data.strftime("%d/%m/%Y") if despesa.data else "",
                    despesa.origem or "",
                    despesa.supplier or "",
                    despesa.numero or "",
                    despesa.info or "",
                    "-",
                    "-",
                    1,
                    valor_total,
                    valor_total,
                    despesa.descricao or "",
                ]
            )

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = (
        'attachment; filename="relatorio_despesas_detalhado.xlsx"'
    )
    wb.save(response)

    return response

@login_required(login_url='/login/')
def resultado_page(request):
    arquivos_salvos = ArquivoResultado.objects.all().order_by('-data_upload')
    tabela_html = ""
    arquivo_selecionado = None
    abas_disponiveis = []
    aba_selecionada = None

    if request.method == 'POST' and 'arquivo_excel' in request.FILES:
        arquivo = request.FILES['arquivo_excel']
        abas_escolhidas = request.POST.get('abas_liberadas', '')
        arquivo.seek(0)
        conteudo_bytes = arquivo.read()
        novo_arquivo = ArquivoResultado(
            nome=arquivo.name,
            arquivo=arquivo,
            abas_liberadas=abas_escolhidas,
            conteudo_binario=conteudo_bytes
        )
        novo_arquivo.save()

        return redirect('resultado_page')

    arquivo_id = request.GET.get('arquivo_id')
    if arquivo_id:
        try:
            arquivo_obj = ArquivoResultado.objects.get(id=arquivo_id)
            arquivo_selecionado = arquivo_obj

            file_stream = arquivo_obj.get_file_stream()

            if not file_stream:
                # Se for um registro antigo sem conteúdo binario
                tabela_html = "<p style='color:red;'>Este arquivo antigo foi apagado pelo servidor. Por favor, reenvie a planilha.</p>"
            else:
   
                wb = openpyxl.load_workbook(file_stream, data_only=True)
            
                if arquivo_obj.abas_liberadas:
                    abas_disponiveis = [aba.strip() for aba in arquivo_obj.abas_liberadas.split(',') if aba.strip()]
                else:
                    abas_disponiveis = wb.sheetnames

                aba_requisitada = request.GET.get('aba')
            
                if aba_requisitada in abas_disponiveis:
                    aba_selecionada = aba_requisitada
                elif abas_disponiveis:
                    aba_selecionada = abas_disponiveis[0]

                if aba_selecionada and aba_selecionada in wb.sheetnames:
                    ws = wb[aba_selecionada]

                    
                # Função auxiliar para descobrir a cor real (o Excel é confuso com cores)
                def pegar_cor(cor_obj):
                    if not cor_obj or cor_obj.type == 'indexed': return None
                    if cor_obj.rgb == '00000000': return None
                    rgb = str(cor_obj.rgb)
                    if len(rgb) == 8 and rgb.startswith('00'): return f"#{rgb[2:]}"
                    return f"#{rgb}"

                        # NOVO: A lista NEGRA. O que estiver aqui, NÃO vira dinheiro. O resto, vira!
                # Adicione mais palavras aqui se precisar ignorar mais colunas
                palavras_que_NAOviram_dinheiro = [
                    'quantidade', 'qtd', 'mês', 'mes', 'month', 'dia', 'day', 
                    'id', 'código', 'codigo', 'code', 'número', 'numero', 'year', 'ano',
                    'unidade', 'item', 'status', 'pago', 'categoria', 'subcategoria','Nights'
                ]
                
                # Pega os cabeçalhos da primeira linha para saber o nome das colunas
                cabecalhos = []
                for cell in ws[1]:
                    cabecalhos.append(str(cell.value).lower() if cell.value else "")

                # Começa a construir a tabela HTML com estilos
                html_builder = ['<table style="border-collapse: collapse; font-family: Calibri, sans-serif;">']
                
                for linha_idx, row in enumerate(ws.iter_rows()):
                    html_builder.append('<tr>')
                    
                    for coluna_idx, cell in enumerate(row):
                        estilos_css = "border: 1px solid #d4d4d4; padding: 5px 10px;"
                        valor = cell.value if cell.value is not None else ""

                        # NOVO: Se o Excel identificou como Data, formata para Mês/Ano
                        if isinstance(valor, (datetime, date)):
                            valor = valor.strftime('%m/%Y')
                        
                        # Verifica se é exatamente uma string vazia (""). 
                        if valor == "":
                            estilos_css = "border: none; padding: 0;"
                        
                        # 1. Fundo (Background)
                        if cell.fill and cell.fill.fgColor:
                            cor_fundo = pegar_cor(cell.fill.fgColor)
                            if cor_fundo:
                                estilos_css += f"background-color: {cor_fundo};"
                        
                        # 2. Fonte (Cor, Tamanho, Negrito)
                        if cell.font:
                            if cell.font.color:
                                cor_letra = pegar_cor(cell.font.color)
                                if cor_letra:
                                    estilos_css += f"color: {cor_letra};"
                            if cell.font.size:
                                try:
                                    tamanho = cell.font.size.pt
                                except AttributeError:
                                    tamanho = float(cell.font.size)
                                tamanho_px = int(tamanho * 1.33)
                                estilos_css += f"font-size: {tamanho_px}px;"
                            if cell.font.bold:
                                estilos_css += "font-weight: bold;"

                        # 3. A LÓGICA INTELIGENTE (Dinheiro, Porcentagem, Vizinho ou Normal)
                        if isinstance(valor, (int, float)):
                            nome_da_coluna = cabecalhos[coluna_idx] if coluna_idx < len(cabecalhos) else ""
                            nao_e_dinheiro = False
                            
                            # REGRA A: É PORCENTAGEM nativa do Excel?
                            if cell.number_format and '%' in str(cell.number_format):
                                valor = f"{valor * 100:.2f}%"
                                nao_e_dinheiro = True
                            
                            # NOVA REGRA B: A célula AO LADO esquerda diz "Beds"?
                            elif coluna_idx > 0:
                                celula_esquerda = row[coluna_idx - 1]
                                if celula_esquerda.value:
                                    # Converte TUDO para texto minúsculo e tira espaços nas pontas
                                    texto_vizinho = str(celula_esquerda.value).lower().strip()
                                    
                                    if 'beds' in texto_vizinho:
                                        valor = f"{valor:.0f}"
                                        nao_e_dinheiro = True
                                        
                            # REGRA C: Está na lista negra pelo cabeçalho da coluna?
                            elif any(palavra in nome_da_coluna for palavra in palavras_que_NAOviram_dinheiro):
                                valor = f"{valor:.2f}"
                                nao_e_dinheiro = True
                                
                            # REGRA D: Se não caiu em nenhuma regra acima, vira Dinheiro!
                            if not nao_e_dinheiro:
                                valor = f"${valor:,.2f}"        
                        
                        html_builder.append(f'<td style="{estilos_css}">{valor}</td>')
                    html_builder.append('</tr>')
                
                html_builder.append('</table>')
                tabela_html = "".join(html_builder)    
            
        except Exception as e:
            tabela_html = f"<p style='color:red;'>Erro ao processar o estilo da planilha: {e}</p>"

    return render(request, 'resultado.html', {
        'arquivos_salvos': arquivos_salvos,
        'tabela_html': tabela_html,
        'arquivo_selecionado': arquivo_selecionado,
        'abas_disponiveis': abas_disponiveis,
        'aba_selecionada': aba_selecionada
    })

@login_required(login_url='/login/')
def listar_extras(request):
    # PORTEIRO: Se for usuário comum de despesas, não deixa ver os extras
    if request.user.perfil.tipo not in ['admin', 'extras']:
        return redirect('home')
        
    # Se ele for admin ou de extras, continua e mostra a página
    extras = Extra.objects.all().order_by('-data')
    return render(request, 'lista_extras.html', {'extras': extras})

@login_required(login_url='/login/')
def novo_extra(request):
    # PORTEIRO: Se for usuário comum de despesas, não deixa ver os extras
    if request.user.perfil.tipo not in ['admin', 'extras']:
        return redirect('home')

    
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
            origin=request.POST.get('origin'),
            description=request.POST.get('description')
        )
        return redirect('listar_extras')

  
    return render(request, 'novo_extra.html', {'produtos_json': produtos_json, 'origens_json': origens_json})

def upload_config_extras(request):
    if request.method == 'POST':
        if 'arquivo_produtos' in request.FILES:
            ConfigProduto.objects.create(arquivo=request.FILES['arquivo_produtos'])
        if 'arquivo_origens' in request.FILES:
            ConfigOrigem.objects.create(arquivo=request.FILES['arquivo_origens'])
    
    # Redireciona para onde o usuário estava
    tela_origem = request.POST.get('tela_origem')
    
    if tela_origem == 'family':
        return redirect('criar_family') 
    else:
        return redirect('novo_extra')


def excluir_resultado(request, id):
    # Vai no banco de dados e busca o arquivo
    arquivo = ArquivoResultado.objects.get(id=id)
    
    # O Django deleta o arquivo físico da pasta media/ E o registro do banco ao mesmo tempo!
    arquivo.delete()
    
    # Volta para a página de resultados
    return redirect('resultado_page')


@login_required(login_url='/login/')
def excluir_extra(request, id):
    if request.user.perfil.tipo not in ['admin', 'extras']:
        return redirect('listar_extras')
    
    extra = Extra.objects.get(id=id)
    extra.delete()
    return redirect('listar_extras')

@login_required(login_url='/login/')
def editar_extra(request, id):
    if request.user.perfil.tipo not in ['admin', 'extras']:
        return redirect('listar_extras')
        
    extra = Extra.objects.get(id=id)
    produtos_json = "[]"
    origens_json = "[]"

    # Tenta ler o último Excel de Produtos (igual fazemos no novo)
    config_prod = ConfigProduto.objects.all().order_by('-id').first()
    if config_prod:
        try:
            df_prod = pd.read_excel(config_prod.arquivo.path)
            dict_produtos = dict(zip(df_prod.iloc[:, 0], df_prod.iloc[:, 1]))
            produtos_json = json.dumps(dict_produtos)
        except: pass

    # Tenta ler o último Excel de Origens
    config_orig = ConfigOrigem.objects.all().order_by('-id').first()
    if config_orig:
        try:
            df_orig = pd.read_excel(config_orig.arquivo.path)
            origens_json = json.dumps(df_orig.iloc[:, 0].tolist())
        except: pass

    if request.method == 'POST':
        amount = float(request.POST.get('amount') or 0)
        unitary_value = float(request.POST.get('unitary_value') or 0)
        total_calculado = amount * unitary_value

        # Atualiza os dados do objeto existente
        extra.data = request.POST.get('data')
        extra.product = request.POST.get('product')
        extra.amount = amount
        extra.unitary_value = unitary_value
        extra.total = total_calculado
        extra.origin = request.POST.get('origin')
        extra.description = request.POST.get('description')
        extra.save()
        return redirect('listar_extras')

    return render(request, 'editar_extra.html', {
        'extra': extra,
        'produtos_json': produtos_json, 
        'origens_json': origens_json
    })


@login_required(login_url='/login/')
def listar_money_box(request):
          
    # O prefetch_related carrega os itens vinculados em uma única consulta, otimizando a listagem
    despesas = MoneyBoxExpense.objects.all().prefetch_related('itens').order_by('-data')
    total_geral = despesas.aggregate(total=Sum('valor'))['total'] or 0
    return render(request, 'lista_despesas_reception.html', {'MoneyBoxExpenses': despesas, 'total_geral': total_geral})



@login_required(login_url='/login/')
def criar_despesa_money_box(request):
    if request.method == 'POST':
        data = request.POST.get('data')
        origem = request.POST.get('origem')
        numero = request.POST.get('numero')
        info = request.POST.get('info')
        descricao = request.POST.get('descricao')
        supplier = request.POST.get('supplier')  # Novo campo

        # Listas de dados capturadas do formulário dinâmico
        categorias = request.POST.getlist('categoria[]')
        subcategorias = request.POST.getlist('subcategoria[]')
        quantidades = request.POST.getlist('quantidade[]')
        valores_unitarios = request.POST.getlist('valor_unitario[]')

        # Transação atômica: se houver falha na gravação de algum item, nada é salvo no banco
        with transaction.atomic():
            # Cria a despesa principal zerada primeiro para vincular os itens
            despesa = MoneyBoxExpense.objects.create(
                data=data,
                origem=origem,
                numero=numero,
                info=info,
                descricao=descricao,
                supplier=supplier,
                valor=0
            )

            total_despesa = 0
            
            # Loop para registrar cada subitem vindo do formulário
            for i in range(len(categorias)):
                cat = categorias[i]
                subcat = subcategorias[i]
                qtd = float(quantidades[i]) if quantidades[i] else 1.0
                v_unit = float(valores_unitarios[i]) if valores_unitarios[i] else 0.0
                
                subtotal = qtd * v_unit
                total_despesa += subtotal

                ItemMoneyBoxExpense.objects.create(
                    despesa=despesa,
                    categoria=cat,
                    subcategoria=subcat,
                    quantidade=qtd,
                    valor_unitario=v_unit,
                    subtotal=subtotal
                )

            # Atualiza o valor total consolidado na despesa pai
            despesa.valor = total_despesa
            # Define categoria/subcategoria do cabeçalho com base no primeiro item para compatibilidade
            if categorias:
                despesa.categoria = categorias[0]
                despesa.subcategoria = subcategorias[0]
            despesa.save()

        acao = request.POST.get('acao')
        if acao == 'salvar_novo':
            return redirect('novo_money_box')
        else:
            return redirect('listar_money_box')
    
    return render(request, 'novo_lancamento_reception.html')


@login_required(login_url='/login/')
def excluir_despesa_money_box(request, id):
    despesa = get_object_or_404(MoneyBoxExpense, id=id)
    despesa.delete()
    return redirect('listar_money_box')


@login_required(login_url='/login/')
def editar_despesa_money_box(request, id):
    despesa = get_object_or_404(MoneyBoxExpense, id=id)

    if request.method == 'POST':
        data = request.POST.get('data')
        origem = request.POST.get('origem')
        numero = request.POST.get('numero')
        info = request.POST.get('info')
        descricao = request.POST.get('descricao')
        supplier = request.POST.get('supplier')

        categorias = request.POST.getlist('categoria[]')
        subcategorias = request.POST.getlist('subcategoria[]')
        quantidades = request.POST.getlist('quantidade[]')
        valores_unitarios = request.POST.getlist('valor_unitario[]')

        with transaction.atomic():
            despesa.data = data
            despesa.origem = origem
            despesa.numero = numero
            despesa.info = info
            despesa.descricao = descricao
            despesa.supplier = supplier

            # Deleta os subitens antigos para recriar os atualizados
            despesa.itens.all().delete()

            total_despesa = 0

            for i in range(len(categorias)):
                cat = categorias[i]
                subcat = subcategorias[i]
                qtd = float(quantidades[i]) if quantidades[i] else 1.0
                v_unit = (
                    float(valores_unitarios[i]) if valores_unitarios[i] else 0.0
                )

                subtotal = qtd * v_unit
                total_despesa += subtotal

                ItemMoneyBoxExpense.objects.create(
                    despesa=despesa,
                    categoria=cat,
                    subcategoria=subcat,
                    quantidade=qtd,
                    valor_unitario=v_unit,
                    subtotal=subtotal,
                )

            despesa.valor = total_despesa
            if categorias:
                despesa.categoria = categorias[0]
                despesa.subcategoria = subcategorias[0]
            despesa.save()

        return redirect('listar_money_box')

    # --- REQUISIÇÃO GET (Carregamento da página) ---
    itens_queryset = despesa.itens.all()
    itens_lista = []

    if itens_queryset.exists():
        for item in itens_queryset:
            itens_lista.append(
                {
                    'categoria': item.categoria or '',
                    'subcategoria': item.subcategoria or '',
                    'quantidade': float(item.quantidade or 1),
                    'valor_unitario': float(item.valor_unitario or 0.0),
                }
            )
    else:
        # Se for um registro antigo do banco sem subitens
        itens_lista.append(
            {
                'categoria': despesa.categoria or '',
                'subcategoria': despesa.subcategoria or '',
                'quantidade': 1.0,
                'valor_unitario': float(despesa.valor or 0.0),
            }
        )

    # Converte explicitamente a lista serializada em string JSON
    itens_json_str = json.dumps(itens_lista)

    return render(
        request,
        'editar_lancamento_reception.html',
        {
            'despesa': despesa,
            'itens_json': itens_json_str,
        },
    )

@login_required(login_url='/login/')
def exportar_excel_money_box(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Money Box Detalhado"

    # Cabeçalho do arquivo Excel
    ws.append(
        [
            "ID Despesa",
            "Data",
            "Origem",
            "Fornecedor",
            "Nº Nota",
            "Mês/Ano Ref",
            "Categoria",
            "Subcategoria",
            "Qtd",
            "Valor Unitário",
            "Subtotal Item",
            "Descrição/Obs",
        ]
    )

    # 1. Troca do Model Despesa por MoneyBoxExpense
    despesas = (
        MoneyBoxExpense.objects.all().prefetch_related("itens").order_by("-data")
    )

    for despesa in despesas:
        # Acessa os subitens da tabela ItemMoneyBoxExpense
        itens_relacionados = despesa.itens.all()

        if itens_relacionados.exists():
            for item in itens_relacionados:
                # Conversão de tipos para evitar erros entre float e Decimal
                qtd = float(item.quantidade or 0)
                valor_unitario = float(item.valor_unitario or 0)

                # Se o objeto item tiver o campo 'subtotal', usa ele; caso contrário calcula
                if hasattr(item, "subtotal") and item.subtotal is not None:
                    subtotal = float(item.subtotal)
                else:
                    subtotal = qtd * valor_unitario

                ws.append(
                    [
                        despesa.id,
                        (
                            despesa.data.strftime("%d/%m/%Y")
                            if despesa.data
                            else ""
                        ),
                        despesa.origem or "",
                        despesa.supplier or "",
                        despesa.numero or "",
                        despesa.info or "",
                        getattr(item, "categoria", ""),
                        getattr(item, "subcategoria", ""),
                        qtd,
                        valor_unitario,
                        subtotal,
                        despesa.descricao or "",
                    ]
                )
        else:
            # Caso o registro não possua subitens cadastrados
            valor_total = float(getattr(despesa, "valor", 0) or 0)
            ws.append(
                [
                    despesa.id,
                    despesa.data.strftime("%d/%m/%Y") if despesa.data else "",
                    despesa.origem or "",
                    despesa.supplier or "",
                    despesa.numero or "",
                    despesa.info or "",
                    "-",
                    "-",
                    1,
                    valor_total,
                    valor_total,
                    despesa.descricao or "",
                ]
            )

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    # Altera o nome do arquivo gerado
    response["Content-Disposition"] = (
        'attachment; filename="relatorio_money_box_detalhado.xlsx"'
    )
    wb.save(response)

    return response





# NOVA VIEW: Todos acessam o Family & Friends
@login_required(login_url='/login/')
def listar_family(request):
    familia = FamilyFriend.objects.all().order_by('-payment_date')
    return render(request, 'lista_family.html', {'familia': familia})


@login_required(login_url='/login/')
def criar_family(request):
    origens_json = "[]"

    config_orig = ConfigOrigem.objects.all().order_by('-id').first()
    if config_orig:
        try:
            df_orig = pd.read_excel(config_orig.arquivo.path)
            origens_json = json.dumps(df_orig.iloc[:, 0].tolist())
        except:
            pass

    if request.method == 'POST':
        amount = float(request.POST.get('amount_per_night') or 0)
        nights = float(request.POST.get('nights') or 0)
        adults = float(request.POST.get('adults') or 0)
        
        total_calculado = amount * nights * adults

        # A TRADUÇÃO DAS DATAS: De DD/MM/AAAA para AAAA-MM-DD
        data_pagamento = datetime.strptime(request.POST.get('payment_date'), '%d/%m/%Y').date()
        data_checkin = datetime.strptime(request.POST.get('check_in'), '%d/%m/%Y').date()
        data_checkout = datetime.strptime(request.POST.get('check_out'), '%d/%m/%Y').date()

        FamilyFriend.objects.create(
            name=request.POST.get('name'),
            bed_number=request.POST.get('bed_number'),
            payment_date=data_pagamento, # Agora no formato correto!
            check_in=data_checkin,           # Agora no formato correto!
            check_out=data_checkout,       # Agora no formato correto!
            amount_per_night=amount,
            nights=int(request.POST.get('nights')),
            adults=int(request.POST.get('adults')),
            total=total_calculado,
            payment_method=request.POST.get('payment_method')
        )
        return redirect('listar_family')

    return render(request, 'novo_guest.html', {'origens_json': origens_json})

@login_required(login_url='/login/')
def excluir_family(request, id):
    guest = FamilyFriend.objects.get(id=id)
    guest.delete()
    return redirect('listar_family')

@login_required(login_url='/login/')
def editar_family(request, id):
    guest = FamilyFriend.objects.get(id=id)
    
    # NOVO: Buscar as formas de pagamento do Excel, igual fazemos na criação
    origens_do_excel = []
    config_orig = ConfigOrigem.objects.all().order_by('-id').first()
    if config_orig:
        try:
            df_orig = pd.read_excel(config_orig.arquivo.path)
            origens_do_excel = df_orig.iloc[:, 0].tolist()
        except:
            pass

    if request.method == 'POST':
        amount = float(request.POST.get('amount_per_night') or 0)
        nights = float(request.POST.get('nights') or 0)
        adults = float(request.POST.get('adults') or 0)
        
        # Tradução das datas (DD/MM/YYYY para AAAA-MM-DD)
        data_pagamento = datetime.strptime(request.POST.get('payment_date'), '%d/%m/%Y').date()
        data_checkin = datetime.strptime(request.POST.get('check_in'), '%d/%m/%Y').date()
        data_checkout = datetime.strptime(request.POST.get('check_out'), '%d/%m/%Y').date()

        guest.name = request.POST.get('name')
        guest.bed_number = request.POST.get('bed_number')
        guest.payment_date = data_pagamento
        guest.check_in = data_checkin
        guest.check_out = data_checkout
        guest.amount_per_night = amount
        guest.nights = int(request.POST.get('nights'))
        guest.adults = int(request.POST.get('adults'))
        guest.total = amount * nights * adults
        guest.payment_method = request.POST.get('payment_method')
        guest.save()
        return redirect('listar_family')
        
    # NOVO: Envia a lista de origens para o HTML
    return render(request, 'editar_guest.html', {
        'guest': guest, 
        'origens_do_excel': origens_do_excel
    })



@login_required(login_url='/login/')
def exportar_extra_form(request):
    # 1. Puxa todos os dados do banco
    dados = Extra.objects.all().values('data', 'product', 'amount', 'unitary_value', 'total', 'origin', 'description')
    
    # 2. Transforma em uma tabela do Pandas
    df = pd.DataFrame(dados)
    
    # 3. Prepara a resposta do navegador como um arquivo de download
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="extras.xlsx"'
    
    # 4. Salva o Pandas dentro do arquivo do navegador
    df.to_excel(response, index=False, engine='openpyxl')
    
    # 5. Entrega o arquivo
    return response



@login_required(login_url='/login/')
def exportar_family_form(request):
    # 1. Puxa todos os dados do banco
    dados = FamilyFriend.objects.all().values('name', 'bed_number', 'payment_date', 'check_in', 'check_out', 'amount_per_night', 'nights', 'adults', 'total', 'payment_method')
    
    # 2. Transforma em uma tabela do Pandas
    df = pd.DataFrame(dados)
    
    # 3. Prepara a resposta do navegador como um arquivo de download
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="family.xlsx"'
    
    # 4. Salva o Pandas dentro do arquivo do navegador
    df.to_excel(response, index=False, engine='openpyxl')
    
    # 5. Entrega o arquivo
    return response