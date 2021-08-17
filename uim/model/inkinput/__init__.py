# -*- coding: utf-8 -*-
"""
Input Data
==========
The  input  data consists of input data configuration the device and its sensor channels producing sensor data.
The sensor data repository is a data repository, which holds a collection of `SensorData` instances.

The `InputContext` repository is a data repository responsible for storing information about where the raw input
data-frame originates from, by allowing unique identification of the exact input source. The repository stores
information about the device itself, the environment and the on-board device sensors for each data point.

The repository holds the following data collections:

- A collection of `InkInputProvider' instances
- A collection of `InputDevice` instances
- A collection of `Environment` instances
- A collection of `SensorContext` instances
- A collection of `InputContext` instances
"""
__all__ = ['inputdata', 'sensordata']

from uim.model.inkinput import inputdata
from uim.model.inkinput import sensordata
