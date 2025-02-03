-- Add PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- Create table antenna with unicity of du_id 
CREATE TABLE IF NOT EXISTS antenna (
    id SERIAL PRIMARY KEY,
    longitude DOUBLE PRECISION NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    du_id INT NOT NULL UNIQUE,  -- Contrainte d'unicité sur du_id
    geom GEOGRAPHY(Point, 4326)
);

-- Add trigger to update geom automatically
CREATE OR REPLACE FUNCTION update_geom()
RETURNS TRIGGER AS $$
BEGIN
    NEW.geom := ST_SetSRID(ST_MakePoint(NEW.longitude, NEW.latitude), 4326);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_geom
BEFORE INSERT OR UPDATE ON antenna
FOR EACH ROW EXECUTE FUNCTION update_geom();

-- index creation for better perfs
CREATE INDEX idx_longitude ON antenna(longitude);
CREATE INDEX idx_latitude ON antenna(latitude);
CREATE INDEX idx_du_id ON antenna(du_id);
CREATE INDEX idx_geom ON antenna USING GIST (geom);

-- Create table febs
CREATE TABLE IF NOT EXISTS feb (
    feb_id INT PRIMARY KEY,              
    mac_address VARCHAR(17) UNIQUE NOT NULL,    -- Format MAC (XX:XX:XX:XX:XX:XX)
    ip_address VARCHAR(15) UNIQUE NOT NULL,       -- Format IP (XXX.XXX.XXX.XXX)
    target_du_id INT
);

CREATE INDEX idx_feb_id ON feb(feb_id);
CREATE INDEX idx_ip_address ON feb(ip_address);

-- join febs and antennas
CREATE TABLE IF NOT EXISTS feb_antenna (
    id SERIAL PRIMARY KEY,
    feb_id INT UNIQUE NOT NULL,
    antenna_id INT UNIQUE NOT NULL,
    last_seen TIMESTAMP NOT NULL,
    last_test TIMESTAMP NOT NULL,
    FOREIGN KEY (feb_id) REFERENCES feb(feb_id),
    FOREIGN KEY (antenna_id) REFERENCES antenna(id),
    UNIQUE (feb_id, antenna_id) -- unicity constraint
);



CREATE OR REPLACE FUNCTION update_last_seen()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_seen = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$
 LANGUAGE plpgsql;

CREATE TRIGGER update_feb_antenna_last_seen
BEFORE UPDATE ON feb_antenna
FOR EACH ROW
EXECUTE FUNCTION update_last_seen();

CREATE OR REPLACE FUNCTION get_antennas_with_febs()
RETURNS TABLE (antenna_id INT, longitude DOUBLE PRECISION, latitude DOUBLE PRECISION,
               du_id INT, feb_id INT, mac_address VARCHAR, ip_address VARCHAR, target_du_id INT) AS $$
BEGIN
    RETURN QUERY
    SELECT a.id AS antenna_id, a.longitude, a.latitude, a.du_id,
           fa.feb_id, f.mac_address, f.ip_address, f.target_du_id
    FROM antenna a
    LEFT JOIN feb_antenna fa ON a.id = fa.antenna_id
    LEFT JOIN feb f ON fa.feb_id = f.feb_id;
END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION get_febs_with_antennas()
RETURNS TABLE (antenna_id INT, longitude DOUBLE PRECISION, latitude DOUBLE PRECISION,
               du_id INT, feb_id INT, mac_address VARCHAR, ip_address VARCHAR, target_du_id INT) AS $$
BEGIN
    RETURN QUERY
    SELECT a.id AS antenna_id, a.longitude, a.latitude, a.du_id,
           f.feb_id, f.mac_address, f.ip_address, f.target_du_id
    FROM feb f
    LEFT JOIN feb_antenna fa ON f.feb_id = fa.feb_id
    LEFT JOIN antenna a ON fa.antenna_id = a.id
    ;
END;
$$ LANGUAGE plpgsql;
