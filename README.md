# antennas_management
This is the code to manage antennas and febs for the GrandProto experiment.
It is composed of a main application app.py with some web templates in the templates directory.

It also provides a small postgres database with the postgis extension to manage geospatial data.

Everything is embeded into a docker compose which will run 2 small docker containers, one for the database and another for the web application.

## Build
To build and launch the app, just do : 
```
docker-compose up --build
```

Then connect to the web interface by the `http://localhost:5000` or `http://<server>:5000` url.
The default password is Grand2026 and can be changed in the docker-compose.yml file.

## Usage
Once a client (feb) is registered with its correct informations and that antennas are also registerd, a client can retreive the du_id corresponding to the closest antenna with the following command :
```
curl -X POST http://<server>:5000/get_du_id -H "Content-Type: application/x-www-form-urlencoded" -d "long=93.9869122891667&lat=40.9372295400003"
```

You will also find 2 example files (febs_list.csv and antenna_list.csv) that you can import into the database from the app for testing.

## Restrict to private network
In case you have a computer with 2 network (let say a private network 10.0.0.0/24 with ip 10.0.0.1 and a public network) and you want to restrict the app only to the private network, then just modify the port configuration in docker-compose.yml replacing :
```
ports:
      - "5432:5432"
```
and
```
ports:
      - "5000:5000"
```
by
```
ports:
      - "10.0.0.1:5432:5432"
```
and
```
ports:
      - "10.0.0.1:5000:5000"
```

## Useful commands
You can get into the database docker with the command :
```
docker exec -it postgis_container psql -U user -d grand
```

You can get into the python application docker with : 
```
docker exec -it flask_app bash
```
