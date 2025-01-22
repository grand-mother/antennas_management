# antennas_management
This is the code to manage antennas for the GrandProto experiment.
It is composed of a main application app.py some web templates in the templates directory.

It also provides a small postgres database with the postgis extension to manage geospatial data.

Everything is embeded into a docker compose which will run 2 small docker containers, one for the database and another for the web application.

## Build
To build and lauch the app, just do : 
```
docker-compose up --build
```

Then connect to the web interface by the `http://localhost:5000` or `http://<server>:5000` url.

## Usage
Once a client (feb) is registered with its correct informations and that antennas are also registerd, a client can retreive the du_id corresponding to the closest antenna with the following command :
```
curl -X POST http://<server>:5000/get_du_id -H "Content-Type: application/x-www-form-urlencoded" -d "long=93.9869122891667&lat=40.9372295400003"
```
