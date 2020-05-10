from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone as tz
from urllib import request

from slogger.models import Percentile

def import_percentiles(type, gender, data):
    if type == "lhfa":
        t = "LH"
    elif type == "wfa":
        t = "W"
    else:
        raise ValueError("Invalid measurement type: " + str(type))

    if gender == "girls":
        g = "F"
    elif gender == "boys":
        g = "M"

    dt = tz.now()

    for row in data.split("\r\n")[1:]:
        r = row.split("\t")

        if len(r) == 1:
            continue

        p = Percentile()
        p.dt = dt
        p.gender = g
        p.m_type = t
        p.day  = r[0]
        p.p01  = r[4]
        p.p1   = r[5]
        p.p3   = r[6]
        p.p5   = r[7]
        p.p10  = r[8]
        p.p15  = r[9]
        p.p25  = r[10]
        p.p50  = r[11]
        p.p75  = r[12]
        p.p85  = r[13]
        p.p90  = r[14]
        p.p95  = r[15]
        p.p97  = r[16]
        p.p99  = r[17]
        p.p999 = r[18]
        p.save()

class Command(BaseCommand):
    help = 'Loads percentile data from the WHO website and inserts it to the DB.'

    URLS=(
        "https://www.who.int/childgrowth/standards/lhfa_boys_p_exp.txt",
        "https://www.who.int/childgrowth/standards/lhfa_girls_p_exp.txt",
        "https://www.who.int/childgrowth/standards/wfa_boys_p_exp.txt",
        "https://www.who.int/childgrowth/standards/wfa_girls_p_exp.txt",
    )

    def handle(self, *args, **options):
        for url in Command.URLS:
            fname = url.split("/")[-1].split("_")
            with request.urlopen(url) as response:
                data = response.read()
                import_percentiles(fname[0], fname[1], data.decode('ascii'))