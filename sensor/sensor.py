from typing import List
import smbus

DEVICE_BUS = 1
DEVICE_ADDR = 0x17

TEMP_REG = 0x01
LIGHT_REG_L = 0x02
LIGHT_REG_H = 0x03
STATUS_REG = 0x04
ON_BOARD_TEMP_REG = 0x05
ON_BOARD_HUMIDITY_REG = 0x06
ON_BOARD_SENSOR_ERROR = 0x07
BMP280_TEMP_REG = 0x08
BMP280_PRESSURE_REG_L = 0x09
BMP280_PRESSURE_REG_M = 0x0A
BMP280_PRESSURE_REG_H = 0x0B
BMP280_STATUS = 0x0C
HUMAN_DETECT = 0x0D

class SensorData:

    humansDetected: bool

    offChipSensorOnline: bool
    onBoardSensorOnline: bool
    barometerSensorOnline: bool
    brightnessSensorOnline: bool

    offChipTemperature: str
    
    temperature: int
    brightness: int
    humidity: int
    
    barometerTemperature: int
    barometerPressure: int

    hasErrors: bool
    errors: List[str] = []

    #def __init__(self, humansDetected) -> None:
    #    self.humansDetected = humansDetected
    
    def addError(message: str) -> None:
        self.errors.append(message)
        hasErrors = True
        return

    @staticmethod
    def getRawdata() -> List[int]:
   
        bus = smbus.SMBus(DEVICE_BUS)
        aReceiveBuf = [0x00]

        for i in range(TEMP_REG,HUMAN_DETECT + 1):
            aReceiveBuf.append(bus.read_byte_data(DEVICE_ADDR, i))
        return aReceiveBuf

    @staticmethod
    def parse(buffer:list[int]) -> SensorData:
        data = SensorData()
            
        # off-chip sensor temperature
        if aReceiveBuf[STATUS_REG] & 0x01 :
            data.addError("Off-chip temperature sensor overrange!")
        elif aReceiveBuf[STATUS_REG] & 0x02 :
            data.addError("No external temperature sensor!")
        else :
            data.offChipSensorOnline = True
            data.offChipTemperature = aReceiveBuf[TEMP_REG]
    
        # brightness
        if aReceiveBuf[STATUS_REG] & 0x04 :
            data.addError("Onboard brightness sensor overrange!")
        elif aReceiveBuf[STATUS_REG] & 0x08 :
            data.addError("Onboard brightness sensor failure!")
        else :
            data.brightnessSensorOnline = True
            data.brightness = (aReceiveBuf[LIGHT_REG_H] << 8 | aReceiveBuf[LIGHT_REG_L])
        
        data.onBoardSensorOnline = aReceiveBuf[ON_BOARD_SENSOR_ERROR] != 0
        data.temperature = aReceiveBuf[ON_BOARD_TEMP_REG]
        data.humidity = aReceiveBuf[ON_BOARD_HUMIDITY_REG]
    
        # barometer
        data.barometerOnline = aReceiveBuf[BMP280_STATUS] == 0
        data.barometerTemperature = aReceiveBuf[BMP280_TEMP_REG]
        data.barometerPressure = (aReceiveBuf[BMP280_PRESSURE_REG_L] | aReceiveBuf[BMP280_PRESSURE_REG_M] << 8 | aReceiveBuf[BMP280_PRESSURE_REG_H] << 16)

        if not data.barometerOnline:
            data.addError("Onboard temperature and humidity sensor data may not be up to date!")
        
        if not data.barometerOnline :
            data.addError("Onboard barometer works abnormally!")
  
        data.humansDetected = aReceiveBuf[HUMAN_DETECT] == 1

        return data

    @staticmethod
    def create() -> SensorData:
        rawSetsorData = SensorData.getRawdata()
        
        return parse(rawSetsorData)
        
    def print() -> None:

        print("barometer temperature = %d Celsius" % data.barometerTemperature)
        print("barometer pressure = %d pascal" % data.barometerPressure)
    
        print("on-board brightness sensor = %d Lux" % data.brightness)
        print("on-board sensor temperature = %d Celsius" % data.temperature)
        print("on-board sensor humidity = %d %%" % data.humidity)

        print("off-chip sensor temperature = %d Celsius" % data.offChipTemperature)

        for error in errors:
            print(error)
        return

if __name__ == '__main__':
    print ('Program is starting ... ')
    try:
        sensorData = SensorData.create()
        sensorData.print()
    except KeyboardInterrupt:
        destroy()