from models.neo_live_comment import NeoLiveComment
from crud.base_crud import CRUDBase


class CRUDNeoLiveComment(CRUDBase[NeoLiveComment]):
    pass


neo_live_comment = CRUDNeoLiveComment(NeoLiveComment)
