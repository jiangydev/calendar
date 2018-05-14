# encoding: utf-8

from datetime import datetime

class WeekdayCal():
    '''
    Calculate the relative time distance between two time
    in the form of weekday
    '''

    def __init__(self, timeStr):
        '''
        init the object
        :param timeStr: time string of start time in form of " %Y-%m-%d"
            e.g.: '2018-2-26'
        '''
        try:
            self.starttime = datetime.strptime(timeStr, '%Y-%m-%d')
        except ValueError:
            raise ValueError('form error, excepted %Y-%m-%d, but got {}.'.format(timeStr))


    def getWeekday(self, timeStr_compare):
        """
        calculate relative time distance from the start time

        :param timeStr_compare: time string of time to be calculated,
        in form of "%Y-%m-%d", e.g. '2018-5-12'

        :return: { 'week': [int]week, 'weekday': [int] weekday }
        the time inputted is the [week](e.g. 2nd) week and
        [weekday](1 to 7, for 1 means Monday, and 7 means Sunday)
        from the start time
        """
        try:
            self.comparetime = datetime.strptime(timeStr_compare, '%Y-%m-%d')
        except ValueError:
            raise ValueError('form error, excepted %Y-%m-%d, but got {}.'.format(timeStr_compare))

        seconds = (self.comparetime - self.starttime).total_seconds()
        day = seconds//(60*60*24)+1 # after 15.6 days, in the 16th day
        week = day//7+1             # after 2.5 weeks, in the 3nd week
        weekday = (day % 7) or 7          # in the 16th day, in Monday

        return {
            'week': int(week),
            'weekday': int(weekday)
        }

if __name__ == '__main__':
    calculator = WeekdayCal('2018-2-26')
    weektime = calculator.getWeekday('2018-5-12')
    print('week: {0}, weekday: {1}'.format(weektime['week'], weektime['weekday']))

