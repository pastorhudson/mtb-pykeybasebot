import os
from pirateweather import forecast
from datetime import date, timedelta


def get_weather(name, LATLONG):
    weekday = date.today()
    with forecast(os.environ.get('PIRATE_WEATHER'), *LATLONG) as place:
        print(f"{name}n: {place.daily.summary}\n---\n")
        for day in place.daily:
            day = dict(day=date.strftime(weekday, '%a'),
                       sum=day.summary,
                       tempMin=day.temperatureMin,
                       tempMax=day.temperatureMax
                       )
            print('{day}: {sum} Temp range: {tempMin} - {tempMax}'.format(**day))
            weekday += timedelta(days=1)


if __name__ == '__main__':
    LATLONG = 39.90008, -79.71643
    get_weather("Uniontown", (39.90008, -79.71643))
