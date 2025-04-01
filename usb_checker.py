from geopy.geocoders import Nominatim

loc = Nominatim(user_agent="Geopy Library")

getLoc = loc.geocode("İzmir")

print(getLoc.address)

print("Latitude = ", getLoc.latitude, "\n")
print("Longitude = ", getLoc.longitude)