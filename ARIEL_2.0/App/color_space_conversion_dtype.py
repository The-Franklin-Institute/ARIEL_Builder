# taken from the image processing section of the scikits library
# https://github.com/scikits-image/scikits-image/blob/master/skimage/util/dtype.py

#LICENSE:

"""Copyright (C) 2011, the scikits-image team
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

 1. Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.
 2. Redistributions in binary form must reproduce the above copyright
    notice, this list of conditions and the following disclaimer in
    the documentation and/or other materials provided with the
    distribution.
 3. Neither the name of skimage nor the names of its contributors may be
    used to endorse or promote products derived from this software without
    specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT,
INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE."""

from __future__ import division
import numpy as np

__all__ = ['img_as_float', 'img_as_int', 'img_as_uint', 'img_as_ubyte',
           'img_as_bool']

# from .. import get_log
# log = get_log('dtype_converter')

dtype_range = {np.bool_: (False, True),
               np.bool8: (False, True),
               np.uint8: (0, 255),
               np.uint16: (0, 65535),
               np.int8: (-128, 127),
               np.int16: (-32768, 32767),
               np.float32: (-1, 1),
               np.float64: (-1, 1)}

integer_types = (np.uint8, np.uint16, np.int8, np.int16)

_supported_types = (np.bool_, np.bool8,
                    np.uint8, np.uint16, np.uint32,
                    np.int8, np.int16, np.int32,
                    np.float32, np.float64)

if np.__version__ >= "1.6.0":
    dtype_range[np.float16] = (-1, 1)
    _supported_types += (np.float16, )


