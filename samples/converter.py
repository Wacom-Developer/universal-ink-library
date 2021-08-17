#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2021 Wacom Authors. All Rights Reserved.
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
import argparse
import io
import logging
import math
import os
import sys
from pathlib import Path
from timeit import default_timer as timer
from typing import List, Optional

import uim.codec.parser.will as p_will
import uim.codec.parser.uim as p_uim
import uim.codec.writer.encoder.encoder_3_1_0 as f_uim_3_1_0

import uim.model.inkinput.inputdata as device
from uim.codec.base import FileExtension

# Logger
from uim.codec.parser.base import FormatException
from uim.model.ink import InkModel

# Export types
UIM_3_1_0_BINARY: str = 'uim_3_1_0-binary'
UIM_3_0_0_BINARY: str = 'uim_3_0_0-binary'
UIM_3_0_0_JSON: str = 'uim_3_0_0-json'
EXPORT_FORMATS: list = [UIM_3_0_0_JSON, UIM_3_0_0_BINARY, UIM_3_1_0_BINARY]
# Logger
logger = None


if __name__ == '__main__':
    val = device.virtual_resolution_for_si_unit(device.Unit.MM)
    # create logger with ''
    logger = logging.getLogger('converter')
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler('conversion.log')
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    parser = argparse.ArgumentParser(description='Conversion script to convert input data codec to another.')
    parser.add_argument("-p", "--path", help="Path to input data files")
    parser.add_argument("-o", "--out", help="Output directory")
    parser.add_argument("-f", "--codec",
                        choices=EXPORT_FORMATS,
                        help="Conversion codec."
                        "[options: uim_3_0_0-json|uim_3_0_0-binary|uim_3_1_0-binary|all].")

    args = parser.parse_args()

    logger.info("Input path: " + os.path.join(os.getcwd(), args.path))
    logger.info("Output path: " + os.path.join(os.getcwd(), args.out))

    # Setting the export codec
    if args.codec is None:
        export_format: str = "uim_3_1_0-binary"
    else:
        export_format: str = args.codec.lower()

    export_jobs: list = []
    if export_format.lower() == 'all':
        export_jobs.extend(EXPORT_FORMATS)
    elif export_format not in EXPORT_FORMATS:
        logger.error("Export codec: {} not supported.".format(args.format))
        sys.exit(-1)
    else:
        export_jobs.append(export_format)

    if args.path is None:
        logger.error("Import path must be defined.")
        sys.exit(-1)

    if args.out is None:
        logger.error("Export path must be defined.")
        sys.exit(-1)

    # Configured paths
    input_path: Path = Path(args.path)
    output_path: Path = Path(args.out)

    # Create output directories
    output_path.mkdir(parents=True, exist_ok=True)

    manufactures = []
    models = []
    # Parser
    will_parser: p_will.WILL2Parser = p_will.WILL2Parser()
    uim_parser: p_uim.UIMParser = p_uim.UIMParser()
    # Writer
    uim_formatter_3_1: f_uim_3_1_0.UIMEncoder310 = f_uim_3_1_0.UIMEncoder310()

    jobs: List[Path] = []
    # Collect export jobs
    if input_path.is_dir():
        jobs.extend([f for f in input_path.iterdir()])
    else:
        jobs.append(input_path)
    # Iterate over jobs
    for file in jobs:
        ink_model: Optional[InkModel] = None
        logger.info(f"Loading ink file: {file.name}")
        try:
            t1: float = timer()
            # ------------------------------------------ Parser --------------------------------------------------------
            if file.name.lower().endswith(FileExtension.WILL_FORMAT_EXTENSION):
                try:
                    ink_model = will_parser.parse(file)
                except FormatException as e:
                    logger.error(e)
            elif file.name.lower().endswith(FileExtension.UIM_BINARY_FORMAT_EXTENSION):
                ink_model = uim_parser.parse(file)
            elif file.name.lower().endswith(FileExtension.UIM_JSON_FORMAT_EXTENSION):
                ink_model = uim_parser.parse_json(file)
            t2: float = timer()
            # ----------------------------------------------------------------------------------------------------------
            if ink_model is None:
                logger.debug(f"Ignore: {file.name}")
                continue
            # ------------------------------------------ Export --------------------------------------------------------
            for export_type in export_jobs:
                t3: float = timer()
                ink_data = None
                export_filename = None

                if export_type == UIM_3_1_0_BINARY:
                    ink_data = uim_formatter_3_1.encode(ink_model)
                    export_filename = file.stem + FileExtension.UIM_BINARY_FORMAT_EXTENSION
                t4: float = timer()
                if ink_data is not None:
                    with io.open(os.path.join(output_path, export_filename), 'wb') as ink_out_file:
                        # unicode(data) auto-decodes data to unicode if str
                        ink_out_file.write(ink_data)
                    logger.info(" [PARSING TIME]: {} ms".format(int((t2 - t1) * 1000)))
                    logger.info(" [FORMATTING]:  {} ms".format(int((t4 - t3) * 1000)))
                    logger.info(" [FILE SIZE]:  {} kB".format(int(math.ceil(len(ink_data) / 1000))))

        except UnicodeDecodeError as e:
            logger.error("Parsing of {} failed. [exception:={}]".format(file.name, e))
            continue
