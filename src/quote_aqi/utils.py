from datetime import datetime, timedelta


def floor_datetime(dt: datetime, interval: timedelta) -> datetime:
    """
    Round a datetime down to the nearest interval (floor).

    :param dt: The datetime to round down.
    :param interval: The interval to round down to.
    :return: The rounded datetime.
    """
    timestamp = dt.timestamp()
    interval_seconds = interval.total_seconds()
    floored_timestamp = (timestamp // interval_seconds) * interval_seconds
    return datetime.fromtimestamp(floored_timestamp, tz=dt.tzinfo)


def floor_hour(dt: datetime) -> datetime:
    return floor_datetime(dt, timedelta(hours=1))


def floor_half_hour(dt: datetime) -> datetime:
    return floor_datetime(dt, timedelta(minutes=30))


def round_datetime(dt: datetime, interval: timedelta) -> datetime:
    """
    Round a datetime to the nearest interval.

    :param dt: The datetime to round.
    :param interval: The interval to round to.
    :return: The rounded datetime.
    """
    timestamp = dt.timestamp()
    interval_seconds = interval.total_seconds()
    rounded_timestamp = round(timestamp / interval_seconds) * interval_seconds
    return datetime.fromtimestamp(rounded_timestamp, tz=dt.tzinfo)


def round_hour(dt: datetime) -> datetime:
    return round_datetime(dt, timedelta(hours=1))


def round_half_hour(dt: datetime) -> datetime:
    return round_datetime(dt, timedelta(minutes=30))


def draw_text_psd_style(draw, xy, text, font, tracking=0, leading=None, **kwargs):
    """
    usage: draw_text_psd_style(draw, (0, 0), "Test",
                tracking=-0.1, leading=32, fill="Blue")

    Leading is measured from the baseline of one line of text to the
    baseline of the line above it. Baseline is the invisible line on which most
    letters—that is, those without descenders—sit. The default auto-leading
    option sets the leading at 120% of the type size (for example, 12‑point
    leading for 10‑point type).

    Tracking is measured in 1/1000 em, a unit of measure that is relative to
    the current type size. In a 6 point font, 1 em equals 6 points;
    in a 10 point font, 1 em equals 10 points. Tracking
    is strictly proportional to the current type size.
    """

    def stutter_chunk(lst, size, overlap=0, default=None):
        for i in range(0, len(lst), size - overlap):
            r = list(lst[i : i + size])
            while len(r) < size:
                r.append(default)
            yield r

    x, y = xy
    font_size = font.size
    lines = text.splitlines()
    if leading is None:
        leading = font.size * 1.2
    for line in lines:
        for a, b in stutter_chunk(line, 2, 1, " "):
            w = font.getlength(a + b) - font.getlength(b)
            # dprint("[debug] kwargs")
            print("[debug] kwargs:{}".format(kwargs))

            draw.text((x, y), a, font=font, **kwargs)
            x += w + (tracking / 1000) * font_size
        y += leading
        x = xy[0]
