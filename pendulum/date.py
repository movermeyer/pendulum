import calendar
import math
import pendulum

from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from .period import Period
from .formatting.difference_formatter import DifferenceFormatter
from .mixins.default import FormattableMixing
from .constants import (
    DAYS_PER_WEEK, YEARS_PER_DECADE, YEARS_PER_CENTURY,
    MONTHS_PER_YEAR,
    MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY
)
from .exceptions import DateTimeException


class Date(FormattableMixing, date):

    # Names of days of the week
    _days = {
        SUNDAY: 'Sunday',
        MONDAY: 'Monday',
        TUESDAY: 'Tuesday',
        WEDNESDAY: 'Wednesday',
        THURSDAY: 'Thursday',
        FRIDAY: 'Friday',
        SATURDAY: 'Saturday'
    }

    _MODIFIERS_VALID_UNITS = [
        'day', 'week', 'month', 'year', 'decade', 'century'
    ]

    _diff_formatter = None

    @classmethod
    def instance(cls, dt):
        """
        Return a new Date instance given a native date instance.

        :param dt: The native date instance.
        :type dt: date

        :rtype: Date
        """
        if not isinstance(dt, date):
            raise ValueError('instance() only accepts date objects')

        return cls(dt.year, dt.month, dt.day)

    @classmethod
    def create(cls, year=None, month=None, day=None):
        """
        Create a new Date instance from a specific date.

        If any of year, month or day are set to None their today() values will
        be used.

        :type year: int
        :type month: int
        :type day: int

        :rtype: Date
        """
        if any([year is None, month is None, day is None]):
            now = date.today()

            if year is None:
                year = now.year

            if month is None:
                month = now.month

            if day is None:
                day = now.day

        return cls(year, month, day)

    @classmethod
    def today(cls, tz=None):
        """
        Create a Date instance for today.

        :param tz: The timezone
        :type tz: Timezone or TimezoneInfo or str or None

        :rtype: Date
        """
        if pendulum.has_test_now():
            now = pendulum.get_test_now()

            return now.date()

        return cls.create()

    @classmethod
    def yesterday(cls):
        return cls.today().subtract(days=1)

    @classmethod
    def tomorrow(cls):
        return cls.today().add(days=1)

    # Getters/Setters

    def set(self, year=None, month=None, day=None):
        return self.replace(
            year=year, month=month, day=day
        )

    @property
    def day_of_week(self):
        """
        Returns the day of the week (0-6).

        :rtype: int
        """
        return self.isoweekday() % 7

    @property
    def day_of_year(self):
        """
        Returns the day of the year (1-366).

        :rtype: int
        """
        k = 1 if self.is_leap_year() else 2

        return (
            (275 * self.month) // 9
            - k * ((self.month + 9) // 12)
            + self.day - 30
        )

    @property
    def week_of_year(self):
        return self.isocalendar()[1]

    @property
    def days_in_month(self):
        return calendar.monthrange(self.year, self.month)[1]

    @property
    def week_of_month(self):
        return int(math.ceil(self.day / DAYS_PER_WEEK))

    @property
    def age(self):
        return self.diff().in_years()

    @property
    def quarter(self):
        return int(math.ceil(self.month / 3))

    # String Formatting

    def to_date_string(self):
        """
        Format the instance as date.

        :rtype: str
        """
        return self.strftime('%Y-%m-%d')

    def to_formatted_date_string(self):
        """
        Format the instance as a readable date.

        :rtype: str
        """
        return self.strftime('%b %d, %Y')

    def __repr__(self):
        return (
            f'{self.__class__.__name__}('
            f'{self.year}, {self.month}, {self.day}'
            f')'
        )

    # COMPARISONS

    def closest(self, dt1, dt2):
        """
        Get the closest date from the instance.

        :type dt1: Date or date
        :type dt2: Date or date

        :rtype: Date
        """
        dt1 = self.instance(dt1)
        dt2 = self.instance(dt2)

        if self.diff(dt1).in_seconds() < self.diff(dt2).in_seconds():
            return dt1

        return dt2

    def farthest(self, dt1, dt2):
        """
        Get the farthest date from the instance.

        :type dt1: Date or date
        :type dt2: Date or date

        :rtype: Date
        """
        dt1 = self.instance(dt1)
        dt2 = self.instance(dt2)

        if self.diff(dt1).in_seconds() > self.diff(dt2).in_seconds():
            return dt1

        return dt2

    def is_future(self):
        """
        Determines if the instance is in the future, ie. greater than now.

        :rtype: bool
        """
        return self > self.today()

    def is_past(self):
        """
        Determines if the instance is in the past, ie. less than now.

        :rtype: bool
        """
        return self < self.today()

    def is_leap_year(self):
        """
        Determines if the instance is a leap year.

        :rtype: bool
        """
        return calendar.isleap(self.year)

    def is_long_year(self):
        """
        Determines if the instance is a long year

        See link `<https://en.wikipedia.org/wiki/ISO_8601#Week_dates>`_

        :rtype: bool
        """
        return Date(self.year, 12, 28).isocalendar()[1] == 53

    def is_same_day(self, dt):
        """
        Checks if the passed in date is the same day as the instance current day.

        :type dt: Date or date

        :rtype: bool
        """
        return self == dt

    def is_birthday(self, dt=None):
        """
        Check if its the birthday. Compares the date/month values of the two dates.

        :rtype: bool
        """
        if dt is None:
            dt = Date.today()

        instance = self.instance(dt)

        return (self.month, self.day) == (instance.month, instance.day)

    # ADDITIONS AND SUBSTRACTIONS

    def add(self, years=0, months=0, weeks=0, days=0):
        """
        Add duration to the instance.

        :param years: The number of years
        :type years: int

        :param months: The number of months
        :type months: int

        :param weeks: The number of weeks
        :type weeks: int

        :param days: The number of days
        :type days: int

        :rtype: Date
        """
        delta = relativedelta(
            years=years,
            months=months,
            weeks=weeks,
            days=days,
        )

        return self.instance(date(self.year, self.month, self.day) + delta)

    def subtract(self, years=0, months=0, weeks=0, days=0):
        """
        Remove duration from the instance.

        :param years: The number of years
        :type years: int

        :param months: The number of months
        :type months: int

        :param weeks: The number of weeks
        :type weeks: int

        :param days: The number of days
        :type days: int

        :rtype: Date
        """
        delta = relativedelta(
            years=years,
            months=months,
            weeks=weeks,
            days=days
        )

        return self.instance(date(self.year, self.month, self.day) - delta)

    def _add_timedelta(self, delta):
        """
        Add timedelta duration to the instance.

        :param delta: The timedelta instance
        :type delta: pendulum.Duration or datetime.timedelta

        :rtype: Date
        """
        if isinstance(delta, pendulum.duration):
            return self.add(
                years=delta.years,
                months=delta.months,
                weeks=delta.weeks,
                days=delta.remaining_days
            )

        return self.add(days=delta.days)

    def _subtract_timedelta(self, delta):
        """
        Remove timedelta duration from the instance.

        :param delta: The timedelta instance
        :type delta: pendulum.Duration or datetime.timedelta

        :rtype: Date
        """
        if isinstance(delta, pendulum.duration):
            return self.subtract(
                years=delta.years,
                months=delta.months,
                weeks=delta.weeks,
                days=delta.remaining_days
            )

        return self.subtract(days=delta.days)

    def __add__(self, other):
        if not isinstance(other, timedelta):
            return NotImplemented

        return self._add_timedelta(other)

    def __sub__(self, other):
        if isinstance(other, timedelta):
            return self._subtract_timedelta(other)

        try:
            return self.instance(other).diff(self, False)
        except ValueError:
            return NotImplemented

    # DIFFERENCES

    @property
    def diff_formatter(self):
        """
        Returns a DifferenceFormatter instance.

        :rtype: DifferenceFormatter
        """
        if not self.__class__._diff_formatter:
            self.__class__._diff_formatter = DifferenceFormatter(pendulum.translator())

        return self.__class__._diff_formatter

    def diff(self, dt=None, abs=True):
        """
        Returns the difference between two Date objects as a Period.

        :type dt: Date or None

        :param abs: Whether to return an absolute interval or not
        :type abs: bool

        :rtype: Period
        """
        if dt is None:
            dt = self.today()

        return Period(self, self.instance(dt), absolute=abs)

    def diff_for_humans(self, other=None, absolute=False, locale=None):
        """
        Get the difference in a human readable format in the current locale.

        When comparing a value in the past to default now:
        1 day ago
        5 months ago

        When comparing a value in the future to default now:
        1 day from now
        5 months from now

        When comparing a value in the past to another value:
        1 day before
        5 months before

        When comparing a value in the future to another value:
        1 day after
        5 months after

        :type other: Date

        :param absolute: removes time difference modifiers ago, after, etc
        :type absolute: bool

        :param locale: The locale to use for localization
        :type locale: str

        :rtype: str
        """
        return self.diff_formatter.diff_for_humans(self, other, absolute, locale)

    # MODIFIERS

    def start_of(self, unit):
        """
        Returns a copy of the instance with the time reset
        with the following rules:

        * day: time to 00:00:00
        * week: date to first day of the week and time to 00:00:00
        * month: date to first day of the month and time to 00:00:00
        * year: date to first day of the year and time to 00:00:00
        * decade: date to first day of the decade and time to 00:00:00
        * century: date to first day of century and time to 00:00:00

        :param unit: The unit to reset to
        :type unit: str

        :rtype: Date
        """
        if unit not in self._MODIFIERS_VALID_UNITS:
            raise ValueError('Invalid unit "{}" for start_of()'.format(unit))

        return getattr(self, '_start_of_{}'.format(unit))()

    def end_of(self, unit):
        """
        Returns a copy of the instance with the time reset
        with the following rules:

        * week: date to last day of the week
        * month: date to last day of the month
        * year: date to last day of the year
        * decade: date to last day of the decade
        * century: date to last day of century

        :param unit: The unit to reset to
        :type unit: str

        :rtype: Date
        """
        if unit not in self._MODIFIERS_VALID_UNITS:
            raise ValueError('Invalid unit "%s" for end_of()' % unit)

        return getattr(self, '_end_of_%s' % unit)()

    def _start_of_day(self):
        """
        Compatibility method.

        :rtype: Date
        """
        return self

    def _end_of_day(self):
        """
        Compatibility method

        :rtype: Date
        """
        return self

    def _start_of_month(self):
        """
        Reset the date to the first day of the month.

        :rtype: Date
        """
        return self.set(self.year, self.month, 1)

    def _end_of_month(self):
        """
        Reset the date to the last day of the month.

        :rtype: Date
        """
        return self.set(
            self.year, self.month, self.days_in_month
        )

    def _start_of_year(self):
        """
        Reset the date to the first day of the year.

        :rtype: Date
        """
        return self.set(self.year, 1, 1)

    def _end_of_year(self):
        """
        Reset the date to the last day of the year.

        :rtype: Date
        """
        return self.set(self.year, 12, 31)

    def _start_of_decade(self):
        """
        Reset the date to the first day of the decade.

        :rtype: Date
        """
        year = self.year - self.year % YEARS_PER_DECADE

        return self.set(year, 1, 1)

    def _end_of_decade(self):
        """
        Reset the date to the last day of the decade.

        :rtype: Date
        """
        year = self.year - self.year % YEARS_PER_DECADE + YEARS_PER_DECADE - 1

        return self.set(year, 12, 31)

    def _start_of_century(self):
        """
        Reset the date to the first day of the century.

        :rtype: Date
        """
        year = self.year - 1 - (self.year - 1) % YEARS_PER_CENTURY + 1

        return self.set(year, 1, 1)

    def _end_of_century(self):
        """
        Reset the date to the last day of the century.

        :rtype: Date
        """
        year = self.year - 1 - (self.year - 1) % YEARS_PER_CENTURY + YEARS_PER_CENTURY

        return self.set(year, 12, 31)

    def _start_of_week(self):
        """
        Reset the date to the first day of the week.

        :rtype: Date
        """
        dt = self

        if self.day_of_week != pendulum._WEEK_STARTS_AT:
            dt = self.previous(pendulum._WEEK_STARTS_AT)

        return dt.start_of('day')

    def _end_of_week(self):
        """
        Reset the date to the last day of the week.

        :rtype: Date
        """
        dt = self

        if self.day_of_week != pendulum._WEEK_ENDS_AT:
            dt = self.next(pendulum._WEEK_ENDS_AT)

        return dt.end_of('day')

    def next(self, day_of_week=None):
        """
        Modify to the next occurrence of a given day of the week.
        If no day_of_week is provided, modify to the next occurrence
        of the current day of the week.  Use the supplied consts
        to indicate the desired day_of_week, ex. pendulum.MONDAY.

        :param day_of_week: The next day of week to reset to.
        :type day_of_week: int or None

        :rtype: Date
        """
        if day_of_week is None:
            day_of_week = self.day_of_week

        if day_of_week < SUNDAY or day_of_week > SATURDAY:
            raise ValueError('Invalid day of week')

        dt = self.add(days=1)
        while dt.day_of_week != day_of_week:
            dt = dt.add(days=1)

        return dt

    def previous(self, day_of_week=None):
        """
        Modify to the previous occurrence of a given day of the week.
        If no day_of_week is provided, modify to the previous occurrence
        of the current day of the week.  Use the supplied consts
        to indicate the desired day_of_week, ex. pendulum.MONDAY.

        :param day_of_week: The previous day of week to reset to.
        :type day_of_week: int or None

        :rtype: Date
        """
        if day_of_week is None:
            day_of_week = self.day_of_week

        if day_of_week < SUNDAY or day_of_week > SATURDAY:
            raise ValueError('Invalid day of week')

        dt = self.subtract(days=1)
        while dt.day_of_week != day_of_week:
            dt = dt.subtract(days=1)

        return dt

    def first_of(self, unit, day_of_week=None):
        """
        Returns an instance set to the first occurrence
        of a given day of the week in the current unit.
        If no day_of_week is provided, modify to the first day of the unit.
        Use the supplied consts to indicate the desired day_of_week, ex. pendulum.MONDAY.

        Supported units are month, quarter and year.

        :param unit: The unit to use
        :type unit: str

        :type day_of_week: int or None

        :rtype: Date
        """
        if unit not in ['month', 'quarter', 'year']:
            raise ValueError('Invalid unit "{}" for first_of()'.format(unit))

        return getattr(self, '_first_of_{}'.format(unit))(day_of_week)

    def last_of(self, unit, day_of_week=None):
        """
        Returns an instance set to the last occurrence
        of a given day of the week in the current unit.
        If no day_of_week is provided, modify to the last day of the unit.
        Use the supplied consts to indicate the desired day_of_week, ex. pendulum.MONDAY.

        Supported units are month, quarter and year.

        :param unit: The unit to use
        :type unit: str

        :type day_of_week: int or None

        :rtype: Date
        """
        if unit not in ['month', 'quarter', 'year']:
            raise ValueError('Invalid unit "{}" for first_of()'.format(unit))

        return getattr(self, '_last_of_{}'.format(unit))(day_of_week)

    def nth_of(self, unit, nth, day_of_week):
        """
        Returns a new instance set to the given occurrence
        of a given day of the week in the current unit.
        If the calculated occurrence is outside the scope of the current unit,
        then raise an error. Use the supplied consts
        to indicate the desired day_of_week, ex. pendulum.MONDAY.

        Supported units are month, quarter and year.

        :param unit: The unit to use
        :type unit: str

        :type nth: int

        :type day_of_week: int or None

        :rtype: Date
        """
        if unit not in ['month', 'quarter', 'year']:
            raise ValueError('Invalid unit "{}" for first_of()'.format(unit))

        dt = getattr(self, '_nth_of_{}'.format(unit))(nth, day_of_week)
        if dt is False:
            raise DateTimeException('Unable to find occurence {} of {} in {}'.format(
                                     nth, self._days[day_of_week], unit))

        return dt

    def _first_of_month(self, day_of_week):
        """
        Modify to the first occurrence of a given day of the week
        in the current month. If no day_of_week is provided,
        modify to the first day of the month. Use the supplied consts
        to indicate the desired day_of_week, ex. pendulum.MONDAY.

        :type day_of_week: int

        :rtype: Date
        """
        dt = self

        if day_of_week is None:
            return dt.set(day=1)

        month = calendar.monthcalendar(dt.year, dt.month)

        calendar_day = (day_of_week - 1) % 7

        if month[0][calendar_day] > 0:
            day_of_month = month[0][calendar_day]
        else:
            day_of_month = month[1][calendar_day]

        return dt.set(day=day_of_month)

    def _last_of_month(self, day_of_week=None):
        """
        Modify to the last occurrence of a given day of the week
        in the current month. If no day_of_week is provided,
        modify to the last day of the month. Use the supplied consts
        to indicate the desired day_of_week, ex. pendulum.MONDAY.

        :type day_of_week: int or None

        :rtype: Date
        """
        dt = self

        if day_of_week is None:
            return dt.set(day=self.days_in_month)

        month = calendar.monthcalendar(dt.year, dt.month)

        calendar_day = (day_of_week - 1) % 7

        if month[-1][calendar_day] > 0:
            day_of_month = month[-1][calendar_day]
        else:
            day_of_month = month[-2][calendar_day]

        return dt.set(day=day_of_month)

    def _nth_of_month(self, nth, day_of_week):
        """
        Modify to the given occurrence of a given day of the week
        in the current month. If the calculated occurrence is outside,
        the scope of the current month, then return False and no
        modifications are made. Use the supplied consts
        to indicate the desired day_of_week, ex. pendulum.MONDAY.

        :type nth: int

        :type day_of_week: int or None

        :rtype: Date
        """
        if nth == 1:
            return self.first_of('month', day_of_week)

        dt = self.first_of('month')
        check = dt.format('YYYY-MM')
        for i in range(nth - (1 if dt.day_of_week == day_of_week else 0)):
            dt = dt.next(day_of_week)

        if dt.format('YYYY-MM') == check:
            return self.set(day=dt.day)

        return False

    def _first_of_quarter(self, day_of_week=None):
        """
        Modify to the first occurrence of a given day of the week
        in the current quarter. If no day_of_week is provided,
        modify to the first day of the quarter. Use the supplied consts
        to indicate the desired day_of_week, ex. pendulum.MONDAY.

        :type day_of_week: int or None

        :rtype: Date
        """
        return self.set(self.year, self.quarter * 3 - 2, 1).first_of('month', day_of_week)

    def _last_of_quarter(self, day_of_week=None):
        """
        Modify to the last occurrence of a given day of the week
        in the current quarter. If no day_of_week is provided,
        modify to the last day of the quarter. Use the supplied consts
        to indicate the desired day_of_week, ex. pendulum.MONDAY.

        :type day_of_week: int or None

        :rtype: Date
        """
        return self.set(self.year, self.quarter * 3, 1).last_of('month', day_of_week)

    def _nth_of_quarter(self, nth, day_of_week):
        """
        Modify to the given occurrence of a given day of the week
        in the current quarter. If the calculated occurrence is outside,
        the scope of the current quarter, then return False and no
        modifications are made. Use the supplied consts
        to indicate the desired day_of_week, ex. pendulum.MONDAY.

        :type nth: int

        :type day_of_week: int or None

        :rtype: Date
        """
        if nth == 1:
            return self.first_of('quarter', day_of_week)

        dt = self.replace(self.year, self.quarter * 3, 1)
        last_month = dt.month
        year = dt.year
        dt = dt.first_of('quarter')
        for i in range(nth - (1 if dt.day_of_week == day_of_week else 0)):
            dt = dt.next(day_of_week)

        if last_month < dt.month or year != dt.year:
            return False

        return self.set(self.year, dt.month, dt.day)

    def _first_of_year(self, day_of_week=None):
        """
        Modify to the first occurrence of a given day of the week
        in the current year. If no day_of_week is provided,
        modify to the first day of the year. Use the supplied consts
        to indicate the desired day_of_week, ex. pendulum.MONDAY.

        :type day_of_week: int or None

        :rtype: Date
        """
        return self.set(month=1).first_of('month', day_of_week)

    def _last_of_year(self, day_of_week=None):
        """
        Modify to the last occurrence of a given day of the week
        in the current year. If no day_of_week is provided,
        modify to the last day of the year. Use the supplied consts
        to indicate the desired day_of_week, ex. pendulum.MONDAY.

        :type day_of_week: int or None

        :rtype: Date
        """
        return self.set(month=MONTHS_PER_YEAR).last_of('month', day_of_week)

    def _nth_of_year(self, nth, day_of_week):
        """
        Modify to the given occurrence of a given day of the week
        in the current year. If the calculated occurrence is outside,
        the scope of the current year, then return False and no
        modifications are made. Use the supplied consts
        to indicate the desired day_of_week, ex. pendulum.MONDAY.

        :type nth: int

        :type day_of_week: int or None

        :rtype: Date
        """
        if nth == 1:
            return self.first_of('year', day_of_week)

        dt = self.first_of('year')
        year = dt.year
        for i in range(nth - (1 if dt.day_of_week == day_of_week else 0)):
            dt = dt.next(day_of_week)

        if year != dt.year:
            return False

        return self.set(self.year, dt.month, dt.day)

    def average(self, dt=None):
        """
        Modify the current instance to the average
        of a given instance (default now) and the current instance.

        :type dt: Date or date

        :rtype: Date
        """
        if dt is None:
            dt = Date.today()

        return self.add(days=int(self.diff(dt, False).in_days() / 2))

    # Native methods override

    @classmethod
    def fromtimestamp(cls, t):
        return cls.instance(super(Date, cls).fromtimestamp(t))

    @classmethod
    def fromordinal(cls, n):
        return cls.instance(super(Date, cls).fromordinal(n))

    def replace(self, year=None, month=None, day=None):
        year = year if year is not None else self.year
        month = month if month is not None else self.month
        day = day if day is not None else self.day

        return self.__class__(year, month, day)
