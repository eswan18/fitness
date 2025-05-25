Various analysis of workout data.

I have two sources:
1. MapMyFitness: Historically I have tracked most of my runs with this app, and I still track my treadmill runs with it. However, I no longer use it for outdoor runs.
2. Strava: Starting in June 2024, I use Strava to track my outdoor runs.

## Getting the data: MapMyRun

Download by logging into mapmyfitness and then going to https://www.mapmyfitness.com/workout/export/csv.


## Getting the data: Strava

This data is pulled in automatically via the Strava API -- you'll just be prompted to authorize the app on startup.

## Running the API

todo

## Testing

Run unit tests with `make test`.

Run *all* tests, including integration tests, with `make all-test`.
This requires authorizing Strava.
