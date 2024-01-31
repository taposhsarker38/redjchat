# Import necessary modules and classes
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from .models import Server
from .serializer import ServerSerializer
from django.db.models import Count
from .schema import server_list_docs
# Define a Django ViewSet for handling Server-related operations
class ServerListViewSet(viewsets.ViewSet):
    # Set the initial queryset to include all Server objects
    queryset = Server.objects.all()
    
    # Define a method to handle the 'list' action (GET request)
    @server_list_docs
    def list(self, request):
        """
    Lists servers based on provided query parameters.

    This method retrieves a list of servers based on various query parameters
    that can be specified in the HTTP request. It supports filtering by category,
    limiting the number of servers returned, filtering by user, and more.

    Args:
        request (HttpRequest): The HTTP request object.

    Raises:
        AuthenticationFailed: If 'by_user' or 'by_serverid' is specified and
            the user is not authenticated.

    Filters:
        - category (str): Filters servers by category name.
        - qty (str): Limits the number of servers returned.
        - by_user (str, optional): Filters servers by the requesting user.
        - by_serverid (str, optional): Filters servers by the specified server ID.
        - with_num_members (str, optional): Includes the count of members in each server.

    Returns:
        Response: A JSON response containing a list of serialized servers.

    Usage:
        To list servers:
        ```
        GET /api/servers/?category=gaming&qty=5&by_user=true&with_num_members=true
        ```

    Note:
        - If 'by_user' is specified, authentication is required.
        - If 'by_serverid' is specified, the server ID must exist in the queryset.

    Raises:
        ValidationError: If there is an issue with the provided server ID.
            - "Server with id {by_serverid} not found"
            - "Server value error"

    Examples:
        - To retrieve gaming servers with details and member count:
        ```
        GET /api/servers/?category=gaming&with_num_members=true
        ```

        - To retrieve the first 3 servers for the authenticated user:
        ```
        GET /api/servers/?qty=3&by_user=true
        ```

        - To retrieve a specific server by ID:
        ```
        GET /api/servers/?by_serverid=123
        ```

        - To list all servers without any filtering:
        ```
        GET /api/servers/
        ```
    """
        # Retrieve query parameters from the request
        category = request.query_params.get("category")
        qty = request.query_params.get("qty")
        by_user = request.query_params.get("by_user") == "true"
        by_serverid = request.query_params.get("by_serverid")
        with_num_members = request.query_params.get("with_num_members") == "true"

        # Check authentication if 'by_user' or 'by_serverid' is specified
        # if by_user or by_serverid and not request.user.is_authenticated:
        #     raise AuthenticationFailed()

        # Apply filters based on query parameters
        if category:
            self.queryset = self.queryset.filter(category__name=category)
        if by_user:
            if by_user and request.user.is_authenticated:
                user_id = request.user.id
                self.queryset = self.queryset.filter(member=user_id)
            else:
                raise AuthenticationFailed()
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
