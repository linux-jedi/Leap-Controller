import sys, thread, time, requests, json, unirest, math
from websocket import create_connection

sys.path.insert(0, "LeapSDK/lib")
import Leap
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture

class SampleListener(Leap.Listener):
    def on_init(self, controller):
        host = "ws://globe-sb.herokuapp.com/LeapPosition"
        self.ws = create_connection(host)
        print "Initialized"

    def on_connect(self, controller):
        print "Connected"

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print "Disconnected"

    def on_exit(self, controller):
        self.ws.close()
        print "Exited"

    def on_frame(self, controller):
        # Get the most recent frame and report some basic information
        frame = controller.frame()

        # Get hands
        for hand in frame.hands:

            handType = "Left hand" if hand.is_left else "Right hand"

            # Get distance from leap to hand
            distanceFromLeap = hand.stabilized_palm_position.y
            distanceFromLeap = int(distanceFromLeap) / 10 * 10
            
            # Get the hand's normal vector
            normal = hand.palm_normal
            x = -1 * normal.x
            z = normal.z

            # Send all data
            sendTrackingData(distanceFromLeap, x, z, self.ws)

def sendTrackingData(distance, x, y, ws):
    jsonData = {}
    jsonData["direction"] = determineDirection(x,y)
    jsonData["position"] = transformPosition(distance)

    ws.send(json.dumps(jsonData))
    print jsonData

def transformPosition(position):
    return int((7.0/275.0) * (position) + (107.0/11.0))

def determineDirection(x, y):
    if abs(x) < .4 and abs(y) < .4:
        return 0

    if abs(x) > abs(y):
        if x >= 0:
            return 2
        else:
            return 4
    else:
        if y >= 0:
            return 1
        else:
            return 3

def main():
    # Create a sample listener and controller
    listener = SampleListener()
    controller = Leap.Controller()

    # Have the sample listener receive events from the controller
    controller.add_listener(listener)

    # Keep this process running until Enter is pressed
    print "Press Enter to quit..."
    try:
        sys.stdin.readline()
    except KeyboardInterrupt:
        pass
    finally:
        # Remove the sample listener when done
        controller.remove_listener(listener)


if __name__ == "__main__":
    main()