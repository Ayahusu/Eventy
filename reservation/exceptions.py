from rest_framework.exceptions import APIException
from rest_framework import status

class EventNotOpenForReservation(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "This event is not open for reservations."

class AlreadyReserved(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "You already have an active reservation for this event."

class EventFull(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Event is full."

class ReservationNotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "No active reservation found."