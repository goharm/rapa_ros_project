
#!/usr/bin/env python

import rospy
from geometry_msgs.msg import Twist
import sys, select, tty, termios
import speech_recognition as sr

BURGER_MAX_LIN_VEL = 0.22
BURGER_MAX_ANG_VEL = 2.84

LIN_VEL_STEP_SIZE = 0.01
ANG_VEL_STEP_SIZE = 0.1

msg = """
Control Your TurtleBot3 by SOUND!
---------------------------------

준비~
출발! 전진
빨리!
천천히! 느리게~
거기 아니야~
좌로~ 우로~
오른쪽~ 왼쪽~
정지!
그만~

긴급강제 정지 : s, 스페이스 바, "안돼"

Moving around:
        w
   a    s    d
        x
w/x : increase/decrease linear velocity (Burger : ~ 0.22, Waffle and Waffle Pi : ~ 0.26)
a/d : increase/decrease angular velocity (Burger : ~ 2.84, Waffle and Waffle Pi : ~ 1.82)
space key, s : force stop
CTRL-C to quit
"""

e = """
터틀봇이 준비가 안된 것 같아요~
"""


def getKey():
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''

    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key


def vels(target_linear_vel, target_angular_vel):
    return "currently:\tlinear vel %s\t angular vel %s " % (target_linear_vel,target_angular_vel)


def makeSimpleProfile(output, input, slop):
    if input > output:
        output = min( input, output + slop )
    elif input < output:
        output = max( input, output - slop )
    else:
        output = input

    return output


def constrain(input, low, high):
    if input < low:
      input = low
    elif input > high:
      input = high
    else:
      input = input

    return input


def checkLinearLimitVelocity(vel):
    vel = constrain(vel, -BURGER_MAX_LIN_VEL, BURGER_MAX_LIN_VEL)
    
    return vel


def checkAngularLimitVelocity(vel):
    vel = constrain(vel, -BURGER_MAX_ANG_VEL, BURGER_MAX_ANG_VEL)

    return vel


if __name__=="__main__":

    rospy.init_node('tb3_control_by_sound')
    pub = rospy.Publisher('cmd_vel', Twist, queue_size=10)

    turtlebot3_model = rospy.get_param("model", "burger")

    status = 0
    target_linear_vel   = 0.0
    target_angular_vel  = 0.0
    control_linear_vel  = 0.0
    control_angular_vel = 0.0


    try:
        print(msg)
        while(1):
            key = getKey()
            r = sr.Recognizer()
            with sr.Microphone() as source:
                print("터틀봇에게 이야기를 해주세요~")
                audio = r.listen(source)

            if key == 'w' or r.recognize_google(audio, language='ko') == "출발" or r.recognize_google(audio, language='ko') == "전진":
                target_linear_vel = checkLinearLimitVelocity(target_linear_vel + LIN_VEL_STEP_SIZE)
                status = status + 1
                print(vels(target_linear_vel,target_angular_vel))
            elif r.recognize_google(audio, language='ko') == "빨리":
                status = status + 1
                print(vels(target_linear_vel,target_angular_vel))
            
            elif r.recognize_google(audio, language='ko') == "느리게" or r.recognize_google(audio, language='ko') == "천천히":
                status = status - 1
                print(vels(target_linear_vel,target_angular_vel))

            elif key == 'x' :
                target_linear_vel = checkLinearLimitVelocity(target_linear_vel - LIN_VEL_STEP_SIZE)
                status = status + 1
                print(vels(target_linear_vel,target_angular_vel))
            elif key == 'a' or r.recognize_google(audio, language='ko') == "왼쪽" or r.recognize_google(audio, language='ko') == "좌로":
                target_angular_vel = checkAngularLimitVelocity(target_angular_vel + ANG_VEL_STEP_SIZE)
                status = status + 1
                print(vels(target_linear_vel,target_angular_vel))
            elif key == 'd' or r.recognize_google(audio, language='ko') == "오른쪽" or r.recognize_google(audio, language='ko') == "우로":
                target_angular_vel = checkAngularLimitVelocity(target_angular_vel - ANG_VEL_STEP_SIZE)
                status = status + 1
                print(vels(target_linear_vel,target_angular_vel))
            elif r.recognize_google(audio, language='ko') == "정지" or r.recognize_google(audio, language='ko') == "멈춰":
                target_linear_vel   = 0.0
                control_linear_vel  = 0.0
                target_angular_vel  = 0.0
                control_angular_vel = 0.0
                print(vels(target_linear_vel, target_angular_vel))
                break
            elif key == ' ' or key == 's' or r.recognize_google(audio, language='ko') == "그만" or r.recognize_google(audio, language='ko') == "안되" or r.recognize_google(audio, language='ko') == "안돼":
                target_linear_vel   = 0.0
                control_linear_vel  = 0.0
                target_angular_vel  = 0.0
                control_angular_vel = 0.0
                print(vels(target_linear_vel, target_angular_vel))
                break
            else:
                if (key == '\x03'):
                    break

            if status == 20 :
                print(msg)
                status = 0

            twist = Twist()

            control_linear_vel = makeSimpleProfile(control_linear_vel, target_linear_vel, (LIN_VEL_STEP_SIZE/2.0))
            twist.linear.x = control_linear_vel; twist.linear.y = 0.0; twist.linear.z = 0.0

            control_angular_vel = makeSimpleProfile(control_angular_vel, target_angular_vel, (ANG_VEL_STEP_SIZE/2.0))
            twist.angular.x = 0.0; twist.angular.y = 0.0; twist.angular.z = control_angular_vel

            pub.publish(twist)
    
    except sr.UnknownValueError:
        print("터틀봇이 알아듣지 못했습니다.")

    except sr.RequestError as e:
        print("알 수 없는 문제가 발생했습니다.; {0}".format(e))

    except:
        print(e)

    finally:
        twist = Twist()
        twist.linear.x = 0.0; twist.linear.y = 0.0; twist.linear.z = 0.0
        twist.angular.x = 0.0; twist.angular.y = 0.0; twist.angular.z = 0.0
        pub.publish(twist)