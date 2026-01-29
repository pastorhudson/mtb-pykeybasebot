import os
from pprint import pprint

from pirateweather import forecast
from datetime import date, timedelta



def get_weather(name="Uniontown PA", LATLONG=(39.90008, -79.71643)):
    msg = ""
    weekday = date.today()

    with forecast(os.environ.get('PIRATE_WEATHER'), *LATLONG) as place:
        msg += f"{name}: {place.daily.summary}\n"
        msg += "```\n"
        days_to_show = 2
        current_day = 0
        for day in place.daily:
            day = dict(day=date.strftime(weekday, '%a'),
                       sum=day.summary,
                       tempMin=day.temperatureMin,
                       tempMax=day.temperatureMax
                       )
            msg +='{day}: {tempMin}°F - {tempMax}°F {sum}\n'.format(**day)
            weekday += timedelta(days=1)
            if current_day >= days_to_show:
                break
            current_day += 1
    msg += "```"

    return msg



if __name__ == '__main__':
    LATLONG = 39.90008, -79.71643
    print(get_weather("Uniontown", (39.90008, -79.71643)))
