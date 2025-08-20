from models.neo_global_json_config import GlobalJsonConfig
from crud.async_crud.base_crud import CRUDBase


class CRUDGlobalJsonConfig(CRUDBase[GlobalJsonConfig]):
    pass


neo_global_json_config = CRUDGlobalJsonConfig(GlobalJsonConfig, engine="neoailive")