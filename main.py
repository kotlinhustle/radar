from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import httpx

app = FastAPI()

# OpenSky Network API URL for states in a bounding box
# Armenia bounding box: lamin=38.5, lomin=43.5, lamax=41.5, lomax=46.5
OPENSKY_URL = "https://opensky-network.org/api/states/all"

@app.get("/api/flights")
async def get_flights():
    params = {
        "lamin": 38.5,
        "lomin": 43.5,
        "lamax": 41.5,
        "lomax": 46.5
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(OPENSKY_URL, params=params, timeout=10.0)
            data = response.json()
            
            flights = []
            if data and "states" in data and data["states"]:
                for state in data["states"]:
                    # OpenSky state vector documentation:
                    # 0: icao24, 1: callsign, 2: origin_country, 3: time_position, 
                    # 4: last_contact, 5: longitude, 6: latitude, 7: baro_altitude...
                    flights.append({
                        "icao24": state[0],
                        "callsign": state[1].strip() if state[1] else "N/A",
                        "lat": state[6],
                        "lon": state[5],
                        "velocity": state[9],
                        "heading": state[10]
                    })
            return flights
        except Exception as e:
            print(f"Error fetching data: {e}")
            return []

# Mount the static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse(os.path.join("static", "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
