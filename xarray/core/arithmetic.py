"""Base classes implementing arithmetic for xarray objects."""
import numbers

import numpy as np

# _typed_ops.py is a generated file
from ._typed_ops import (
    DataArrayGroupByOpsMixin,
    DataArrayOpsMixin,
    DatasetGroupByOpsMixin,
    DatasetOpsMixin,
    VariableOpsMixin,
)
from .common import ImplementsArrayReduce, ImplementsDatasetReduce
from .ops import IncludeCumMethods, IncludeNumpySameMethods, IncludeReduceMethods
from .options import OPTIONS, _get_keep_attrs
from .pycompat import dask_array_type


class SupportsArithmetic:
    """Base class for xarray types that support arithmetic.

    Used by Dataset, DataArray, Variable and GroupBy.
    """

    __slots__ = ()

    # TODO: implement special methods for arithmetic here rather than injecting
    # them in xarray/core/ops.py. Ideally, do so by inheriting from
    # numpy.lib.mixins.NDArrayOperatorsMixin.

    # TODO: allow extending this with some sort of registration system
    _HANDLED_TYPES = (
        np.ndarray,
        np.generic,
        numbers.Number,
        bytes,
        str,
    ) + dask_array_type

    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
        from .computation import apply_ufunc

        # See the docstring example for numpy.lib.mixins.NDArrayOperatorsMixin.
        out = kwargs.get("out", ())
        for x in inputs + out:
            if not isinstance(x, self._HANDLED_TYPES + (SupportsArithmetic,)):
                return NotImplemented

        if ufunc.signature is not None:
            raise NotImplementedError(
                "{} not supported: xarray objects do not directly implement "
                "generalized ufuncs. Instead, use xarray.apply_ufunc or "
                "explicitly convert to xarray objects to NumPy arrays "
                "(e.g., with `.values`).".format(ufunc)
            )

        if method != "__call__":
            # TODO: support other methods, e.g., reduce and accumulate.
            raise NotImplementedError(
                "{} method for ufunc {} is not implemented on xarray objects, "
                "which currently only support the __call__ method. As an "
                "alternative, consider explicitly converting xarray objects "
                "to NumPy arrays (e.g., with `.values`).".format(method, ufunc)
            )

        if any(isinstance(o, SupportsArithmetic) for o in out):
            # TODO: implement this with logic like _inplace_binary_op. This
            # will be necessary to use NDArrayOperatorsMixin.
            raise NotImplementedError(
                "xarray objects are not yet supported in the `out` argument "
                "for ufuncs. As an alternative, consider explicitly "
                "converting xarray objects to NumPy arrays (e.g., with "
                "`.values`)."
            )

        join = dataset_join = OPTIONS["arithmetic_join"]

        return apply_ufunc(
            ufunc,
            *inputs,
            input_core_dims=((),) * ufunc.nin,
            output_core_dims=((),) * ufunc.nout,
            join=join,
            dataset_join=dataset_join,
            dataset_fill_value=np.nan,
            kwargs=kwargs,
            dask="allowed",
            keep_attrs=_get_keep_attrs(default=True),
        )


class VariableArithmetic(
    ImplementsArrayReduce,
    IncludeReduceMethods,
    IncludeCumMethods,
    IncludeNumpySameMethods,
    SupportsArithmetic,
    VariableOpsMixin,
):
    __slots__ = ()
    # prioritize our operations over those of numpy.ndarray (priority=0)
    __array_priority__ = 50


class DatasetArithmetic(
    ImplementsDatasetReduce,
    IncludeCumMethods,
    SupportsArithmetic,
    DatasetOpsMixin,
):
    __slots__ = ()
    __array_priority__ = 50


class DataArrayArithmetic(
    ImplementsArrayReduce,
    IncludeCumMethods,
    IncludeNumpySameMethods,
    SupportsArithmetic,
    DataArrayOpsMixin,
):
    __slots__ = ()
    # priority must be higher than Variable to properly work with binary ufuncs
    __array_priority__ = 60


class DataArrayGroupbyArithmetic(
    SupportsArithmetic,
    DataArrayGroupByOpsMixin,
):
    __slots__ = ()


class DatasetGroupbyArithmetic(
    SupportsArithmetic,
    DatasetGroupByOpsMixin,
):
    __slots__ = ()


class CoarsenArithmetic(IncludeReduceMethods):
    __slots__ = ()
