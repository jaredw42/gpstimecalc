#!/usr/bin/env python3
from datetime import datetime, timedelta, timezone
import sys

# constants
CALENDAR_DAY_FORMAT = "'%Y-%m-%d'"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S%z"


class GpsTime:

    # constants
    GPS_EPOCH = "1980-01-06 00:00:00+00:00"
    MICROSEC_TO_SEC = 1e-6
    MILLISEC_TO_SEC = 1e-3
    DAYS_IN_WEEK = 7
    SECONDS_IN_DAY = 86400

    # dict containing leap second values using dates as keys
    # Leap second calendar taken from this website:
    # https://www.ptb.de/cms/en/ptb/fachabteilungen/abt4/fb-44/ag-441/realisation-of-legal-time-in-germany/leap-seconds.html
    LEAP_SECONDS = {
        "2017-01-01 00:00:00+00:00": 18,
        "2015-07-01 00:00:00+00:00": 17,
        "2012-07-01 00:00:00+00:00": 16,
        "2009-01-01 00:00:00+00:00": 15,
        "2006-01-01 00:00:00+00:00": 14,
        "1999-01-01 00:00:00+00:00": 13,
        "1997-07-01 00:00:00+00:00": 12,
        "1996-01-01 00:00:00+00:00": 11,
        "1994-07-01 00:00:00+00:00": 10,
        "1993-07-01 00:00:00+00:00": 9,
        "1992-07-01 00:00:00+00:00": 8,
        "1991-01-01 00:00:00+00:00": 7,
        "1990-01-01 00:00:00+00:00": 6,
        "1988-01-01 00:00:00+00:00": 5,
        "1985-07-01 00:00:00+00:00": 4,
        "1983-07-01 00:00:00+00:00": 3,
        "1982-07-01 00:00:00+00:00": 2,
        "1981-07-01 00:00:00+00:00": 1,
        GPS_EPOCH: 0,
    }

    def __init__(self, utc):

        self.gpstimefromutc(utc)

    def gpstimefromutc(self, utc):

        """
        Find the given leap second for a date, then calculate the GPS week number and seconds into week for a given UTC datetime
        """

        self.leap_seconds = self.get_leap_seconds(utc)

        gps_epoch = datetime.strptime(self.GPS_EPOCH, DATETIME_FORMAT)
        tdiff = utc - gps_epoch + timedelta(seconds=self.leap_seconds)
        self.gps_week = tdiff.days // self.DAYS_IN_WEEK
        days_into_week = tdiff.days - (self.gps_week * self.DAYS_IN_WEEK)
        self.gps_seconds_into_week = (
            tdiff.seconds + (self.SECONDS_IN_DAY * days_into_week) + (tdiff.microseconds * self.MICROSEC_TO_SEC)
        )

    def get_leap_seconds(self, utc):
        ls_datetimes = sorted([datetime.strptime(x, DATETIME_FORMAT) for x in self.LEAP_SECONDS.keys()])
        if utc > ls_datetimes[-1]:
            leapsec = self.LEAP_SECONDS[(str(ls_datetimes[-1]))]
            print(
                f"Date {datetime.strftime(utc, '%Y-%m-%d')} exceeds last leap second addition date of {ls_datetimes[-1]}. Leap seconds set to {leapsec}"
            )
        elif utc < ls_datetimes[0]:

            return leapsec
        prev_lsd = ls_datetimes[0]
        for lsd in ls_datetimes:
            if lsd > utc:
                leapsec = self.LEAP_SECONDS[str(prev_lsd)]
                print(f"There were {leapsec} leap seconds after {datetime.strftime(prev_lsd, '%Y-%m-%d')}")
                return leapsec

            prev_lsd = lsd


def timecalc():
    """
    converts UTC datetimes to GPS weeks and seconds
    accepts UTC epoch time or UTC datetime in format  "%Y-%m-%d %H:%M:%S"
    """
    print("timecalc started.\n")

    if len(sys.argv) == 1:
        print(
            "Timecalc called without arguments. Using device local time.\nTo specify another time, enter a UTC datetime in format %YYYY-%mm-%dd %H:%M:%S or Unix epoch time in ms."
        )
        dt = datetime.now(timezone.utc)

    elif len(sys.argv) == 2:
        print("single input argument, assuming this is a UTC epoch timestamp in ms")
        dt = int(sys.argv[1])
        dt = datetime.utcfromtimestamp(dt * GpsTime.MSEC_TO_SEC)
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        if ":" in sys.argv[2]:
            dt = sys.argv[1] + " " + sys.argv[2]
            dt = datetime.strptime(dt, DATETIME_FORMAT)
        else:
            print("timecalc requires time in either UTC epoch time or datetime in {}".format(DATETIME_FORMAT))
            raise ValueError("UTC datetime needs to be {}".format(DATETIME_FORMAT))

    gpstime = GpsTime(dt)

    print(f"UTC DATETIME: {dt} \nGPS WEEK: {gpstime.gps_week}, TOW: {gpstime.gps_seconds_into_week:.2f}")


if __name__ == "__main__":

    timecalc()
