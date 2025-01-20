import time
import zmq
import msgpack as serializer
subject = ' Sub2'
# Setup zmq context and remote helper
ctx = zmq.Context()
socket = zmq.Socket(ctx, zmq.REQ)
socket.connect("tcp://127.0.0.1:50020")

# Measure round trip delay
t = time.time()
socket.send_string("t")
print(socket.recv_string())
print("Round trip command delay:", time.time() - t)

# set current Pupil time to 0.0
socket.send_string("T 0.0")
print(socket.recv_string())

#notify({"subject": "calibration.should_start"})
socket.send_string("C")
print("Eye tracking calibration started")
print(socket.recv_string())
sleep(25)
#notify({"subject": "calibration.should_stop"})
socket.send_string("c")
print("Eye tracking calibration stoped")
print(socket.recv_string())
# start recording
sleep(1)
socket.send_string("R" + subject)
print("Eye tracking recoding started")
print(socket.recv_string())
socket.send_string("T 1")
print(socket.recv_string())
#socket.send_string("t")
#print(socket.recv_string())
sleep(20)
socket.send_string("r")
print("Eye tracking recoding stoped")
print(socket.recv_string())