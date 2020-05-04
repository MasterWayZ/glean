# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import datetime
import sys
from typing import List, Optional


from .. import _ffi
from .._dispatcher import Dispatcher
from ..testing import ErrorType


from .lifetime import Lifetime
from .timeunit import TimeUnit


if sys.version_info < (3, 7):
    import iso8601  # type: ignore
else:
    iso8601 = None


class DatetimeMetricType:
    """
    This implements the developer facing API for recording datetime metrics.

    Instances of this class type are automatically generated by
    `glean.load_metrics`, allowing developers to record values that were
    previously registered in the metrics.yaml file.

    The datetime API only exposes the `DatetimeMetricType.set` method.
    """

    def __init__(
        self,
        disabled: bool,
        category: str,
        lifetime: Lifetime,
        name: str,
        send_in_pings: List[str],
        time_unit: TimeUnit,
    ):
        self._disabled = disabled
        self._send_in_pings = send_in_pings

        self._handle = _ffi.lib.glean_new_datetime_metric(
            _ffi.ffi_encode_string(category),
            _ffi.ffi_encode_string(name),
            _ffi.ffi_encode_vec_string(send_in_pings),
            len(send_in_pings),
            lifetime.value,
            disabled,
            time_unit.value,
        )

    def __del__(self):
        if getattr(self, "_handle", 0) != 0:
            _ffi.lib.glean_destroy_datetime_metric(self._handle)

    def set(self, value: Optional[datetime.datetime] = None):
        """
        Set a datetime value, truncating it to the metric's resolution.

        Args:
            value (datetime.datetime): (default: now) The `datetime.datetime`
                value to set. If not provided, will record the current time.
        """
        if self._disabled:
            return

        if value is None:
            value = datetime.datetime.now()

        @Dispatcher.launch
        def set():
            tzinfo = value.tzinfo
            if tzinfo is not None:
                offset = tzinfo.utcoffset(value).seconds
            else:
                offset = 0
            _ffi.lib.glean_datetime_set(
                self._handle,
                value.year,
                value.month,
                value.day,
                value.hour,
                value.minute,
                value.second,
                value.microsecond * 1000,
                offset,
            )

    def test_has_value(self, ping_name: Optional[str] = None) -> bool:
        """
        Tests whether a value is stored for the metric for testing purposes
        only.

        Args:
            ping_name (str): (default: first value in send_in_pings) The name
                of the ping to retrieve the metric for.

        Returns:
            has_value (bool): True if the metric value exists.
        """
        if ping_name is None:
            ping_name = self._send_in_pings[0]

        return bool(
            _ffi.lib.glean_datetime_test_has_value(
                self._handle, _ffi.ffi_encode_string(ping_name)
            )
        )

    def test_get_value_as_str(self, ping_name: Optional[str] = None) -> str:
        """
        Returns the stored value for testing purposes only, as an ISO8601 string.

        Args:
            ping_name (str): (default: first value in send_in_pings) The name
                of the ping to retrieve the metric for.

        Returns:
            value (str): value of the stored metric.
        """
        if ping_name is None:
            ping_name = self._send_in_pings[0]

        if not self.test_has_value(ping_name):
            raise ValueError("metric has no value")

        return _ffi.ffi_decode_string(
            _ffi.lib.glean_datetime_test_get_value_as_string(
                self._handle, _ffi.ffi_encode_string(ping_name)
            )
        )

    def test_get_value(self, ping_name: Optional[str] = None) -> datetime.datetime:
        """
        Returns the stored value for testing purposes only.

        Args:
            ping_name (str): (default: first value in send_in_pings) The name
                of the ping to retrieve the metric for.

        Returns:
            value (datetime.datetime): value of the stored metric.
        """
        if sys.version_info < (3, 7):
            return iso8601.parse_date(self.test_get_value_as_str(ping_name))
        else:
            return datetime.datetime.fromisoformat(
                self.test_get_value_as_str(ping_name)
            )

    def test_get_num_recorded_errors(
        self, error_type: ErrorType, ping_name: Optional[str] = None
    ) -> int:
        """
        Returns the number of errors recorded for the given metric.

        Args:
            error_type (ErrorType): The type of error recorded.
            ping_name (str): (default: first value in send_in_pings) The name
                of the ping to retrieve the metric for.

        Returns:
            num_errors (int): The number of errors recorded for the metric for
                the given error type.
        """
        if ping_name is None:
            ping_name = self._send_in_pings[0]

        return _ffi.lib.glean_datetime_test_get_num_recorded_errors(
            self._handle, error_type.value, _ffi.ffi_encode_string(ping_name),
        )


__all__ = ["DatetimeMetricType"]
