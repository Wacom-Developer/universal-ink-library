# -*- coding: utf-8 -*-
# Copyright © 2024-present Wacom Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
import base64
import pathlib
from io import BytesIO
from pathlib import Path
from typing import Union, Dict, Optional

from lxml import etree
from lxml.etree import Element

from uim.codec.parser.base import Parser, FormatException
from uim.codec.parser.inkml import InkMLParser
from uim.model.ink import InkModel


class IOTPaperParser(Parser):
    """
    IOTPaperParser
    ==============
    Parser for IOT Paper format.
    The format encodes the ink as InkML, but additionally it encodes a template image as base64.

    ```xml
    <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <paper xmlns:inkml="http://www.w3.org/2003/InkML"
           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           xsi:schemaLocation="http://www.w3.org/2003/InkML">
        <resource>
            <templateImage Content-Type="image/bmp">
                <!-- Base64 encoded template -->
            </templateImage>
        </resource>
        <inkml:ink>
            <!-- Ink content encoded as InkML -->
        </inkml:ink>
    </paper>
    ```

    """
    def parse(self, path_or_stream: Union[str, bytes, memoryview, BytesIO, Path]) -> InkModel:
        """
        Parse the content of the ink file to the Universal Ink memory model.

        Parameters
        ----------
        path_or_stream: Union[str, bytes, memoryview, BytesIO, Path]
            `Path` of file, path as str, stream, or byte array.

        Returns
        -------
           model - `InkModel`
               Parsed `InkModel` from UIM encoded stream
        """
        ink_parser: InkMLParser = InkMLParser()
        ink_parser.cropping_ink = False
        if isinstance(path_or_stream, (str, pathlib.Path)):
            # It's a file path
            with open(path_or_stream, 'r') as inkml_file:
                buffer = inkml_file.read()
        else:
            # It's a buffer
            if isinstance(path_or_stream, (bytes, memoryview)):
                path_or_stream = BytesIO(path_or_stream)

            buffer = path_or_stream.read()
        parser: etree.XMLParser = etree.XMLParser(recover=True)
        if isinstance(buffer, str):
            root: Element = etree.fromstring(buffer.encode(), parser)
        else:
            root: Element = etree.fromstring(buffer, parser)

        namespaces: Dict[str, str] = {'inkml': 'http://www.w3.org/2003/InkML'}

        inkml_element: Optional[Element] = root.find('.//inkml:ink', namespaces)
        if inkml_element is not None:
            # Step 3: Convert the InkML subtree to a string
            inkml_string: str = etree.tostring(inkml_element, encoding='unicode')
            ink_model = ink_parser.parse(inkml_string.encode('utf-8'))
            return ink_model
        raise FormatException("The IOT paper format contains no ink data")

    @staticmethod
    def parse_template(path_or_stream: Union[str, bytes, memoryview, BytesIO, Path]) -> bytes:
        """
        Parse the template image from the IOT paper format.

        Parameters
        ----------
        path_or_stream: Union[str, bytes, memoryview, BytesIO, Path]
            `Path` of file, path as str, stream, or byte array.

        Returns
        -------
           image_content - bytes
               Template content bytes encoded as BMP from the IOT paper format
        """
        if isinstance(path_or_stream, (str, pathlib.Path)):
            # It's a file path
            with open(path_or_stream, 'r') as inkml_file:
                buffer = inkml_file.read()
        else:
            # It's a buffer
            if isinstance(path_or_stream, (bytes, memoryview)):
                path_or_stream = BytesIO(path_or_stream)

            buffer = path_or_stream.read()
        parser: etree.XMLParser = etree.XMLParser(recover=True)
        if isinstance(buffer, str):
            root: Element = etree.fromstring(buffer.encode(), parser)
        else:
            root: Element = etree.fromstring(buffer, parser)
        template_image_element: Optional[Element] = root.find('.//templateImage')

        if template_image_element is not None:
            base64_image_string = template_image_element.text.strip()  # Extract and strip whitespace
            # Decode the base64 string
            image_data = base64.b64decode(base64_image_string)
            # Load the binary data into a BytesIO object
            image_io = BytesIO(image_data)
            return image_io.read()
        raise FormatException("The IOT paper format contains no ink data")
