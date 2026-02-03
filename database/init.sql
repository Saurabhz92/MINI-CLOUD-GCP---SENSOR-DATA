CREATE TABLE IF NOT EXISTS sensor_measurements (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    temperature DECIMAL(5, 2),
    humidity DECIMAL(5, 2),
    battery_level DECIMAL(5, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_device_timestamp ON sensor_measurements(device_id, timestamp);
