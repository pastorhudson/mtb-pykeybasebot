import os
from pirateweather import forecast
from datetime import date, timedelta


def get_weather(name, LATLONG):
    msg = ""
    weekday = date.today()
    with forecast(os.environ.get('PIRATE_WEATHER'), *LATLONG) as place:
        msg += f"{name}n: {place.daily.summary}\n---\n"
        for day in place.daily:
            day = dict(day=date.strftime(weekday, '%a'),
                       sum=day.summary,
                       tempMin=day.temperatureMin,
                       tempMax=day.temperatureMax
                       )
            msg +='{day}: {sum} Temp range: {tempMin} - {tempMax}\n'.format(**day)
            weekday += timedelta(days=1)
    return msg


if __name__ == '__main__':
    LATLONG = 39.90008, -79.71643
    print(get_weather("Uniontown", (39.90008, -79.71643)))
