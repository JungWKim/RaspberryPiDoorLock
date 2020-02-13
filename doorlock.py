import RPi.GPIO as gpio
import time
from RPLCD import CharLCD

gpio.setwarnings(False) #경고메시지 무시

#BCM상에 설정된 번호로 각각의 핀에 접근
gpio.setmode(gpio.BCM)

#keypad에 연결된 gpio 번호 리스트
keypad = [11, 19, 6, 9, 20, 12, 10, 26, 13, 21, 7, 16]
#keypad 리스트대로 setup
for i in range(len(keypad)):
    gpio.setup(keypad[i], gpio.IN)

red = 5 #빨간 LED 핀번호
green = 14 #초록 LED 핀번호
gpio.setup(red, gpio.OUT)
gpio.setup(green, gpio.OUT)

gpio.setup(25, gpio.OUT)
motor = gpio.PWM(25, 50) #duty rate = 50%(최대 100의 속도 중 50)

lcd = CharLCD(numbering_mode=gpio.BCM, cols = 16, rows = 2, pin_rs = 23, pin_e=22, pins_data=[27,18,17,4])

password = ['1','2','3','4','#'] #비밀번호 설정

tryPassword = [] #입력할 패스워드는 공백으로 설정

count = 0 #번호 입력 횟수
    
falseCount = 0 #잘못 입력한 횟수

#Buzzer 사용가능 옥타브 설정(4옥타브 기준>>도레미파솔라시도)
octav = [523, 587, 659, 698, 784, 880, 987, 1046]

def setup():
    BUZZER = 24 #Buzzer GPIO번호 설정
    
    #Buzzer를 출력신호로 설정
    gpio.setup(BUZZER, gpio.OUT)

    global Buzz
    
    #523Hz를 초기주파수로 설정
    Buzz = gpio.PWM(BUZZER, octav[0])

    gpio.output(BUZZER, 1)
    
    gpio.output(green, False)
    gpio.output(red, True)

def LCD(row, col, string):
    lcd.cursor_pos = (row, col)
    lcd.write_string(string)

def sound(start, end, gap):
    Buzz.start(10)
    for i in range(start, end, gap):
        Buzz.ChangeFrequency(octav[i])
        time.sleep(0.7)
    Buzz.stop()

def keypadCheck():
    for i in range(len(keypad)):
        if gpio.input(keypad[i]) == 0:
            if i == 10:
                tryPassword.append('*')
            elif i == 11:
                tryPassword.append('#')
            else:
                tryPassword.append(str(i+1))
            time.sleep(1)
            return 1
    return 0
        
setup() #Buzzer와 LED 기본 설정

lcd.clear()
LCD(0, 0, "Password :")
for i in range(len(tryPassword)):
    LCD(0, 11+i, str(tryPassword[i]))

while True:
    while keypadCheck(): #keypad의 버튼이 눌릴때만 명령들 실행
        count += 1 #버튼 누른 횟수
        
        #lcd part
        lcd.clear()
        LCD(0, 0, "Password :")
        for i in range(len(tryPassword)):
            LCD(0, 11+i, str(tryPassword[i]))
        
        print("입력횟수 :", count)
        if count == 5: #5개의 버튼을 누른 경우
            if password == tryPassword: #일치할 경우 초록불 켜지고 빨간불 꺼지고
                print("문이 열립니다.")
                
                gpio.output(green, True)
                gpio.output(red, False)
                
                #lcd part
                time.sleep(1)
                lcd.clear()
                LCD(0, 0, "Opening the door")
                
                sound(4, 8, 1)
                motor.start(5) #모터 동작
                motor.ChangeDutyCycle(1) #모터 왼쪽으로 약 90도 회전
                
                #lcd part
                for i in range(3,-1,-1):
                    LCD(1, 0, "Time Left : "+str(i))
                    time.sleep(1)
                lcd.clear()
                LCD(0, 0, "Closing the door")
                
                sound(3, -1, -1)
                motor.ChangeDutyCycle(5) # 모터 오른쪽으로 약 90도 회전
                time.sleep(1.5)
                motor.stop() #모터 정지
                print("문이 닫힙니다.")
                
                gpio.output(green,False)
                gpio.output(red, True)
                
            elif password != tryPassword: #일치하지 않을 경우
                falseCount += 1
                if falseCount == 3: #심지어 3회 오류시 >> 2분동작 입력불가
                    print("3회 입력 오류")
                    falseCount = 0
                    
                    #lcd part
                    time.sleep(1)
                    lcd.clear()
                    LCD(0, 0, "3times mismatch")
                    LCD(1, 0, "Time Left : 2min")
                    time.sleep(120)
                    
                else: #2회 미만으로 틀리면 메시지만 출력
                    print("비밀번호가 맞지 않습니다.")
                    
                    #lcd part
                    time.sleep(1)
                    lcd.clear()
                    LCD(0, 0, "Wrong Password")
                    for i in range(3, -1, -1):
                        LCD(1, 0, "Time Left : "+str(i))
                        time.sleep(1)
            count = 0
            tryPassword = []
            
        lcd.clear()
        LCD(0, 0, "Password :")
        for i in range(len(tryPassword)):
            LCD(0, 11+i, str(tryPassword[i]))

Buzz.stop()
motor.stop()
gpio.cleanup() #gpio가 점유한 하드웨어자원 반납