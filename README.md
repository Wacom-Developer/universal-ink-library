
# Universal Ink Library

[![PyPI](https://img.shields.io/pypi/v/universal-ink-library.svg)](https://pypi.python.org/pypi/universal-ink-library)
[![PyPI](https://img.shields.io/pypi/pyversions/universal-ink-library.svg)](https://pypi.python.org/pypi/universal-ink-library)
[![Documentation](https://img.shields.io/badge/api-reference-blue.svg)](https://developer-docs.wacom.com/sdk-for-ink/docs/model) 

Universal Ink Library is a pure Python package for working with Universal Ink Models ([UIM](https://developer.wacom.com/products/universal-ink-model)).
The UIM defines a language-neutral and platform-neutral data model for representing and manipulating digital ink data captured using an electronic pen or stylus, or using touch input.

The main aspects of the UIM are:

- Interoperability of ink-based data models by defining a standardized interface with other systems
- Biometric data storage mechanism
- Spline data storage mechanism
- Rendering configurations storage mechanism
- Ability to compose spline/raw-input based logical trees, which are contained within the ink model
- Portability, by enabling conversion to common industry standards
- Extensibility, by enabling the description of ink data related semantic meta-data
- Standardized serialization mechanism

This reference document defines a RIFF container and Protocol Buffers schema for serialization of ink models as well as 
a standard mechanism to describe relationships between different parts of the ink model, and/or between parts of the ink 
model and external entities.

The specified serialization schema is based on the following standards:

- **Resource Interchange File Format (RIFF)** - A generic file container format for storing data in tagged chunks
- **Protocol Buffers v3** - A language-neutral, platform-neutral extensible mechanism for serializing structured data
- **Resource Description Framework (RDF)** - A standard model for data interchange on the Web
- **OWL 2 Web Ontology Language (OWL2)** - An ontology language for the Semantic Web with formally defined meaning

## Data Model
The *Universal Ink Model* has five fundamental categories:

- **Input data**: A collection of data repositories, holding raw sensor input, input device/provider configurations, sensor channel configurations, etc. Each data repository keeps certain data-sets isolated and is responsible for specific type(s) of data
- **Ink data**: The visual appearance of the digital ink, presented as ink geometry with rendering configurations
- **Meta-data**: Related meta-data about the environment, input devices, etc.
- **Ink Trees / Views**: A collection of logical trees, representing structures of hierarchically organized paths or raw input data-frames
- **Semantic triple store**: An RDF compliant triple store, holding semantic information, such as text structure, handwriting recognition results, and semantic entities

The diagram below illustrates the different logical parts of the ink model.
![Logical Parts of Ink Model.](https://github.com/Wacom-Developer/universal-ink-library/raw/main/assets/uim-v1.png)

This UML diagram illustrates the complete Ink Model in terms of logical models and class dependencies.
![UML Diagram](https://github.com/Wacom-Developer/universal-ink-library/raw/main/assets/uim-uml-all-v9.png)

The *Universal Ink Model* provides the flexibility required for a variety of applications, since the display of pen data is only one aspect.
For example, the same data can be used for data mining or even signature comparison, while the ink display can be on a range of platforms potentially requiring different scaling and presentation.

## Input data

In reality, pen data is captured from a pen device as a set of positional points:

![Digital-ink-w](https://github.com/Wacom-Developer/universal-ink-library/raw/main/assets/overview_ink_device_sensor_channels.png)

Depending on the type of hardware, in addition to the x/y positional coordinates, the points can contain further information such as pen tip force and angle.
Collectively, this information is referred to as sensor data and the *Universal Ink Model* provides a means of storing all the available data.
For example, with some types of hardware, pen hover coordinates can be captured while the pen is not in contact with the surface.
The information is saved in the *Universal Ink Model* and can be used when required.

## Ink data

Ink data is the result of the [ink geometry pipeline](https://developer-docs.wacom.com/sdk-for-ink/docs/pipeline) of the [WILL SDK for ink](https://developer.wacom.com/products/will-sdk-for-ink).
Pen strokes are identified as continuous sets of pen coordinates captured while the pen is in contact with the surface. 
For example, writing the letter ‘w', as illustrated below.
The process converts each pen stroke into a matmeta-datahematical representation, which can then be used to render the shape on a display.
Steps in the so-called Ink Geometry pipeline are illustrated below where each step is configured by an application to generate the desired output:

![Digital-ink-rendering](https://github.com/Wacom-Developer/universal-ink-library/raw/main/assets/pen-data-w-rendering.png)

As a result, the data points are smoothed and shaped to produce the desired representation. 
For example, simulating the appearance of a felt-tip ink pen.
Raster and vector rendering is supported with a selection of rendering brush types.

The results are saved as Ink data, containing ink geometry and rendering information.

## Meta-data

Meta-data is added as data about the pen data.
The *Universal Ink Model* allows for administrative information such as author name, location, pen data source, etc.
Further meta-data is computed by analysis of the pen data.
An example of digital ink is annotated below:

![Digital-ink-annotated](https://github.com/Wacom-Developer/universal-ink-library/raw/main/assets/pen-data-annotated.png)

The labels identify pen strokes *s1, s2, s3*, etc.
In addition, groups of strokes are identified as *g1, g2, g3*, etc.
Pen strokes are passed to a handwriting recognition engine, and the results are stored as additional meta-data, generally referred to as semantic data.
The semantic data is stored with reference to the groups, categorized as single characters, individual words, lines of text, and so on.


# Installation

Our Universal Ink Library can be installed using pip.

``
    $ pip install universal-ink-library
``


# Quick Start

## File handling
###  Loading UIM

The `UIMParser` is be used to load a serialized Universal Ink Model in version 3.0.0 or 3.1.0 and you receive the memory model `InkModel` which can be used for extracting the relevant data.

```python
from uim.codec.parser.uim import UIMParser
from uim.model.ink import InkModel

parser: UIMParser = UIMParser()
# ---------------------------------------------------------------------------------
# Parse a UIM file version 3.0.0
# ---------------------------------------------------------------------------------
ink_model_1: InkModel = UIMParser().parse('../ink/uim_3.0.0/1) Value of Ink 1.uim')
# ---------------------------------------------------------------------------------
# Parse a UIM file version 3.1.0
# ---------------------------------------------------------------------------------
ink_model_2: InkModel = UIMParser().parse('../ink/uim_3.1.0/1) Value of Ink 1.uim')

```
###  Loading WILL 2.0 file

The `WILL2Parser` is be used to load a serialized Wacom Ink Layer Language (WILL), e.g., from [Wacom's Inkspace](https://inkspace.wacom.com/).

```python
from uim.codec.parser.will import WILL2Parser
from uim.model.ink import InkModel

parser: WILL2Parser = WILL2Parser()
ink_model: InkModel = parser.parse('../ink/will/elephant.will')
```

### Saving of UIM

Saving the `InkModel` as a Universal Ink Model file.

```python
from uim.codec.writer.encoder.encoder_3_1_0 import UIMEncoder310
from uim.model.ink import InkModel

ink_model: InkModel = InkModel()
... 

# Save the model, this will overwrite an existing file
with io.open('3_1_0.uim', 'wb') as uim:
    # unicode(data) auto-decodes data to unicode if str
    uim.write(UIMEncoder310().encode(ink_model))
```

Find the sample, [here](https://github.com/Wacom-Developer/universal-ink-library/blob/main/samples/sample_file_handling.py)

## InkModel

### Iterate over semantics

If the `InkModel` is enriched with semantics from handwriting recognition and named entity recognition, or named entity linking.
The semantics an be access with a helper function `uim_extract_text_and_semantics_from` or by iterating the views, like shown in `uim_extract_text_and_semantics_from` function:

```python
    if ink_model.has_knowledge_graph() and ink_model.has_tree(CommonViews.HWR_VIEW.value):
        # The sample
        words, entities, text = uim_extract_text_and_semantics_from(ink_model, hwr_view=CommonViews.HWR_VIEW.value)
        print('=' * 100)
        print(' Recognised text: ')
        print(text)
        print('=' * 100)
        print(' Words:')
        print('=' * 100)
        for word_idx, word in enumerate(words):
            print(f' Word #{word_idx + 1}:')
            print(f'  Text: {word["text"]}')
            print(f'  Alternatives: {word["alternatives"]}')
            print(f'  Bounding box: x:={word["bounding_box"]["x"]}, y:={word["bounding_box"]["y"]}, '
                  f'width:={word["bounding_box"]["width"]}, height:={word["bounding_box"]["height"]}')
            print('')
        print('=' * 100)
        print(' Entities:')
        print('=' * 100)
        entity_idx: int = 1
        for entity_uri, entity_mappings in entities.items():
            print(f' Entity #{entity_idx}: URI: {entity_uri}')
            print("-" * 100)
            print(f" Label: {entity_mappings[0]['label']}")
            print(f' Ink Stroke IDs:')
            for word_idx, entity in enumerate(entity_mappings):
                print(f"  #{word_idx + 1}: Word match: {entity['path_id']}")
            print('=' * 100)
            entity_idx += 1
```

### Accessing input and ink data
In order to access ink input configuration data, sensor data, or stroke data from `InkModel`, you can use the following functions:

```python
from typing import Dict
from uuid import UUID

from uim.codec.parser.uim import UIMParser
from uim.model.ink import InkModel
from uim.model.inkinput.inputdata import InkInputType, InputContext, SensorContext, InputDevice
from uim.model.inkinput.sensordata import SensorData

if __name__ == '__main__':
    parser: UIMParser = UIMParser()
    # This file contains ink from different providers: PEN, TOUCH, MOUSE
    ink_model: InkModel = parser.parse('../ink/uim_3.1.0/6) Different Input Providers.uim')
    
    mapping_type: Dict[UUID, InkInputType] = {}
    if ink_model.has_ink_structure():
        print('InkInputProviders:')
        print('-------------------')
        # Iterate Ink input providers
        for ink_input_provider in ink_model.input_configuration.ink_input_providers:
            print(f' InkInputProvider. ID: {ink_input_provider.id} | type: {ink_input_provider.type}')
            mapping_type[ink_input_provider.id] = ink_input_provider.type
        print()
        print('Strokes:')
        print('--------')
        # Iterate over strokes
        for stroke in ink_model.strokes:
            print(f'|- Stroke (id:={stroke.id} | points count: {stroke.points_count})')
            if stroke.style and stroke.style.path_point_properties:
                print(f'|   |- Style (render mode:={stroke.style.render_mode_uri} | color:=('
                      f'red: {stroke.style.path_point_properties.red}, '
                      f'green: {stroke.style.path_point_properties.green}, '
                      f'blue: {stroke.style.path_point_properties.green}, '
                      f'alpha: {stroke.style.path_point_properties.alpha}))')
            # Stroke is produced by sensor data being processed by the ink geometry pipeline
            sd: SensorData = ink_model.sensor_data.sensor_data_by_id(stroke.sensor_data_id)
            # Get InputContext for the sensor data
            input_context: InputContext = ink_model.input_configuration.get_input_context(sd.input_context_id)
            # Retrieve SensorContext
            sensor_context: SensorContext = ink_model.input_configuration\
                .get_sensor_context(input_context.sensor_context_id)
            for scc in sensor_context.sensor_channels_contexts:
                # Sensor channel context is referencing input device
                input_device: InputDevice = ink_model.input_configuration.get_input_device(scc.input_device_id)
                print(f'|   |- Input device (id:={input_device.id} | type:=({mapping_type[scc.input_provider_id]})')
                # Iterate over sensor channels
                for c in scc.channels:
                    print(f'|   |     |- Sensor channel (iid:={c.id} | name: {c.type.name} '
                          f'| values: {sd.get_data_by_id(c.id).values}')
            print('|')
```

Find the sample, [here](https://github.com/Wacom-Developer/universal-ink-library/blob/main/samples/sample_input_and_ink.py)

## Creating an Ink Model 
Creating an `InkModel` from the scratch:

```python
import io
from typing import List

from uim.codec.writer.encoder.encoder_3_1_0 import UIMEncoder310
from uim.model.base import UUIDIdentifier
from uim.model.ink import InkModel, InkTree
from uim.model.inkdata.brush import VectorBrush, BrushPolygon, BrushPolygonUri
from uim.model.inkdata.strokes import Spline, Style, Stroke, LayoutMask
from uim.model.inkinput.inputdata import Environment, InkInputProvider, InkInputType, InputDevice, SensorChannel, \
    InkSensorType, InkSensorMetricType, SensorChannelsContext, SensorContext, InputContext
from uim.model.inkinput.sensordata import SensorData, InkState
from uim.model.semantics.node import StrokeGroupNode, StrokeNode, URIBuilder
import uim.model.semantics.schema as schema
from uim.utils.matrix import Matrix4x4

if __name__ == '__main__':
    """Creates an ink model from the scratch."""
    # Create the model
    ink_model: InkModel = InkModel()
    # Setting a unit scale factor
    ink_model.unit_scale_factor = 1.5
    # Using a 4x4 matrix for scaling
    ink_model.transform = Matrix4x4.create_scale(1.5)

    # Properties are added as key-value pairs
    ink_model.properties.append(("Author", "Markus"))
    ink_model.properties.append(("PrimaryLanguage", "en_US"))

    # Create an environment
    env: Environment = Environment()
    env.properties.append(("os.name", "macOS Monterey"))
    env.properties.append(("os.version", "12.2.1 (21D62)"))
    env.properties.append(("os.platform", "macOS"))
    ink_model.input_configuration.environments.append(env)

    # Ink input provider can be pen, mouse or touch.
    provider: InkInputProvider = InkInputProvider(input_type=InkInputType.PEN)
    provider.properties.append(("pen.id", "1234567"))
    ink_model.input_configuration.ink_input_providers.append(provider)

    # Input device is the sensor (pen tablet, screen, etc.)
    input_device: InputDevice = InputDevice()
    input_device.properties.append(("dev.id", "123454321"))
    input_device.properties.append(("dev.manufacturer", "Wacom"))
    input_device.properties.append(("dev.model", "Wacom One"))
    input_device.properties.append(("dev.cpu", "Intel"))
    input_device.properties.append(("dev.graphics.display", "1920x1080 32bit"))
    ink_model.input_configuration.devices.append(input_device)

    # Create a group of sensor channels
    sensor_channels_tablet: list = [
        SensorChannel(channel_type=InkSensorType.TIMESTAMP, metric=InkSensorMetricType.TIME, resolution=1.0)
    ]

    scc_wacom_one: SensorChannelsContext = SensorChannelsContext(channels=sensor_channels_tablet,
                                                                 ink_input_provider_id=provider.id,
                                                                 input_device_id=input_device.id)

    # Add sensor channel contexts
    sensor_context: SensorContext = SensorContext()
    sensor_context.add_sensor_channels_context(scc_wacom_one)
    ink_model.input_configuration.sensor_contexts.append(sensor_context)

    # Create the input context using the Environment and the Sensor Context
    input_context: InputContext = InputContext(environment_id=env.id, sensor_context_id=sensor_context.id)
    ink_model.input_configuration.input_contexts.append(input_context)

    # Create sensor data
    sensor_data_0: SensorData = SensorData(UUIDIdentifier.id_generator(), input_context_id=input_context.id,
                                           state=InkState.PLANE)
    sensor_data_0.add_timestamp_data(sensor_channels_tablet[0],
                                     [1649226708.175, 1649226708.182, 1649226708.197, 1649226708.216, 1649226708.232,
                                      1649226708.25, 1649226708.266, 1649226708.282, 1649226708.3, 1649226708.316,
                                      1649226708.332, 1649226708.35, 1649226708.366, 1649226708.382, 1649226708.4,
                                      1649226708.416, 1649226708.432, 1649226708.451, 1649226708.466, 1649226708.482,
                                      1649226708.501, 1649226708.516, 1649226708.532, 1649226708.548, 1649226708.566,
                                      1649226708.582, 1649226708.598, 1649226708.616, 1649226708.632, 1649226708.648,
                                      1649226708.666, 1649226708.682, 1649226708.698, 1649226708.716, 1649226708.732,
                                      1649226708.748, 1649226708.766, 1649226708.782, 1649226708.798, 1649226708.816,
                                      1649226708.832, 1649226708.848, 1649226708.866, 1649226708.882, 1649226708.898,
                                      1649226708.907, 1649226708.909])

    sensor_data_1: SensorData = SensorData(UUIDIdentifier.id_generator(), input_context_id=input_context.id,
                                           state=InkState.PLANE)
    sensor_data_1.add_timestamp_data(sensor_channels_tablet[0],
                                     [1649226709.89, 1649226709.897, 1649226709.911, 1649226709.931, 1649226709.947,
                                      1649226709.961, 1649226709.981, 1649226709.997, 1649226710.012, 1649226710.027,
                                      1649226710.048, 1649226710.062, 1649226710.078, 1649226710.099, 1649226710.112,
                                      1649226710.128, 1649226710.148, 1649226710.162, 1649226710.178, 1649226710.194,
                                      1649226710.21, 1649226710.232, 1649226710.248, 1649226710.26, 1649226710.278,
                                      1649226710.294, 1649226710.314, 1649226710.328, 1649226710.349, 1649226710.364,
                                      1649226710.378, 1649226710.398, 1649226710.414, 1649226710.428, 1649226710.448,
                                      1649226710.464, 1649226710.478, 1649226710.498, 1649226710.514, 1649226710.528,
                                      1649226710.548, 1649226710.564, 1649226710.578, 1649226710.594, 1649226710.614,
                                      1649226710.626, 1649226710.644, 1649226710.662, 1649226710.665])

    sensor_data_2: SensorData = SensorData(UUIDIdentifier.id_generator(), input_context_id=input_context.id,
                                           state=InkState.PLANE)
    sensor_data_2.add_timestamp_data(sensor_channels_tablet[0],
                                     [1649226711.773, 1649226711.78, 1649226711.796, 1649226711.812, 1649226711.83,
                                      1649226711.846, 1649226711.862, 1649226711.88, 1649226711.896, 1649226711.912,
                                      1649226711.928, 1649226711.946, 1649226711.962, 1649226711.978, 1649226711.996,
                                      1649226712.012, 1649226712.028, 1649226712.046, 1649226712.062, 1649226712.078,
                                      1649226712.096, 1649226712.112, 1649226712.128, 1649226712.146, 1649226712.162,
                                      1649226712.178, 1649226712.196, 1649226712.212, 1649226712.228, 1649226712.246,
                                      1649226712.262, 1649226712.278, 1649226712.296, 1649226712.312, 1649226712.332,
                                      1649226712.344, 1649226712.362, 1649226712.378, 1649226712.394, 1649226712.412,
                                      1649226712.428, 1649226712.444, 1649226712.463, 1649226712.478, 1649226712.498,
                                      1649226712.512, 1649226712.528, 1649226712.548, 1649226712.562, 1649226712.578,
                                      1649226712.594, 1649226712.612, 1649226712.628, 1649226712.648, 1649226712.662,
                                      1649226712.678, 1649226712.699, 1649226712.712, 1649226712.728, 1649226712.744,
                                      1649226712.76, 1649226712.778, 1649226712.794, 1649226712.81, 1649226712.832,
                                      1649226712.844, 1649226712.864, 1649226712.878, 1649226712.895, 1649226712.896])

    sensor_data_3: SensorData = SensorData(UUIDIdentifier.id_generator(), input_context_id=input_context.id,
                                           state=InkState.PLANE)
    sensor_data_3.add_timestamp_data(sensor_channels_tablet[0],
                                     [1649226713.731, 1649226713.746, 1649226713.764, 1649226713.776, 1649226713.796,
                                      1649226713.815, 1649226713.83, 1649226713.846, 1649226713.864, 1649226713.879,
                                      1649226713.889, 1649226713.932, 1649226713.946, 1649226713.964, 1649226713.98,
                                      1649226714.012, 1649226714.03, 1649226714.046, 1649226714.062, 1649226714.08,
                                      1649226714.096, 1649226714.113, 1649226714.13, 1649226714.146, 1649226714.162,
                                      1649226714.181, 1649226714.186])

    # Add sensor data to the model
    ink_model.sensor_data.add(sensor_data_0)
    ink_model.sensor_data.add(sensor_data_1)
    ink_model.sensor_data.add(sensor_data_2)
    ink_model.sensor_data.add(sensor_data_3)

    # We need to define a brush polygon
    points: list = [(10, 10), (0, 10), (0, 0), (10, 0)]
    brush_polygons: list = [BrushPolygon(min_scale=0., points=points)]

    # Create the brush object using polygons
    vector_brush_0: VectorBrush = VectorBrush(
        "app://qa-test-app/vector-brush/MyTriangleBrush",
        brush_polygons)

    # Add it to the model
    ink_model.brushes.add_vector_brush(vector_brush_0)

    # Add a brush specified with shape Uris
    poly_uris: list = [
        BrushPolygonUri("will://brush/3.0/shape/Circle?precision=20&radius=1", 0.),
        BrushPolygonUri("will://brush/3.0/shape/Ellipse?precision=20&radiusX=1&radiusY=0.5", 4.0)
    ]

    vector_brush_1: VectorBrush = VectorBrush(
        "app://qa-test-app/vector-brush/MyEllipticBrush",
        poly_uris)

    ink_model.brushes.add_vector_brush(vector_brush_1)

    # Specify the layout of the stroke data, in this case the stroke will have variable X, Y and Size properties.
    layout_mask: int = LayoutMask.X.value | LayoutMask.Y.value | LayoutMask.SIZE.value

    # Provide the stroke data - in this case 4 data points, each consisting of X, Y, Size
    path_0: List[float] = [719.688, 301.988, 1.0, 719.688, 301.988, 1.0, 719.688, 301.981, 1.0, 719.688, 301.963, 1.0,
                           719.688, 301.94, 1.0, 719.598, 301.923, 1.0, 719.365, 301.916, 1.0, 719.034, 301.918, 1.0,
                           718.749, 301.92, 1.0, 718.601, 301.922, 1.0, 718.557, 301.922, 1.0, 718.49, 301.937, 1.0,
                           718.301, 302.002, 1.0, 717.953, 302.193, 1.0, 717.465, 302.612, 1.0, 716.874, 303.333, 1.0,
                           716.216, 304.35, 1.0, 715.505, 305.621, 1.0, 714.709, 307.159, 1.0, 713.768, 309.035, 1.0,
                           712.629, 311.335, 1.0001, 711.307, 314.054, 1.0032, 709.92, 317.047, 1.0115, 708.615,
                           320.041, 1.0251, 707.48, 322.805, 1.0449, 706.491, 325.339, 1.0732, 705.583, 327.882, 1.1081,
                           704.762, 330.676, 1.1431, 704.136, 333.765, 1.1754, 703.806, 336.985, 1.2092, 703.834,
                           340.136, 1.2482, 704.228, 343.103, 1.2912, 704.956, 345.841, 1.335, 705.961, 348.318, 1.3777,
                           707.178, 350.493, 1.4175, 708.564, 352.333, 1.454, 710.069, 353.821, 1.4894, 711.622,
                           354.934, 1.5282, 713.152, 355.651, 1.5732, 714.608, 355.999, 1.6233, 715.963, 356.05, 1.6737,
                           717.203, 355.873, 1.7193, 718.323, 355.504, 1.7572, 719.312, 354.987, 1.7866, 720.14,
                           354.418, 1.8066, 720.795, 353.918, 1.7667, 721.283, 353.572, 1.608, 721.613, 353.394, 1.3529,
                           721.791, 353.34, 1.1085, 721.845, 353.349, 0.9692, 721.829, 353.372, 0.9407, 721.829,
                           353.372, 0.9407]
    path_1: List[float] = [750.477, 303.813, 1.0, 750.477, 303.813, 1.0, 750.469, 303.805, 1.0, 750.451, 303.789, 1.0,
                           750.428, 303.767, 1.0, 750.411, 303.751, 1.0, 750.367, 303.58, 1.0, 750.281, 303.194, 1.0,
                           750.172, 302.893, 1.0087, 750.091, 303.308, 1.0413, 750.06, 305.053, 1.1002, 750.073,
                           308.489, 1.172, 750.134, 313.214, 1.2388, 750.272, 318.388, 1.2953, 750.482, 323.29, 1.344,
                           750.702, 327.581, 1.3868, 750.853, 331.172, 1.422, 750.918, 333.963, 1.449, 750.937, 335.825,
                           1.4723, 750.985, 336.702, 1.501, 751.209, 336.508, 1.5391, 751.805, 335.057, 1.5821, 752.97,
                           332.049, 1.6188, 754.712, 327.535, 1.6419, 756.774, 322.207, 1.6502, 758.834, 316.976,
                           1.6496, 760.686, 312.437, 1.6458, 762.33, 308.756, 1.6406, 763.762, 306.03, 1.6317, 765.055,
                           304.347, 1.6174, 766.305, 303.705, 1.6031, 767.594, 303.9, 1.5959, 768.95, 304.793, 1.6018,
                           770.297, 306.365, 1.6217, 771.477, 308.548, 1.6525, 772.367, 311.28, 1.6895, 772.976,
                           314.424, 1.7253, 773.419, 317.725, 1.7533, 773.827, 320.99, 1.7705, 774.26, 324.085, 1.7804,
                           774.705, 326.877, 1.7893, 775.124, 329.243, 1.8049, 775.479, 331.125, 1.8317, 775.749,
                           332.551, 1.867, 775.928, 333.588, 1.903, 776.026, 334.323, 1.9323, 776.065, 334.815, 1.952,
                           776.069, 335.099, 1.947, 776.067, 335.199, 1.8192, 776.076, 335.178, 1.5495, 776.095,
                           335.116, 1.2262, 776.111, 335.069, 1.0012, 776.118, 335.053, 0.9232, 776.118, 335.053,
                           0.9232]
    path_2: List[float] = [799.793, 266.957, 1.0, 799.793, 266.957, 1.0, 799.785, 266.912, 1.0, 799.767, 266.807, 1.0,
                           799.744, 266.672, 1.0, 799.683, 266.55, 1.0, 799.571, 266.459, 1.0101, 799.437, 266.399,
                           1.0432, 799.333, 266.56, 1.1013, 799.226, 267.524, 1.1772, 799.035, 269.949, 1.2575, 798.746,
                           273.998, 1.3308, 798.457, 279.154, 1.3905, 798.277, 284.647, 1.4409, 798.227, 289.96, 1.4936,
                           798.249, 295.031, 1.5582, 798.251, 300.044, 1.6316, 798.135, 305.044, 1.6998, 797.867,
                           309.734, 1.7488, 797.522, 313.576, 1.7754, 797.232, 316.139, 1.7874, 797.08, 317.381, 1.7983,
                           797.052, 317.658, 1.8188, 797.095, 317.448, 1.8513, 797.233, 316.963, 1.8884, 797.637,
                           316.05, 1.9194, 798.532, 314.375, 1.9381, 800.036, 311.742, 1.9456, 802.049, 308.294, 1.9462,
                           804.313, 304.546, 1.9448, 806.502, 301.151, 1.945, 808.361, 298.603, 1.9479, 809.801,
                           297.046, 1.9522, 810.935, 296.326, 1.9563, 811.968, 296.191, 1.9598, 813.057, 296.499,
                           1.9636, 814.152, 297.165, 1.9688, 815.082, 298.135, 1.9753, 815.681, 299.332, 1.9831,
                           815.924, 300.673, 1.9938, 815.857, 302.048, 2.009, 815.524, 303.342, 2.0283, 814.889,
                           304.465, 2.0486, 813.886, 305.37, 2.0663, 812.526, 306.065, 2.0794, 810.885, 306.629, 2.0859,
                           809.189, 307.146, 2.0852, 807.721, 307.622, 2.0788, 806.733, 307.982, 2.0693, 806.269,
                           308.168, 2.0549, 806.184, 308.272, 2.0281, 806.334, 308.546, 1.9895, 806.706, 309.235,
                           1.9513, 807.363, 310.397, 1.9294, 808.353, 311.956, 1.9301, 809.586, 313.713, 1.948, 810.966,
                           315.556, 1.9741, 812.521, 317.567, 2.0008, 814.264, 319.806, 2.0229, 816.136, 322.218,
                           2.0367, 818.01, 324.625, 2.044, 819.799, 326.867, 2.0508, 821.421, 328.813, 2.0635, 822.796,
                           330.371, 2.0837, 823.86, 331.476, 2.1095, 824.601, 332.138, 2.1395, 825.042, 332.435, 2.1718,
                           825.237, 332.502, 2.206, 825.268, 332.437, 2.2362, 825.229, 332.175, 2.1123, 825.186,
                           331.723, 1.7819, 825.165, 331.219, 1.3445, 825.163, 330.88, 1.0205, 825.166, 330.767, 0.8968,
                           825.166, 330.767, 0.8968]
    path_3: List[float] = [726.93, 264.871, 1.0, 726.93, 264.871, 1.0, 726.937, 264.856, 1.0, 726.954, 264.82, 1.0,
                           726.975, 264.774, 1.0, 726.991, 264.62, 1.0, 726.968, 264.327, 1.0067, 726.867, 263.975,
                           1.0248, 726.667, 263.786, 1.051, 726.398, 263.901, 1.0739, 726.14, 264.284, 1.0857, 725.968,
                           264.724, 1.0868, 725.955, 264.972, 1.096, 726.105, 264.857, 1.1311, 726.341, 264.41, 1.1942,
                           726.541, 263.857, 1.266, 726.602, 263.505, 1.3213, 726.494, 263.548, 1.3478, 726.287,
                           263.935, 1.3493, 726.094, 264.419, 1.3386, 726.027, 264.727, 1.3295, 726.126, 264.688,
                           1.3328, 726.336, 264.34, 1.3493, 726.547, 263.897, 1.3608, 726.698, 263.708, 1.3467, 726.854,
                           264.065, 1.3055, 727.208, 265.009, 1.2323, 727.774, 266.179, 1.1399, 728.363, 267.104,
                           1.0512, 728.732, 267.532, 0.996, 728.834, 267.567, 0.9791, 728.834, 267.567, 0.9791]

    # Create a spline object from the path data
    spline_0: Spline = Spline(layout_mask, path_0)
    spline_1: Spline = Spline(layout_mask, path_1)
    spline_2: Spline = Spline(layout_mask, path_2)
    spline_3: Spline = Spline(layout_mask, path_3)

    # Create some style
    style: Style = Style(brush_uri=vector_brush_0.name)
    style.path_point_properties.red = 1.0
    style.path_point_properties.green = 0.0
    style.path_point_properties.blue = 0.4
    style.path_point_properties.alpha = 1.0

    # Create a stroke object. Note that it just exists, but is not in the model yet.
    stroke_0: Stroke = Stroke(sid=UUIDIdentifier.id_generator(), spline=spline_0, style=style)
    stroke_1: Stroke = Stroke(sid=UUIDIdentifier.id_generator(), spline=spline_1, style=style)
    stroke_2: Stroke = Stroke(sid=UUIDIdentifier.id_generator(), spline=spline_2, style=style)
    stroke_3: Stroke = Stroke(sid=UUIDIdentifier.id_generator(), spline=spline_3, style=style)

    # First you need a root group to contain the strokes
    root: StrokeGroupNode = StrokeGroupNode(UUIDIdentifier.id_generator())

    # Assign the group as the root of the main ink tree
    ink_model.ink_tree = InkTree()
    ink_model.ink_tree.root = root

    # Add a node for stroke 0
    stroke_node_0: StrokeNode = StrokeNode(stroke_0)
    root.add(stroke_node_0)

    # Add a node for stroke 1
    stroke_node_1: StrokeNode = StrokeNode(stroke_1)
    root.add(stroke_node_1)

    # Add a node for stroke 2
    stroke_node_2: StrokeNode = StrokeNode(stroke_2)
    root.add(stroke_node_2)

    # Add a node for stroke 3
    stroke_node_3: StrokeNode = StrokeNode(stroke_3)
    root.add(stroke_node_3)

    # Adding view for handwriting recognition results
    hwr_tree: InkTree = InkTree(str(schema.CommonViews.HWR_VIEW.value))
    # Add view right after creation, to avoid warnings that tree is not yet attached
    ink_model.add_view(hwr_tree)

    hwr_root: StrokeGroupNode = StrokeGroupNode(UUIDIdentifier.id_generator())
    hwr_tree.root = hwr_root
    ink_model.knowledge_graph.append(schema.SemanticTriple(hwr_root.uri, schema.IS, 'will:seg/0.3/Root'))
    ink_model.knowledge_graph.append(schema.SemanticTriple(hwr_root.uri, schema.REPRESENTS_VIEW,
                                                           schema.CommonViews.HWR_VIEW.value))

    # Here you can add the same strokes as in the main tree, but you can organize them in a different way
    # (put them in different groups)
    # You are not supposed to add strokes that are not already in the main tree.
    text_region: StrokeGroupNode = StrokeGroupNode(UUIDIdentifier.id_generator())
    hwr_root.add(text_region)
    ink_model.knowledge_graph.append(schema.SemanticTriple(text_region.uri, schema.IS, schema.TEXT_REGION))

    # The text_line root denotes the text line
    text_line: StrokeGroupNode = StrokeGroupNode(UUIDIdentifier.id_generator())
    text_region.add(text_line)
    ink_model.knowledge_graph.append(schema.SemanticTriple(text_line.uri, schema.IS, schema.TEXT_LINE))

    # The word node denotes a word
    word: StrokeGroupNode = StrokeGroupNode(UUIDIdentifier.id_generator())
    text_line.add(word)
    ink_model.knowledge_graph.append(schema.SemanticTriple(word.uri, schema.IS, schema.WORD))
    ink_model.knowledge_graph.append(schema.SemanticTriple(word.uri, schema.HAS_CONTENT, "ink"))
    ink_model.knowledge_graph.append(schema.SemanticTriple(word.uri, schema.HAS_LANGUAGE, "en_US"))
    word.add(StrokeNode(stroke_0))
    word.add(StrokeNode(stroke_1))
    word.add(StrokeNode(stroke_2))
    word.add(StrokeNode(stroke_3))

    # We need a URI builder
    uri_builder: URIBuilder = URIBuilder()

    # Create a named entity
    named_entity_uri: str = uri_builder.build_named_entity_uri(UUIDIdentifier.id_generator())
    ink_model.knowledge_graph.append(schema.SemanticTriple(word.uri, schema.PART_OF_NAMED_ENTITY, named_entity_uri))

    # Add knowledge for the named entity
    ink_model.knowledge_graph.append(schema.SemanticTriple(named_entity_uri, "hasPart-0", word.uri))
    ink_model.knowledge_graph.append(schema.SemanticTriple(named_entity_uri, schema.HAS_LABEL, "Ink"))
    ink_model.knowledge_graph.append(schema.SemanticTriple(named_entity_uri, schema.HAS_LANGUAGE, "en_US"))
    ink_model.knowledge_graph.append(schema.SemanticTriple(named_entity_uri, schema.HAS_CONFIDENCE, "0.95"))
    ink_model.knowledge_graph.append(schema.SemanticTriple(named_entity_uri, schema.HAS_ARTICLE_URL,
                                                    'https://en.wikipedia.org/wiki/Ink'))
    ink_model.knowledge_graph.append(schema.SemanticTriple(named_entity_uri, schema.HAS_UNIQUE_ID, 'Q127418'))
    # Save the model, this will overwrite an existing file
    with io.open('3_1_0_vector.uim', 'wb') as uim:
        # unicode(data) auto-decodes data to unicode if str
        uim.write(UIMEncoder310().encode(ink_model))

```

Find the sample, [here](https://github.com/Wacom-Developer/universal-ink-library/blob/main/samples/sample_create_model.py)

# Web Demos
The following web demos can be used to produce Universal Ink Model files: 

- [Universal Ink Model Viewer](https://universal-ink.wacom.com/) - producing UIM 3.1.0 files,
- [WILL SDK for ink - Demo](https://will3-web-ink-demo.azurewebsites.net/) - producing UIM 3.1.0 files.


# Documentation
You can find more detailed technical documentation, [here](https://developer-docs.wacom.com/sdk-for-ink/docs/model).
API documentation is available [here](docs/uim/index.html).

# Usage

The library is used for machine learning experiments based on digital ink using the Universal Ink Model. 

# Contributing
Contribution guidelines are still work in progress.

# License
[Apache License 2.0](LICENSE)

