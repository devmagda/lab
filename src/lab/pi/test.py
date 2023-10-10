import RPi.GPIO as GPIO
import time

class LCD1602:
    def __init__(self, rs, e, d4, d5, d6, d7, width=16, rows=2):
        self.RS = rs
        self.E = e
        self.D4 = d4
        self.D5 = d5
        self.D6 = d6
        self.D7 = d7
        self.LCD_WIDTH = width
        self.LCD_ROWS = rows

    def setup_gpio(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.RS, GPIO.OUT)
        GPIO.setup(self.E, GPIO.OUT)
        GPIO.setup(self.D4, GPIO.OUT)
        GPIO.setup(self.D5, GPIO.OUT)
        GPIO.setup(self.D6, GPIO.OUT)
        GPIO.setup(self.D7, GPIO.OUT)

    def send_command(self, cmd):
        GPIO.output(self.RS, False)
        self.lcd_byte(cmd)

    def send_data(self, data):
        GPIO.output(self.RS, True)
        self.lcd_byte(data)

    def lcd_byte(self, bits):
        GPIO.output(self.D4, False)
        GPIO.output(self.D5, False)
        GPIO.output(self.D6, False)
        GPIO.output(self.D7, False)

        if bits & 0x10 == 0x10:
            GPIO.output(self.D4, True)
        if bits & 0x20 == 0x20:
            GPIO.output(self.D5, True)
        if bits & 0x40 == 0x40:
            GPIO.output(self.D6, True)
        if bits & 0x80 == 0x80:
            GPIO.output(self.D7, True)

        self.lcd_toggle_enable()

        GPIO.output(self.D4, False)
        GPIO.output(self.D5, False)
        GPIO.output(self.D6, False)
        GPIO.output(self.D7, False)

        if bits & 0x01 == 0x01:
            GPIO.output(self.D4, True)
        if bits & 0x02 == 0x02:
            GPIO.output(self.D5, True)
        if bits & 0x04 == 0x04:
            GPIO.output(self.D6, True)
        if bits & 0x08 == 0x08:
            GPIO.output(self.D7, True)

        self.lcd_toggle_enable()

    def lcd_toggle_enable(self):
        time.sleep(0.0005)
        GPIO.output(self.E, True)
        time.sleep(0.0005)
        GPIO.output(self.E, False)
        time.sleep(0.0005)

    def initialize_lcd(self):
        self.lcd_byte(0x33)
        self.lcd_byte(0x32)
        self.lcd_byte(0x28)
        self.lcd_byte(0x0C)
        self.lcd_byte(0x01)
        self.lcd_byte(0x06)

    def display_text(self, text, line=1):
        if line == 1:
            self.send_command(0x80)
        elif line == 2:
            self.send_command(0xC0)

        text = text.ljust(self.LCD_WIDTH, " ")
        for i in range(self.LCD_WIDTH):
            self.send_data(ord(text[i]))

    def clear_lcd(self):
        self.send_command(0x01)

    def cleanup(self):
        GPIO.cleanup()

if __name__ == "__main__":
    try:
        lcd = LCD1602(rs=4, e=6, d4=17, d5=18, d6=27, d7=22, width=16, rows=2)
        lcd.setup_gpio()
        lcd.initialize_lcd()
        lcd.display_text("Hello, World!", line=1)
        lcd.display_text("LCD OOP Example", line=2)
        time.sleep(5)
        lcd.clear_lcd()
    except KeyboardInterrupt:
        pass
    finally:
        lcd.cleanup()
