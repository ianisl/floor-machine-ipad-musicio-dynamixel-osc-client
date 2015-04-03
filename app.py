import sys
import rtmidi
import threading
import OSC

# Settings
sendAdress = '169.254.0.2', 8000

def process_message(midi, port):
    if midi.isController():
        global dxlIO, foundIds
        value = midi.getControllerValue()
        cc = midi.getControllerNumber()
        print '%s: cc' % port, midi.getControllerNumber(), value
        address = ""
        if cc == 0:
            address = "/wheelspeed"
        elif cc == 1:
            address = "/wheelslowdown"
        elif cc == 2:
            address = "/dremeljointpos"
        elif cc == 3:
            address = "/dremeljointspeed"
        message = OSC.OSCMessage()
        message.setAddress(address)
        message.append(value)
        client.send(message)


class Collector(threading.Thread):
    def __init__(self, device, port):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.port = port
        self.portName = device.getPortName(port)
        self.device = device
        self.quit = False

    def run(self):
        self.device.openPort(self.port)
        self.device.ignoreTypes(True, False, True)
        while True:
            if self.quit:
                return
            msg = self.device.getMessage(250)
            if msg:
                process_message(msg, self.portName)

# Init OSC client
client = OSC.OSCClient()
client.connect(sendAdress)
# Init midi ports
dev = rtmidi.RtMidiIn()
collectors = []
for i in range(dev.getPortCount()):
    device = rtmidi.RtMidiIn()
    print 'OPENING',dev.getPortName(i)
    collector = Collector(device, i)
    collector.start()
    collectors.append(collector)

print 'HIT ENTER TO EXIT'
sys.stdin.read(1)
for c in collectors:
    c.quit = True
