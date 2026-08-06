from scenes.main_menu import MainMenuScene

class ModeSelectScene(MainMenuScene):
    """Redirección de escena antigua hacia el nuevo Hub de Modos (MainMenuScene)."""
    def __init__(self, manager, context=None):
        ctx = dict(context or {})
        ctx["skip_splash"] = True
        super().__init__(manager, context=ctx)
