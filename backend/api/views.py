from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from importer.services import import_products_from_yaml
from products.models import Product
from products.serializers import ProductSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser

# Create your views here.


class ImportProductsView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        file_path = request.data.get('file_path')

        if not file_path:
            return Response(
                {'error': 'file_path is required'}, 
                status=400
            )
        
        import_products_from_yaml(file_path)
        return Response({'status': 'import started'})
        


class ProductListView(ListAPIView):
    serializer_class = ProductSerializer
    
    def get_queryset(self):
        qs = Product.objects.all()

        shop_id = self.request.query_params.get('shop')
        category_id = self.request.query_params.get('category')

        if shop_id:
            qs = qs.filter(product_infos__shop_id=shop_id)

        if category_id:
            qs = qs.filter(category_id=category_id)

        return qs.distinct()
    
