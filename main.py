from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from FlightRadar24 import FlightRadar24API

app = FastAPI()

fr_api = FlightRadar24API()

# Armenia bounding box: lamin=38.5, lomin=43.5, lamax=41.5, lomax=46.5
# FlightRadar24 bounds format: "max_lat,min_lat,min_lon,max_lon"
ARMENIA_BOUNDS = "41.5,38.5,43.5,46.5"

@app.get("/api/flights")
async def get_flights():
    try:
        # get_flights is a blocking call in the library, 
        # for a production app it's better to run in a thread, 
        # but for this scale it's fine.
        flights_data = fr_api.get_flights(bounds=ARMENIA_BOUNDS)
        
        flights = []
        for f in flights_data:
            flights.append({
                "icao24": f.icao_24_addr,
                "callsign": f.callsign if f.callsign else "N/A",
                "lat": f.latitude,
                "lon": f.longitude,
                "velocity": f.ground_speed,
                "heading": f.heading
            })
        return flights
    except Exception as e:
        print(f"Error fetching data from FlightRadar24: {e}")
        return []

# Mount the static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse(os.path.join("static", "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
