from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


from users.services.auth_service import AuthService


class UserAuthViewSet(ViewSet):
    permission_classes = [AllowAny ]
    throttle_classes = [AnonRateThrottle]

    # Signup endpoint.
    #
    # User creation logic is delegated to AuthService
    # to keep the view layer responsible only for HTTP handling.
    #
    # The service validates user data, creates the account,
    # and returns the created user response.
    @action(detail=False, methods=['post'])
    def signup(self, request):
        user_data = AuthService.register_service(request.data)
        return Response(user_data, status=status.HTTP_201_CREATED)
    
    # Login endpoint.
    #
    # Authentication logic is delegated to AuthService
    # to keep the view layer responsible only for HTTP handling.
    #
    # The service validates credentials and generates
    # authentication tokens for the client.
    @action(detail=False, methods=['post'])
    def login(self, request):
        user_data = AuthService.login_service(request.data)
        return Response(user_data, status=status.HTTP_200_OK)
