2024/07/29 - RELEASE 2.0.2
==========================
- Minor improvements in the UIM model avoiding None exception, when iterating empty model
- Rename constant 

2024/07/24 - RELEASE 2.0.1
==========================
- Setting default transformation matrix to identity matrix if not provided in the UIM model
- Refactor the schema constants for different schemas


2024/07/12 - RELEASE 2.0.0
==========================
- Refactor schema handling in uim.model.semantics.schema package
- Support __eq__ for all classes in uim.model package, to enable comparison of UIM models
- Fixing several bugs in parsing of UIM files
- Improve API documentation
- Adding serialization to JSON file for human readable UIM model representation
- Adding helper function to create csv file from sensor data


2023/09/11 - RELEASE 1.1.0
==========================
- Fix: Azimuth and Altitude values are now correctly set in the UIM model
- Rename syntax package to schema and using new naming convention for the schema
- Add a analysis package to provide a set of functions to analyze the UIM model

2022/10/7 - RELEASE 1.0.6
==========================
Minor fix: 
Set protobuf dependency to fixed tested version number

2022/04/6 - RELEASE 1.0.5
==========================
Helper function:
- Adding a remove node function

Samples:
- Adding an additional sample to produce a valid UIM 3.1.0 vector file

2022/01/26 - RELEASE 1.0.4
==========================
Minor bug fix:
- WILL 2.0 File format files have been falsely identified as WILL data files.

2021/08/18 - RELEASE 1.0.2
==========================
First public release.