# This module caused circular imports when using custom models,
# base_models reads managers, thus imports this file, but first loads models that need base_models again.
import warnings
warnings.warn("Importing managers from fluent_blogs.models is deprecated; use fluent_blogs.managers instead.", DeprecationWarning)

from fluent_blogs.managers import *  # noqa
