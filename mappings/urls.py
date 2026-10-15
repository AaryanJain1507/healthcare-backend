from django.urls import path
from .views import MappingListCreateView, MappingPatientOrDetailView

urlpatterns = [
    path('', MappingListCreateView.as_view(), name='mapping_list_create'),
    path('<int:pk>/', MappingPatientOrDetailView.as_view(), name='mapping_detail'),
]
