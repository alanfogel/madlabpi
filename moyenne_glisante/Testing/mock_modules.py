# mock_modules.py

class MockAnalogIn:
    def __init__(self, pin):
        self.value = 30000  # Simulated ADC value

class MockI2C:
    def __init__(self, scl, sda):
        pass

# Mock the board module
class MockBoard:
    D25 = "D25"
    D24 = "D24"
    A1 = "A1"

# Mock the ulab.numpy module
class MockNumpy:
    @staticmethod
    def mean(values):
        return sum(values) / len(values)

# Assign mocks to the module names
board = MockBoard()
busio = type('busio', (), {'I2C': MockI2C})
analogio = type('analogio', (), {'AnalogIn': MockAnalogIn})
np = MockNumpy()