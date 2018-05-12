# encoding: utf-8

from datetime import datetime

class WeekdayCal():
    def __init__(self, timeStr):
        try:
            self.starttime = datetime.strptime(timeStr, '%Y-%m-%d')
        except ValueError:
            raise ValueError('form error, excepted %Y-%m-%d, but got {}.'.format(timeStr))

    def getWeekday(self, timeStr_compare):
        try:
            self.comparetime = datetime.strptime(timeStr_compare, '%Y-%m-%d')
        except ValueError:
            raise ValueError('form error, excepted %Y-%m-%d, but got {}.'.format(timeStr_compare))

        seconds = (self.comparetime - self.starttime).total_seconds()
        day = seconds//(60*60*24)+1 # after 15.6 days, in the 16th day
        week = day//7+1             # after 2.5 weeks, in the 3nd week
        weekday = day % 7           # in the 16th day, in Monday

        return {
            'week': int(week),
            'weekday': int(weekday)
        }

if __name__ == '__main__':
    calculator = WeekdayCal('2018-2-26')
    weektime = calculator.getWeekday('2018-5-12')
    print('week: {0}, weekday: {1}'.format(weektime['week'], weektime['weekday']))

