# Import necessary modules and classes
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from .models import Server
from .serializer import ServerSerializer
from django.db.models import Count

# Define a Django ViewSet for handling Server-related operations
class ServerListViewSet(viewsets.ViewSet):
    # Set the initial queryset to include all Server objects
    queryset = Server.objects.all()

    # Define a method to handle the 'list' action (GET request)
    def list(self, request):
        # Retrieve query parameters from the request
        category = request.query_params.get("category")
        qty = request.query_params.get("qty")
        by_user = request.query_params.get("by_user") == "true"
        by_serverid = request.query_params.get("by_serverid")
        with_num_members = request.query_params.get("with_num_members") == "true"

        # Check authentication if 'by_user' or 'by_serverid' is specified
        if by_user or by_serverid and not request.user.is_authenticated:
            raise AuthenticationFailed()

        # Apply filters based on query parameters
        if category:
            self.queryset = self.queryset.filter(category__name=category)
        if by_user:
            user_id = request.user.id
            self.queryset = self.queryset.filter(member=user_id)
        if with_num_members:
            self.queryset = self.queryset.annotate(num_members=Count("member"))
        if qty:
            self.queryset = self.queryset[:int(qty)]
        if by_serverid:
            try:
                # Filter queryset by server id and validate existence
                self.queryset = self.queryset.filter(id=by_serverid)
                if not self.queryset.exists():
                    raise ValidationError(detail=f"Server with id {by_serverid} not found")
            except ValueError:
                raise ValidationError(detail="Server value error")

        # Serialize the queryset and return the response
        serializer = ServerSerializer(self.queryset, many=True)
        return Response(serializer.data)
