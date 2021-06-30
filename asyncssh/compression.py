# Copyright (c) 2013-2021 by Ron Frederick <ronf@timeheart.net> and others.
#
# This program and the accompanying materials are made available under
# the terms of the Eclipse Public License v2.0 which accompanies this
# distribution and is available at:
#
#     http://www.eclipse.org/legal/epl-2.0/
#
# This program may also be made available under the following secondary
# licenses when the conditions for such availability set forth in the
# Eclipse Public License v2.0 are satisfied:
#
#    GNU General Public License, Version 2.0, or any later versions of
#    that license
#
# SPDX-License-Identifier: EPL-2.0 OR GPL-2.0-or-later
#
# Contributors:
#     Ron Frederick - initial implementation, API, and documentation

"""SSH compression handlers"""

import zlib
from typing import Any
from typing import Optional
from typing import List
from asyncssh.compression import _ZLibCompress
from asyncssh.compression import _ZLibDecompress


_cmp_algs = []
_default_cmp_algs = []

_cmp_params = {}

_cmp_compressors = {}
_cmp_decompressors = {}


def _none() -> Optional[Any]:
    """Compressor/decompressor for no compression."""

    return None


class _ZLibCompress:
    """Wrapper class to force a sync flush and handle exceptions"""

    def __init__(self) -> None:
        self._comp = zlib.compressobj()

    def compress(self, data: bytes) -> bytes:
        """Compress data using zlib compression with sync flush"""

        try:
            return self._comp.compress(data) + \
                   self._comp.flush(zlib.Z_SYNC_FLUSH)
        except zlib.error: # pragma: no cover
            return None


class _ZLibDecompress:
    """Wrapper class to handle exceptions"""

    def __init__(self) -> None:
        self._decomp = zlib.decompressobj()

    def decompress(self, data: bytes) -> bytes:
        """Decompress data using zlib compression"""

        try:
            return self._decomp.decompress(data)
        except zlib.error: # pragma: no cover
            return None


def register_compression_alg(alg, compressor, decompressor,
                             after_auth, default):
    """Register a compression algorithm"""

    _cmp_algs.append(alg)

    if default:
        _default_cmp_algs.append(alg)

    _cmp_params[alg] = after_auth

    _cmp_compressors[alg] = compressor
    _cmp_decompressors[alg] = decompressor


def get_compression_algs() -> List[bytes]:
    """Return supported compression algorithms"""

    return _cmp_algs


def get_default_compression_algs() -> List[bytes]:
    """Return default compression algorithms"""

    return _default_cmp_algs


def get_compression_params(alg: bytes) -> bool:
    """Get parameters of a compression algorithm

       This function returns whether or not a compression algorithm should
       be delayed until after authentication completes.

    """

    return _cmp_params[alg]


def get_compressor(alg: bytes) -> Optional[_ZLibCompress]:
    """Return an instance of a compressor

       This function returns an object that can be used for data compression.

    """

    return _cmp_compressors[alg]()


def get_decompressor(alg: bytes) -> Optional[_ZLibDecompress]:
    """Return an instance of a decompressor

       This function returns an object that can be used for data decompression.

    """

    return _cmp_decompressors[alg]()

register_compression_alg(b'zlib@openssh.com',
                         _ZLibCompress, _ZLibDecompress, True,  True)
register_compression_alg(b'zlib',
                         _ZLibCompress, _ZLibDecompress, False, False)
register_compression_alg(b'none',
                         _none,         _none,           False, True)
