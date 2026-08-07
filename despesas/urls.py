from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_despesas, name='home'),
    path('novo/', views.criar_despesa, name='criar_despesa'),
    path('editar/<int:id>/', views.editar_despesa, name='editar_despesa'), 
    path('excluir/<int:id>/', views.excluir_despesa, name='excluir_despesa'),
    path('login/', views.tela_login, name='tela_login'),
    path('exportar/', views.exportar_excel, name='exportar_excel'), # <-- ROTA DO EXCEL
]


from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_despesas, name='home'),
    path('novo/', views.criar_despesa, name='criar_despesa'),
    path('editar/<int:id>/', views.editar_despesa, name='editar_despesa'), 
    path('excluir/<int:id>/', views.excluir_despesa, name='excluir_despesa'),
    path('login/', views.tela_login, name='tela_login'),
	path('logout/', views.deslogar, name='logout'), 
    path('exportar/', views.exportar_excel, name='exportar_excel'),
    path('resultado/', views.resultado_page, name='resultado_page'), 
	path('resultado/excluir/<int:id>/', views.excluir_resultado, name='excluir_resultado'), # NOVA ROTA
    path('extras/', views.listar_extras, name='listar_extras'),
    path('extras/novo/', views.novo_extra, name='novo_extra'),
    path('extras/upload_config/', views.upload_config_extras, name='upload_config_extras'),
]