"""
Plugin system error classes.
"""


class PluginError(Exception):
    """Base exception for plugin errors"""
    pass


class PluginNotFoundError(PluginError):
    """Plugin not found in any discovery location"""
    pass


class PluginValidationError(PluginError):
    """Plugin failed security validation"""
    pass


class PluginPermissionError(PluginError):
    """Plugin lacks required permissions"""
    pass


class PluginLoadError(PluginError):
    """Plugin failed to load"""
    pass


class PluginExecutionError(PluginError):
    """Plugin execution failed"""
    pass


class PluginDependencyError(PluginError):
    """Plugin dependency not satisfied"""
    pass


class PluginConflictError(PluginError):
    """Plugin conflicts with another plugin"""
    pass
