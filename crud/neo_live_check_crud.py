from models.neo_live_check import NeoLiveCheck
from crud.base_crud import CRUDBase


class CRUDNeoLiveCheck(CRUDBase[NeoLiveCheck]):
    pass


neo_live_check = CRUDNeoLiveCheck(NeoLiveCheck)
