
class FastShipError(Exception):
  "FastAPIで発生させるすべてのれいがいのためのもの"

class EntityNotFoundError(FastShipError):
  "Entity not Found in Database"

class ClientNotAuthorized(FastShipError):
  "Client is not authorized to perform the action"
class ClientNotAuthorized(FastShipError):
  "Client is not verified"

class BadCredentials(FastShipError):
  "User email or password is incorrect"

class InvalidToken(FastShipError):
  "Access token is invalid or expired"


class DeliveryPartnerNotAvailable(FastShipError):
  "Delivery Partner not Found"

class NothingToUpdate(FastShipError):
  "No data provided to update"

class BadCredentials(FastShipError):
  "Email or Password is not found"

