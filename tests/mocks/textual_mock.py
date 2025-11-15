"""
Mock textual module for testing when textual is not installed.
"""


class MockWidget:
    """Mock Widget class."""

    def __init__(self, *args, **kwargs):
        pass

    def compose(self):
        return []

    def mount(self, *args, **kwargs):
        pass


class MockApp:
    """Mock App class."""

    def __init__(self, *args, **kwargs):
        pass

    def compose(self):
        return []

    def run(self, *args, **kwargs):
        pass

    def exit(self, *args, **kwargs):
        pass


class MockContainer(MockWidget):
    """Mock Container class."""

    pass


class MockHeader(MockWidget):
    """Mock Header class."""

    pass


class MockFooter(MockWidget):
    """Mock Footer class."""

    pass


class MockInput(MockWidget):
    """Mock Input class."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value = ""


class MockLog(MockWidget):
    """Mock Log class."""

    def write(self, text):
        pass


# Mock the main textual module structure
class MockTextual:
    """Mock textual module."""

    class app:
        App = MockApp
        ComposeResult = list

    class widget:
        Widget = MockWidget

    class containers:
        Container = MockContainer
        Horizontal = MockContainer
        Vertical = MockContainer

    class widgets:
        Header = MockHeader
        Footer = MockFooter
        Input = MockInput
        Log = MockLog
        Button = MockWidget
        Label = MockWidget

    # Direct exports
    App = MockApp
    Widget = MockWidget
