import time
import numpy as np
import json
import serial
import dynamixel_sdk as dynamixel
from pypot.dynamixel.conversion import dxl_to_degree, degree_to_dxl, dxl_to_speed, speed_to_dxl 

class NicoRobot():

    # Control table address
    ADDR_MX_TORQUE_ENABLE       = 24 
    ADDR_MX_GOAL_POSITION       = 30
    ADDR_MX_MOVING_SPEED        = 32
    ADDR_MX_PRESENT_POSITION    = 36
    ADDR_STATUS_RETURN_LEVEL    = 16  # Protocol 1
    
    # Values
    TORQUE_ENABLE               = 1                             # Value for enabling the torque
    TORQUE_DISABLE              = 0                             # Value for disabling the torque
    DEFAULT_MOVING_SPEED        = 40
    STATUS_RETURN_NONE          = 0                             # Value for no response from the motor
    STATUS_RETURN_READ          = 1                             # Value for no response from the motor on WRITE but not READ commands
    STATUS_RETURN_ALL           = 2                             # Value for no response from the motor on both WRITE and READ commands

    # Protocol version
    PROTOCOL_VERSION            = 1
    
    # Baud rate
    BAUDRATE                    = 1000000
    
    def __init__(self, portname='COM4', motorConfig='nico_humanoid_upper_rh7d_ukba.json'):
        with open(motorConfig,'rt') as f:
            self.config = json.load(f)
        # motor attributes: ['offset', 'type', 'id', 'angle_limit', 'orientation']
        self.dofs = [ dof for dof in self.config['motors'].keys() if not '_virtual' in dof ]
        self.joints = { # standard position
            'l_shoulder_z':0.0,
            'l_shoulder_y':1.0,
            'l_arm_x':0.0,
            'l_elbow_y':91.0,
            'l_wrist_z':-4.0,
            'l_wrist_x':-56.0,
            'l_thumb_z':-57.0,
            'l_thumb_x':-180.0,
            'l_indexfinger_x':-180.0,
            'l_middlefingers_x':-180.0,
            'r_shoulder_z':0.0,
            'r_shoulder_y':1.0,
            'r_arm_x':0.0,
            'r_elbow_y':91.0,
            'r_wrist_z':-5.0,
            'r_wrist_x':-56.0,
            'r_thumb_z':-57.0,
            'r_thumb_x':-180.0,
            'r_indexfinger_x':-180.0,
            'r_middlefingers_x':-180.0,
            'head_z':1.0,
            'head_y':1.0
        }
        self.offsets = {}
        self.directions = {}
        self.ranges = {}
        self.speeds = {}
        self.models = {}
        for dof in self.dofs:
            if '_virtual' in dof:
                continue
            self.offsets[dof] = self.config['motors'][dof]['offset']
            self.directions[dof] = -1.0 if self.config['motors'][dof]['orientation'] == 'indirect' else 1.0
            self.ranges[dof] = self.config['motors'][dof]['angle_limit']
            if self.directions[dof] < 0:
                self.ranges[dof] = [ -self.ranges[dof][1], -self.ranges[dof][0] ] 
            self.ranges[dof] = [
                self.ranges[dof][0] - self.offsets[dof],
                self.ranges[dof][1] - self.offsets[dof]
            ]
            self.speeds[dof] = -1.0
            self.models[dof] = self.config['motors'][dof]['type']
        """
        self.ranges = {
            'head_z':(-90.0,90.0),
            'head_y':(-40.0,30.0),
            'l_shoulder_z':(-30.0,80.0),
            'l_shoulder_y':(-30.0,180.0),
            'l_arm_x':(-0.0,70.0),
            'l_elbow_y':(50.0,180.0),
            'r_shoulder_z':(-30.0,80.0),
            'r_shoulder_y':(-30.0,180.0),
            'r_arm_x':(-0.0,70.0),
            'r_elbow_y':(50.0,180.0),
            'r_wrist_z':(-180.0,180.0),
            'r_wrist_x':(-180.0,180.0),
            'r_thumb_z':(-180.0,180.0),
            'r_thumb_x':(-180.0,180.0),
            'r_indexfinger_x':(-180.0,180.0),
            'r_middlefingers_x':(-180.0,180.0),
            'l_wrist_z':(-180.0,180.0),
            'l_wrist_x':(-180.0,180.0),
            'l_thumb_z':(-180.0,180.0),
            'l_thumb_x':(-180.0,180.0),
            'l_indexfinger_x':(-180.0,180.0),
            'l_middlefingers_x':(-180.0,180.0)
        }
        """
        self.port = dynamixel.PortHandler(portname)
        if self.port.openPort():
            print("Succeeded to open the port",portname)
        else:
            print("Failed to open the port",portname)
        if self.port.setBaudRate(self.BAUDRATE):
            print("Succeeded to change the baudrate")
        else:
            print("Failed to change the baudrate")
        self.port.setPacketTimeoutMillis(8) # [ms]
        self.handler = dynamixel.PacketHandler(protocol_version=self.PROTOCOL_VERSION)
        self.idxs = {
            'head_z':19,            # left(+90)-front(0)-right(-90)
            'head_y':20,            # up(+25)-down(-35)
            'l_shoulder_z':22,      #(-25)-to-left(0)-(+80)
            'l_shoulder_y':2,       #(-25)-down(0)-front(90)-up(180)
            'l_arm_x':4,            # to-body(0) - 70
            'l_elbow_y':6,          # close(50)-(90)-open(180)
            'r_shoulder_z':21,      # (-25)-to-right(0)-(+80)
            'r_shoulder_y':1,       #(-25)-down(0)-front(90)-up(180)
            'r_arm_x':3,            # to-body(0) - 70
            'r_elbow_y':5,          # close(50)-(90)-open(180)
            'r_wrist_z':31,         # elbow-wrist palm-up(-180)-palm-to-left(0)-palm-down(+180)
            'r_wrist_x':33,         # open(-180)-straight(0)-close(180)
            'r_thumb_z':34,         # up(-180)-left(+180)
            'r_thumb_x':35,         # open(-180)-close(+180)
            'r_indexfinger_x':36,   # open(-180)-close(+180)
            'r_middlefingers_x':37, # open(-180)-close(+180)
            'l_wrist_z':41,         # elbow-wrist palm-up(-180)-palm-to-right(0)-palm-down(+180)
            'l_wrist_x':43,         # open(-180)-straight(0)-close(180)
            'l_thumb_z':44,         # up(-180)-right(+180)
            'l_thumb_x':45,         # open(-180)-close(+180)
            'l_indexfinger_x':46,   # open(-180)-close(+180)
            'l_middlefingers_x':47, # open(-180)-close(+180)
        }
        self.noresponse = set()
        self.timeout = 0.0005
    
    def getJointNames(self):
        return self.dofs
        
    def getAngleLowerLimit(self, dof):
        return self.ranges[dof][0]
    
    def getAngleUpperLimit(self, dof):
        return self.ranges[dof][1]
    
    def getAngle(self, dof):
        id = self.idxs[dof]
        dxl, self.errno, self.result = self.handler.read2ByteTxRx(port=self.port, dxl_id=id, address=self.ADDR_MX_PRESENT_POSITION)
        degree = dxl_to_degree(dxl,self.models[dof])
        degree = degree * self.directions[dof] - self.offsets[dof]
        return degree
        
    def setAngle(self, dof, degree, speed=0.04):
        id = self.idxs[dof]
        speed *= 1000
        if speed != self.speeds[dof]:
            speed_dxl = speed_to_dxl(speed,self.models[dof])
            if dof in self.noresponse:
                self.handler.write2ByteTxOnly(port=self.port, dxl_id=id, address=self.ADDR_MX_MOVING_SPEED, data=speed_dxl)
                time.sleep(self.timeout)
                self.errno, self.result = 0, 0
            else:
                self.errno, self.result = self.handler.write2ByteTxRx(port=self.port, dxl_id=id, address=self.ADDR_MX_MOVING_SPEED, data=speed_dxl)       
            self.speeds[dof] = speed
        degree = (degree + self.offsets[dof]) * self.directions[dof] 
        dxl = degree_to_dxl(degree,self.models[dof])
        if dof in self.noresponse:
            self.handler.write2ByteTxOnly(port=self.port, dxl_id=id, address=self.ADDR_MX_GOAL_POSITION, data=dxl)
            time.sleep(self.timeout)
            self.errno, self.result = 0, 0
        else:
            self.errno, self.result = self.handler.write2ByteTxRx(port=self.port, dxl_id=id, address=self.ADDR_MX_GOAL_POSITION, data=dxl)
        
    def enableTorque(self, dof):
        id = self.idxs[dof]
        if dof in self.noresponse:
            self.handler.write1ByteTxOnly(port=self.port, dxl_id=id, address=self.ADDR_MX_TORQUE_ENABLE, data=self.TORQUE_ENABLE)
            time.sleep(self.timeout)
            vself.errno, self.result = 0, 0
        else:
            self.errno, self.result = self.handler.write1ByteTxRx(port=self.port, dxl_id=id, address=self.ADDR_MX_TORQUE_ENABLE, data=self.TORQUE_ENABLE)
    
    def disableTorque(self, dof):
        id = self.idxs[dof]
        if dof in self.noresponse:
            self.handler.write1ByteTxOnly(port=self.port, dxl_id=id, address=self.ADDR_MX_TORQUE_ENABLE, data=self.TORQUE_DISABLE)
            time.sleep(self.timeout)
            self.errno, self.result = 0, 0
        else:
            self.errno, self.result = self.handler.write1ByteTxRx(port=self.port, dxl_id=id, address=self.ADDR_MX_TORQUE_ENABLE, data=self.TORQUE_DISABLE)
        
    def enableResponse(self, dof):
        if not (dof in self.noresponse):
            return
        id = self.idxs[dof]
        self.handler.write1ByteTxOnly(port=self.port, dxl_id=id, address=self.ADDR_STATUS_RETURN_LEVEL, data=self.STATUS_RETURN_READ)
        time.sleep(self.timeout)
        self.errno, self.result = 0, 0
        self.noresponse.remove(dof)
    
    def disableResponse(self, dof):
        if dof in self.noresponse:
            return
        id = self.idxs[dof]
        self.errno, self.result = self.handler.write1ByteTxRx(port=self.port, dxl_id=id, address=self.ADDR_STATUS_RETURN_LEVEL, data=self.STATUS_RETURN_ALL)
        self.noresponse.add(dof)
    
    def getPalmSensorReading(self, dof):
        return 10.0
        
    def close(self):
        self.port.closePort()

if __name__ == '__main__':
    robot = NicoRobot()
    for dof in robot.getJointNames():
        while True:
            value = robot.getAngle(dof)
            print(f'{dof}: {value:.0f}')
            try:
                new_value = int(input())
            except:
                new_value = None
            if new_value is None:
                break
            robot.setAngle(dof,new_value)
