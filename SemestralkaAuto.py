from machine import Pin, ADC, PWM
from time import sleep, ticks_ms, ticks_diff

# SNÍMAČE
sensor_left   = ADC(Pin(4))
sensor_center = ADC(Pin(0))
sensor_right  = ADC(Pin(1))

sensor_left.atten(ADC.ATTN_11DB)
sensor_center.atten(ADC.ATTN_11DB)
sensor_right.atten(ADC.ATTN_11DB)

#  MOTORY
m1_in1 = PWM(Pin(20))
m1_in2 = PWM(Pin(22))

m2_in1 = PWM(Pin(19))
m2_in2 = PWM(Pin(18))

for m in [m1_in1, m1_in2, m2_in1, m2_in2]:
    m.freq(1000)

# RGB LED
led_red_pin   = Pin(10, Pin.OUT)
led_green_pin = Pin(11, Pin.OUT)
led_blue_pin  = Pin(21, Pin.OUT)

# KONŠTANTY
THRESHOLD = 400

SPEED_LEFT  = 20000
SPEED_RIGHT = 22000

MEMORY_TIME = 40

#  STAV
last_direction = "left"
last_seen = ticks_ms()


# Kontrola či snímač vidí čiernu čiaru
def is_black(value):
    return value < THRESHOLD


# Vypnutie LED
def led_off():
    led_red_pin.value(1)
    led_green_pin.value(1)
    led_blue_pin.value(1)


# Červená LED = robot stratil čiaru
def led_show_red():
    led_red_pin.value(0)
    led_green_pin.value(1)
    led_blue_pin.value(1)


# Zelená LED = robot ide rovno
def led_show_green():
    led_red_pin.value(1)
    led_green_pin.value(0)
    led_blue_pin.value(1)


# Modrá LED = robot zatáča
def led_show_blue():
    led_red_pin.value(1)
    led_green_pin.value(1)
    led_blue_pin.value(0)


# Ovládanie ľavého motora
def motor_left(speed):
    if speed > 0:
        m1_in1.duty_u16(min(speed, 65535))
        m1_in2.duty_u16(0)
    elif speed < 0:
        m1_in1.duty_u16(0)
        m1_in2.duty_u16(min(-speed, 65535))
    else:
        m1_in1.duty_u16(0)
        m1_in2.duty_u16(0)


# Ovládanie pravého motora
def motor_right(speed):
    if speed > 0:
        m2_in1.duty_u16(min(speed, 65535))
        m2_in2.duty_u16(0)
    elif speed < 0:
        m2_in1.duty_u16(0)
        m2_in2.duty_u16(min(-speed, 65535))
    else:
        m2_in1.duty_u16(0)
        m2_in2.duty_u16(0)


# Pohyb dopredu
def forward():
    motor_left(SPEED_LEFT)
    motor_right(SPEED_RIGHT)


# Otočenie doľava
def turn_left():
    motor_left(-20000)
    motor_right(42000)


# Otočenie doprava
def turn_right():
    motor_left(42000)
    motor_right(-20000)


# Hľadanie čiary doľava
def search_left():
    motor_left(-24000)
    motor_right(44000)


# Hľadanie čiary doprava
def search_right():
    motor_left(44000)
    motor_right(-24000)


#  HLAVNÝ CYKLUS
while True:

    # Čítanie hodnôt zo snímačov
    l = sensor_left.read()
    c = sensor_center.read()
    r = sensor_right.read()

    left_black = is_black(l)
    center_black = is_black(c)
    right_black = is_black(r)

    print("L:", l, left_black, "C:", c, center_black, "R:", r, right_black)

    # Robot ide rovno po čiare
    if center_black:
        forward()
        led_show_green()
        last_seen = ticks_ms()

    # Čiara je viac vľavo
    elif left_black:
        turn_left()
        led_show_blue()
        last_direction = "left"
        last_seen = ticks_ms()

    # Čiara je viac vpravo
    elif right_black:
        turn_right()
        led_show_blue()
        last_direction = "right"
        last_seen = ticks_ms()

    # Robot stratil čiaru
    else:
        elapsed = ticks_diff(ticks_ms(), last_seen)

        # Krátko pokračuje dopredu
        if elapsed < MEMORY_TIME:
            forward()
            led_off()

        # Potom začne hľadať čiaru
        else:
            led_show_red()

            if last_direction == "left":
                search_left()
            else:
                search_right()

    sleep(0.01)