from field.arena import Arena


# api/arena.py
class APIArena:
    _instance = None  # 存放唯一的 arena 實例

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            raise ValueError('Arena is not initialized yet!')
        return cls._instance

    @classmethod
    def set_instance(cls, arena):
        cls._instance = arena


# 供 API 其他模組使用的訪問接口
def get_arena() -> Arena | None:
    return APIArena.get_instance()