def convert(image, dtype, force_copy=False, uniform=False):
    """
    Convert an image to the requested data-type.

    Warnings are issued in case of precision loss, or when negative values
    are clipped during conversion to unsigned integer types (sign loss).

    Floating point values are expected to be normalized and will be clipped
    to the range [0.0, 1.0] or [-1.0, 1.0] when converting to unsigned or
    signed integers respectively.

    Numbers are not shifted to the negative side when converting from
    unsigned to signed integer types. Negative values will be clipped when
    converting to unsigned integers.

    Parameters
    ----------
    image : ndarray
        Input image.
    dtype : dtype
        Target data-type.
    force_copy : bool
        Force a copy of the data, irrespective of its current dtype.
    uniform : bool
        Uniformly quantize the floating point range to the integer range.
        By default (uniform=False) floating point values are scaled and
        rounded to the nearest integers, which minimizes back and forth
        conversion errors.

    References
    ----------
    (1) DirectX data conversion rules.
        http://msdn.microsoft.com/en-us/library/windows/desktop/dd607323%28v=vs.85%29.aspx
    (2) Data Conversions.
        In "OpenGL ES 2.0 Specification v2.0.25", pp 7-8. Khronos Group, 2010.
    (3) Proper treatment of pixels as integers. A.W. Paeth.
        In "Graphics Gems I", pp 249-256. Morgan Kaufmann, 1990.
    (4) Dirty Pixels. J. Blinn.
        In "Jim Blinn's corner: Dirty Pixels", pp 47-57. Morgan Kaufmann, 1998.

    """
    image = np.asarray(image)
    dtypeobj = np.dtype(dtype)
    dtypeobj_in = image.dtype
    dtype = dtypeobj.type
    dtype_in = dtypeobj_in.type

    if dtype_in == dtype:
        if force_copy:
            image = image.copy()
        return image

    if not (dtype_in in _supported_types and dtype in _supported_types):
        raise ValueError("can not convert %s to %s." % (dtypeobj_in, dtypeobj))

    def sign_loss():
        log.warn("Possible sign loss when converting negative image of type "
                 "%s to positive image of type %s." % (dtypeobj_in, dtypeobj))

    def prec_loss():
        log.warn("Possible precision loss when converting from "
                 "%s to %s" % (dtypeobj_in, dtypeobj))

    def _dtype(itemsize, *dtypes):
        # Return first of `dtypes` with itemsize greater than `itemsize`
        return next(dt for dt in dtypes if itemsize < np.dtype(dt).itemsize)

    def _dtype2(kind, bits, itemsize=1):
        # Return dtype of `kind` that can store a `bits` wide unsigned int
        c = lambda x, y: x <= y if kind == 'u' else x < y
        s = next(i for i in (itemsize, ) + (2, 4, 8) if c(bits, i * 8))
        return np.dtype(kind + str(s))

    def _scale(a, n, m, copy=True):
        # Scale unsigned/positive integers from n to m bits
        # Numbers can be represented exactly only if m is a multiple of n
        # Output array is of same kind as input.
        kind = a.dtype.kind
        if n == m:
            return a.copy() if copy else a
        elif n > m:
            # downscale with precision loss
            prec_loss()
            if copy:
                b = np.empty(a.shape, _dtype2(kind, m))
                np.floor_divide(a, 2**(n - m), out=b, dtype=a.dtype,
                                casting='unsafe')
                return b
            else:
                a //= 2**(n - m)
                return a
        elif m % n == 0:
            # exact upscale to a multiple of n bits
            if copy:
                b = np.empty(a.shape, _dtype2(kind, m))
                np.multiply(a, (2**m - 1) // (2**n - 1), out=b, dtype=b.dtype)
                return b
            else:
                a = np.array(a, _dtype2(kind, m, a.dtype.itemsize), copy=False)
                a *= (2**m - 1) // (2**n - 1)
                return a
        else:
            # upscale to a multiple of n bits,
            # then downscale with precision loss
            prec_loss()
            o = (m // n + 1) * n
            if copy:
                b = np.empty(a.shape, _dtype2(kind, o))
                np.multiply(a, (2**o - 1) // (2**n - 1), out=b, dtype=b.dtype)
                b //= 2**(o - m)
                return b
            else:
                a = np.array(a, _dtype2(kind, o, a.dtype.itemsize), copy=False)
                a *= (2**o - 1) // (2**n - 1)
                a //= 2**(o - m)
                return a

    kind = dtypeobj.kind
    kind_in = dtypeobj_in.kind
    itemsize = dtypeobj.itemsize
    itemsize_in = dtypeobj_in.itemsize

    if kind == 'b' or kind_in == 'b':
        return dtype(image)

    if kind in 'ui':
        imin = np.iinfo(dtype).min
        imax = np.iinfo(dtype).max
    if kind_in in 'ui':
        imin_in = np.iinfo(dtype_in).min
        imax_in = np.iinfo(dtype_in).max

    if kind_in == 'f':
        if np.min(image) < -1.0 or np.max(image) > 1.0:
            raise ValueError("Images of type float must be between -1 and 1.")
        if kind == 'f':
            # floating point -> floating point
            if itemsize_in > itemsize:
                prec_loss()
            return dtype(image)

        # floating point -> integer
        prec_loss()
        # use float type that can represent output integer type
        image = np.array(image, _dtype(itemsize, dtype_in,
                                       np.float32, np.float64))
        if not uniform:
            if kind == 'u':
                image *= imax
            else:
                image *= imax - imin
                image -= 1.0
                image /= 2.0
            np.rint(image, out=image)
            np.clip(image, imin, imax, out=image)
        elif kind == 'u':
            image *= imax + 1
            np.clip(image, 0, imax, out=image)
        else:
            image *= (imax - imin + 1.0) / 2.0
            np.floor(image, out=image)
            np.clip(image, imin, imax, out=image)
        return dtype(image)

    if kind == 'f':
        # integer -> floating point
        if itemsize_in >= itemsize:
            prec_loss()
        # use float type that can exactly represent input integers
        image = np.array(image, _dtype(itemsize_in, dtype,
                                       np.float32, np.float64))
        if kind_in == 'u':
            image /= imax_in
            # DirectX uses this conversion also for signed ints
            #if imin_in:
            #    np.maximum(image, -1.0, out=image)
        else:
            image *= 2.0
            image += 1.0
            image /= imax_in - imin_in
        return dtype(image)

    if kind_in == 'u':
        if kind == 'i':
            # unsigned integer -> signed integer
            image = _scale(image, 8 * itemsize_in, 8 * itemsize - 1)
            return image.view(dtype)
        else:
            # unsigned integer -> unsigned integer
            return _scale(image, 8 * itemsize_in, 8 * itemsize)

    if kind == 'u':
        # signed integer -> unsigned integer
        sign_loss()
        image = _scale(image, 8 * itemsize_in - 1, 8 * itemsize)
        result = np.empty(image.shape, dtype)
        np.maximum(image, 0, out=result, dtype=image.dtype, casting='unsafe')
        return result

    # signed integer -> signed integer
    if itemsize_in > itemsize:
        return _scale(image, 8 * itemsize_in - 1, 8 * itemsize - 1)
    image = image.astype(_dtype2('i', itemsize * 8))
    image -= imin_in
    image = _scale(image, 8 * itemsize_in, 8 * itemsize, copy=False)
    image += imin
    return dtype(image)


def img_as_float(image, force_copy=False):
    """Convert an image to double-precision floating point format.

    Parameters
    ----------
    image : ndarray
        Input image.
    force_copy : bool
        Force a copy of the data, irrespective of its current dtype.

    Returns
    -------
    out : ndarray of float64
        Output image.

    Notes
    -----
    The range of a floating point image is [0, 1].
    Negative input values will be shifted to the positive domain.

    """
    return convert(image, np.float64, force_copy)


def img_as_uint(image, force_copy=False):
    """Convert an image to 16-bit unsigned integer format.

    Parameters
    ----------
    image : ndarray
        Input image.
    force_copy : bool
        Force a copy of the data, irrespective of its current dtype.

    Returns
    -------
    out : ndarray of uint16
        Output image.

    Notes
    -----
    Negative input values will be shifted to the positive domain.

    """
    return convert(image, np.uint16, force_copy)


def img_as_int(image, force_copy=False):
    """Convert an image to 16-bit signed integer format.

    Parameters
    ----------
    image : ndarray
        Input image.
    force_copy : bool
        Force a copy of the data, irrespective of its current dtype.

    Returns
    -------
    out : ndarray of uint16
        Output image.

    Notes
    -----
    If the input data-type is positive-only (e.g., uint8), then
    the output image will still only have positive values.

    """
    return convert(image, np.int16, force_copy)


def img_as_ubyte(image, force_copy=False):
    """Convert an image to 8-bit unsigned integer format.

    Parameters
    ----------
    image : ndarray
        Input image.
    force_copy : bool
        Force a copy of the data, irrespective of its current dtype.

    Returns
    -------
    out : ndarray of ubyte (uint8)
        Output image.

    Notes
    -----
    If the input data-type is positive-only (e.g., uint16), then
    the output image will still only have positive values.

    """
    return convert(image, np.uint8, force_copy)


def img_as_bool(image, force_copy=False):
    """Convert an image to boolean format.

    Parameters
    ----------
    image : ndarray
        Input image.
    force_copy : bool
        Force a copy of the data, irrespective of its current dtype.

    Returns
    -------
    out : ndarray of bool (bool_)
        Output image.

    Notes
    -----
    All non-zero elements are treated as True.

    """
    return convert(image, np.bool_, force_copy)