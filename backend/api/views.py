from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from importer.services import import_products_from_yaml


# Create your views here.


class ImportProductsView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        file_path = request.data.get('file_path')

        if not file_path:
            return Response(
                {'error': 'file_path is required'}, 
                status=400
            )
        
        import_products_from_yaml(file_path)
        return Response({'status': 'import started'})
        





