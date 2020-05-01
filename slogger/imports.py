from slogger.models import SleepPhase, Child

from openpyxl import load_workbook
from datetime import datetime, timedelta, time

class RawSleepPhase:
    def __init__(self, date=None, starttime=None, endtime=None):
        if not date or not starttime or not endtime:
            raise ValueError("Invalid date/time input!")

        d = str(date.date())

        start = datetime.fromisoformat(d + " " + str(starttime))
        end = datetime.fromisoformat(d + " " + str(endtime))

        if start > end:
            end += timedelta(days=1)

        self.date = date
        self.starttime = start
        self.endtime = end
    
    def __str__(self):
        d = "%02i:%02i" % (self.duration()/3600, self.duration()%3600/60)
        return "%s: From %s to %s. Duration: %s." % (self.date.date(), self.starttime, self.endtime, d)
    
    def duration(self):
        return (self.endtime - self.starttime).total_seconds()

class WorkbookReader:
    def __init__(self, filename):
        self._workbook = load_workbook(filename=filename, data_only=True)

    def read_data(self):
        phases = []
        last_date = None

        for cell in self._workbook.active:
            date, start, end = cell[0].value, cell[1].value, cell[2].value

            if date:
                last_date = date

            if not start or not end:
                print(f"Invalid data: {cell}. ignoring line.")
                continue

            phases.append(RawSleepPhase(last_date, start, end))
        
        return phases

def import_xlsx(filename, child_id):
    w = WorkbookReader(filename)
    data = w.read_data()
    
    for d in data:
        s = SleepPhase()
        s.child = Child.objects.get(id=child_id)
        s.dt = d.starttime
        s.dt_end = d.endtime
        s.save()