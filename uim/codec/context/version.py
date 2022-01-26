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
from typing import Any


class Version(object):
    """
    Version encodes the semantic versioning concept a version number MAJOR.MINOR.PATCH, increment the:

    Parameters
    ----------
    major: int
        Major encodes the MAJOR version number. This number is incremented when you make incompatible API changes.
    minor: int
        Minor encodes the MINOR version number. This number is incremented when you add functionality in a backwards
        compatible manner.
    patch: int
        Patch encodes the version number. This number is incremented when you make backwards compatible bug fixes.
    ink_format: str
        String that defines the identifier string for the format that is related to the version.

    References
    ----------
    .. [1] Semantic Versioning 2.0.0 URL https://semver.org/
    """

    def __init__(self, major: int, minor: int, patch: int, ink_format: str = 'Unknown'):
        self.__major: int = major
        self.__minor: int = minor
        self.__patch: int = patch
        self.__ink_format: str = ink_format

    @property
    def ink_format(self) -> str:
        """Version is associated to this format. (`str`)"""
        return self.__ink_format

    @property
    def major(self) -> int:
        """MAJOR version. (`int`)"""
        return self.__major

    @property
    def minor(self) -> int:
        """MINOR version.  (`int`)"""
        return self.__minor

    @property
    def patch(self) -> int:
        """PATCH version. (`int`)"""
        return self.__patch

    def __eq__(self, other: Any):
        """Overrides the default implementation"""
        if isinstance(other, Version):
            return self.major == other.major and self.minor == other.minor and self.patch == other.patch \
                   and self.ink_format == other.ink_format
        return False

    def __repr__(self):
        return f'Version: {self.ink_format} {self.major}.{self.minor}.{self.patch} ({self.ink_format})'
