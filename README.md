Various analysis of workout data.

I have two sources:
1. MapMyFitness: Historically I have tracked most of my runs with this app, and I still track my treadmill runs with it. However, I no longer use it for outdoor runs.
2. Strava: Starting in June 2024, I use Strava to track my outdoor runs.

## Getting the data: MapMyRun

Download by logging into mapmyfitness and then going to https://www.mapmyfitness.com/workout/export/csv.


## Getting the data: Strava

Log in to strava.com.
Go to the settings page.

Navigate to the My Account tab in the sidebar.
Scroll to the bottom of the page, to the heading **Download or Delete Your Account**.
Click **Get Started**.

On that page, find the **Download Request** heading and click the **Request Your Archive** button.
The data will be emailed to you.

## Running the dashboard

Start the dashboard with `poetry run streamlit run dashboard.py --mmf-data data/user82388963_workout_history.csv --strava-data data/strava/activities.csv`.
Obviously you may need to update those file paths.
