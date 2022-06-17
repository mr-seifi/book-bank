import os

if os.environ['ENV'] == 'dev':
    from .local import *
else:
    from .pro import *
