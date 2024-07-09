Various analysis of workout data.

I have two sources:
1. MapMyFitness: Historically I have tracked most of my runs with this app, and I still track my treadmill runs with it. However, I no longer use it for outdoor runs.
2. Strava: Starting in June 2024, I use Strava to track my outdoor runs.

## Getting the data: MapMyRun

Download by logging into mapmyfitness and then going to https://www.mapmyfitness.com/workout/export/csv.


## Getting the data: Strava

This data is pulled in automatically via the Strava API -- you'll just be prompted to authorize the app on startup.

## Running the dashboard

Start the dashboard with `poetry run streamlit run dashboard.py data/user82388963_workout_history.csv`.
Obviously you may need to update those file paths.
