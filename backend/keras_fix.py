"""
Fix tensorflow.keras import for tensorflow-macos on Apple Silicon
Run this before importing any libraries that need tensorflow.keras
"""

import sys
import tensorflow as tf
from tensorflow.python import keras

# Create tensorflow.keras module alias
sys.modules['tensorflow.keras'] = keras
sys.modules['tensorflow.keras.layers'] = keras.layers
sys.modules['tensorflow.keras.models'] = keras.models
sys.modules['tensorflow.keras.callbacks'] = keras.callbacks
sys.modules['tensorflow.keras.optimizers'] = keras.optimizers
sys.modules['tensorflow.keras.preprocessing'] = keras.preprocessing
sys.modules['tensorflow.keras.utils'] = keras.utils

# Also set it as attribute
tf.keras = keras

print("✅ Keras import path fixed for tensorflow-macos!")
