from UI.MenuObjects.Label import Label


class MultiLineLabel(Label):
    """
    Класс, реализующий многострочный Label. Под этим подразумевается несколько Label-ов,
    расположенные один под другим.
    """
    def __init__(self):
        super().__init__()
