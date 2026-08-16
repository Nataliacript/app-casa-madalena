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
	path('resultado/excluir/<int:id>/', views.excluir_resultado, name='excluir_resultado'),
    path('extras/', views.listar_extras, name='listar_extras'),
    path('extras/novo/', views.novo_extra, name='novo_extra'),
    path('extras/upload_config/', views.upload_config_extras, name='upload_config_extras'),
	path('extras/editar/<int:id>/', views.editar_extra, name='editar_extra'),
    path('extras/excluir/<int:id>/', views.excluir_extra, name='excluir_extra'),
	path('extras/exportar/', views.exportar_extra_form, name='exportar_extra_form'),
	path('extras/family/', views.listar_family, name='listar_family'),
    path('extras/money-box/', views.listar_money_box, name='listar_money_box'),
    path('extras/family/novo/', views.criar_family, name='criar_family'),
    path('extras/family/editar/<int:id>/', views.editar_family, name='editar_family'),
    path('extras/family/excluir/<int:id>/', views.excluir_family, name='excluir_family'),
	path('extras/family/exportar/', views.exportar_family_form, name='exportar_family_form'),

]
