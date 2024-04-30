import tensorflow as tf
from tensorflow.keras.models import Model


class AutoEncoder(Model):
  def __init__(self):
    """
    Creates a new AutoEncoder library instance.

    :param ip: The IP address of the Robobo robot.   (param "nombre del parametro" : descipcion)
    :type ip: string    (tipo de dato que entra al parametro "nombre del parametro")
    """
    super(AutoEncoder, self).__init__()
    self.encoder = tf.keras.Sequential([
                  tf.keras.layers.Dense(64, activation="relu"),
                  tf.keras.layers.Dense(32, activation="relu"),
                  tf.keras.layers.Dense(16, activation="relu"),
                  tf.keras.layers.Dense(8, activation="relu")
              ])
    self.decoder = tf.keras.Sequential([
                  tf.keras.layers.Dense(16, activation="relu"),
                  tf.keras.layers.Dense(32, activation="relu"),
                  tf.keras.layers.Dense(64, activation="relu"),
                  tf.keras.layers.Dense(140, activation="sigmoid")
              ])
  def call(self, x):
    encoded = self.encoder(x)
    decoded = self.decoder(encoded)
    return decoded