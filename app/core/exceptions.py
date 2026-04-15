
class FastShipError(Exception):
  "FastAPIで発生させるすべてのれいがいのためのもの"
  pass

class EntityNotFoundError(FastShipError):
  "Entity not Found in Database"

class ClientNotAuthorized(FastShipError):
  "Client is not authorized to perform the action"

class BadCredentials(FastShipError):
  "User email or password is incorrect"

class InvalidToken(FastShipError):
  "Access token is invalid or expired"


class DeliveryPartnerNotAvailable(FastShipError):
  "Delivery Partner not Found"

