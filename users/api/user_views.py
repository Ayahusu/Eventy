from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from django.http import HttpResponseRedirect
from django.conf import settings

from users.services.user_service import UserService
from .serializers import ChangePasswordSerializer

from drf_spectacular.utils import extend_schema, OpenApiResponse

@extend_schema(tags=['User API Endpoint'])
class UserViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    serializer_class = ChangePasswordSerializer

    @extend_schema(
        request=None,  # <--- Tells Swagger that DELETE does NOT expect a body
        responses={
            302: OpenApiResponse(description="Redirects to login page upon success"),
            500: OpenApiResponse(description="Internal server error"),
        }
    )
    @action(detail=False, methods=['delete'], url_path='delete_profile')
    def delet_profile(self, request):
        try:
            user_id = request.user.id
            success = UserService.delet_profile(user_id)

            if success:
                login_url = getattr(settings, 'LOGIN_REDIRECT_URL', 'https://example.com/login')
                return HttpResponseRedirect(login_url)
            
            return Response(
                    {"detail": "Unable to process this request at this moment due to a server error."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        except:
            # logger.error(f"Failed to delete profile for user {request.user.id}: {str(e)}")
            
            return Response(
                {"detail": "An unexpected internal server error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'], url_path='change_password')
    def change_password(self, request):
        """Changes the authenticated user's password."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Add your password update service logic here...
        return Response({"detail": "Password updated successfully."}, status=status.HTTP_200_OK)
        