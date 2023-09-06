# Conditional import for gui only when inside Nuke
try:
    import nuke
    from .gui import *
except ImportError or AttributeError:
    pass

print(__file__)