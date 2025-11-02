import googlemaps
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
# Initialize client with your API key
gmaps = googlemaps.Client(key=api_key)

def get_distance(origin, destination):
    # Request distance matrix
    result = gmaps.distance_matrix(origins=[origin],
                                destinations=[destination],
                                mode="driving")

    # Extract distance and duration
    distance = result['rows'][0]['elements'][0]['distance']['text']
    duration = result['rows'][0]['elements'][0]['duration']['text']
    return distance, duration

if __name__ == "__main__":
    origin = "845 Sherbrooke St W, Montreal, Quebec H3A 0G4"
    destination = "University of Toronto, ON"
    distance, duration = get_distance(origin, destination)
    print(f"Distance: {distance}, Duration: {duration}")
    print(type(distance))

