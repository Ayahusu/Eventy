from rest_framework.viewsets import ViewSet

from users.services.user_service import UserService
class UserViewSet(ViewSet):
    
    def delet_profile(self, request):
        response = UserService.delet_profile(request.data)
        return response