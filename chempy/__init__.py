# -*- coding: utf-8 -*-
"""
ChemPy is a Python package which aims to be useful in solving chemistry
related problems.
"""

from __future__ import absolute_import, division, print_function

from ._url import __url__
from ._release import __version__
from .chemistry import Substance, Reaction, Equilibrium, ReactionSystem
from .equilibria import EqSystem
