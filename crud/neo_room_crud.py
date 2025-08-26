from models.neo_room import NeoRoom
from crud.base_crud import CRUDBase


class CRUDNeoRoom(CRUDBase[NeoRoom]):
    pass


neo_room = CRUDNeoRoom(NeoRoom)
