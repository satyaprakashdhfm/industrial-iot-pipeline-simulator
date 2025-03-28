-- Create the SensorDB database if it doesn't exist
IF DB_ID('SensorDB') IS NULL
BEGIN
    CREATE DATABASE SensorDB;
END
GO

USE SensorDB;
GO

-- Create the SensorData table if it doesn't exist
IF OBJECT_ID('dbo.SensorData', 'U') IS NULL
BEGIN
    CREATE TABLE SensorData (
        ID INT IDENTITY(1,1) PRIMARY KEY,
        MachineID VARCHAR(50),
        Timestamp DATETIME,
        Temperature FLOAT,
        Pressure FLOAT
    );
END
GO
