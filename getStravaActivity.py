from stravaio import strava_oauth2
from stravaio import StravaIO
from dotenv import load_dotenv
from staticmap import StaticMap, CircleMarker, Line

import gpxpy
import gpxpy.gpx
import random

## TO DO:
## export some information about route
## maybe add in some local info

## load CLIENT ID AND SECRET FROM .env FILE
load_dotenv()

##using stravaio's built in oauth2 function
response = strava_oauth2()
client = StravaIO(response['access_token'])

list_activities = client.get_logged_in_athlete_activities(after='last month')
activity_shortlist = []
for a in list_activities:
    if a.type == 'Ride' and a.distance > 40000:
        activity_shortlist.append(a.to_dict())
choice = random.choice(activity_shortlist)
stream_dict = client.get_activity_streams(choice['id'], client.get_logged_in_athlete().id).to_dict()

## reverse lat and lng numbers for use in the staticmap library
lnglat_pairs = []
for lng,lat in zip(stream_dict['lng'], stream_dict['lat']):
    lnglat_pairs.append((lng, lat))


## using komoot's staticmap library
m = StaticMap(500, 500, 10)
marker = CircleMarker((choice['start_latlng'][1], choice['start_latlng'][0]), '#0036FF', 12)
for (index, lnglat) in enumerate(lnglat_pairs[:-1]):
    coords = [list(lnglat), list(lnglat_pairs[index+1])]
    line = Line(coords, '#D2322D', 3)
    m.add_line(line)
m.add_marker(marker)
image = m.render(zoom=9)
image.save('map.png')

## initialise gpxpy object
gpx = gpxpy.gpx.GPX()
gpx_track = gpxpy.gpx.GPXTrack()
gpx.tracks.append(gpx_track)
gpx_segment = gpxpy.gpx.GPXTrackSegment()
gpx_track.segments.append(gpx_segment)

## add track points using latlng data from activity
for lat,lng,elev in zip(stream_dict['lat'], stream_dict['lng'], stream_dict['altitude']):
    gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(lat, lng, elevation=elev))

## write gpx xml to file
with open("output.gpx", "w") as f:
    f.write( gpx.to_xml())