
class FastShipError(Exception):
  status_code:int = 500
  detail:str="An unexpected error occurred"

class EntityNotFoundError(FastShipError):
  status_code=404
  detail="Entity not found"

class ClientNotAuthorized(FastShipError):
  status_code = 403
  detail = "Not authorized to perform this action"

class BadCredentials(FastShipError):
  status_code = 401
  detail = "Email or password is incorrect"

class InvalidToken(FastShipError):
   status_code = 401
   detail = "Access token is invalid or expired"


class DeliveryPartnerNotAvailable(FastShipError):
  status_code = 404
  detail = "Delivery partner not available"

class NothingToUpdate(FastShipError):
    status_code = 400
    detail = "No data provided to update"


