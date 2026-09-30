class utils:

    def register(self, name: str, HANDLER: dict[str, object]) -> object:
        def decorator(func: object) -> object:
            HANDLER[name] = func
            return func
        return decorator