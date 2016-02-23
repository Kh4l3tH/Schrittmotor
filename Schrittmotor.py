# -*- coding: utf-8 -*-
from SchrittmotorConst import *
from time import sleep
from time import time


class Schrittmotor():
    def __init__(self, cmd, id, schritte, schrittmodus, steigung, rampentyp, rampe_hz_pro_ms,
        reference_pin=None, umin_default=None, offset=0, inverted=False):
        self.cmd = cmd
        self.id = id
        self.schritte_pro_u = schritte * schrittmodus
        self.schritte_pro_mm = schritte * schrittmodus / steigung
        self.reference_pin = reference_pin
        self.umin_default = umin_default
        self.offset = offset
        self.inverted = inverted

        self.cmd.setMotor(id)
        self.cmd.setDirection(RECHTS)
        if rampentyp.lower() == 'trapez':
            self.cmd.setRampType(TRAPEZ)
        elif rampentyp.lower() == 'sinus':
            self.cmd.setRampType(SINUS)
        elif rampentyp.lower() == 'jerk_free':
            self.cmd.setRampType(JERK_FREE)
        else:
            raise 'Rampentyp unterstuetzt trapez, sinus und jerk_free'
        ramp = int((3000 / (rampe_hz_pro_ms+11.7)) ** 2)
        self.cmd.setRamp(ramp)
        self.cmd.setBrakeRamp(ramp)
        # self.cmd.setStepMode(schrittmodus)
        assert self.cmd.getStepMode() == schrittmodus, 'Falscher Schrittmodus für Motor {0}!\nSoll: {1}\nIst: {2}'.format(self.id, schrittmodus, cmd.getStepMode())

    def reset_position(self):
        self.cmd.setMotor(self.id)
        self.cmd.resetPositionError(False)

    def get_position(self, offset=None, inverted=None):
        if offset == None:
            offset = self.offset
        if inverted == None:
            inverted = self.inverted
        self.cmd.setMotor(self.id)
        position = float(self.cmd.getPosition()) / self.schritte_pro_mm
        if inverted:
            return offset - position
        else:
            return position - offset

    def move_abs(self, position, speed=2000, offset=None, inverted=None):
        if offset == None:
            offset = self.offset
        if inverted == None:
            inverted = self.inverted
        frequency = self.calc_frequency(speed)
        if inverted:
            position = -position
        position = offset + position
        steps = int(self.schritte_pro_mm * position)
        self.cmd.setMotor(self.id)
        self.cmd.setPositionType(ABSOLUT)
        self.cmd.setDirection(RECHTS)
        self.cmd.setMaxFrequency(frequency)
        self.cmd.setSteps(steps)
        print 'Motor {0}: \033[92m{1:b}\033[0m'.format(self.id, self.status())
        self.cmd.startTravelProfile()

    def move_rel(self, distance, speed=2000, inverted=None):
        if inverted == None:
            inverted = self.inverted
        frequency = self.calc_frequency(speed)
        if inverted:
            distance = -distance
        steps = int(self.schritte_pro_mm * distance)

        self.cmd.setMotor(self.id)
        self.cmd.setPositionType(RELATIV)
        self.cmd.setDirection(RECHTS)
        self.cmd.setMaxFrequency(frequency)
        self.cmd.setSteps(steps)
        self.cmd.startTravelProfile()

    def rotate(self, umin=None, direction=LINKS):
        if self.umin_default == None:
            raise ValueError('Drehzahlmodus fuer diesen Motor nicht zulaessig! Bei der Initialisierung muss umin_default gesetzt werden!')
        if umin == None:
            umin = self.umin_default
    	speed = int(umin * self.schritte_pro_u / 60)
        self.cmd.setMotor(self.id)
        self.cmd.setPositionType(DREHZAHLMODUS)
        self.cmd.setMaxFrequency(speed)
        self.cmd.setDirection(direction)
        self.cmd.startTravelProfile()

    def calc_frequency(self, speed):
        frequency = self.schritte_pro_mm * speed / 60.0
        return int(round(frequency,0))

    def stop(self):
        self.cmd.setMotor(self.id)
        self.cmd.stopTravelProfile()

    def status(self):
        self.cmd.setMotor(self.id)
        return self.cmd.getStatusByte()

    def wait(self):
        print 'Waiting for Motor {0}'.format(self.id)
        self.cmd.setMotor(self.id)
        time_current = time()
        position_current = self.cmd.getPosition()
        while not self.cmd.isMotorReady():
            if time() - time_current >= 5:
                print 'Motor: {0}, Position: {1:.6f}, Status: \033[96m{2:b}\033[0m'.format(self.id, self.get_position(), self.status())
                time_current = time()
                if position_current == self.cmd.getPosition():
                    print '\033[91mMotor ist vermutlich stehen geblieben!\033[0m'
                    raise ValueError('Motor ist vermutlich stehen geblieben!')
                position_current = self.cmd.getPosition()
            sleep(0.1)

        print 'Checking Position Error:'
        self.position_error()
        print 'Continuing'

    def ready(self):
        self.cmd.setMotor(self.id)
        return self.cmd.isMotorReady()

    def position_error(self):
        self.cmd.setMotor(self.id)
        pos_control = self.cmd.getPosition()
        pos_encoder = self.cmd.getEncoderRotary()
        diff = pos_encoder-pos_control
        print 'Position   Motor: {0}'.format(pos_control)
        print 'Position Encoder: {0}'.format(pos_encoder)
        if abs(diff) < 3:
            print 'Position Diff: \033[92m{0}\033[0m'.format(diff)
        else:
            print 'Position Diff: \033[91m{0}\033[0m'.format(diff)
            print '\033[91mPositionsfehler!\033[0m'
            #raise ValueError('Positionsfehler!')
