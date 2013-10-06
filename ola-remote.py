#!/usr/bin/python
import threading
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import json
import sys
import os
import time
from ola.ClientWrapper import ClientWrapper

LISTENERS = []
NUM_PIXELS = 168
PIXEL_SIZE = 3
LED_POWER = 0.02
MAX_POWER = NUM_PIXELS * PIXEL_SIZE * LED_POWER
MAX_BRIGHT = NUM_PIXELS * PIXEL_SIZE * 255.0
SOURCES = ['OLA', 'Backup']

if os.path.exists('/dev/spidev0.0'):
    SPI_DEVICE = "/dev/spidev0.0";
else:
    SPI_DEVICE = "/dev/null"

BACKUP_FILE = "save.out"
AMP_LIMIT = 4.0

GAMMA = bytearray(256)
for i in range(256): GAMMA[i] = int(pow(float(i) / 255.0, 2.5) * 255.0)

root = os.path.dirname(__file__)


class OlaHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')


class BackupHandler(tornado.web.RequestHandler):
    def get(self, action):
        global ola_thread
        action = self.get_argument('action', 'none')
        if action == 'start':
            self.write('recording')
            print "backup recording started"
            ola_thread._backup.close()
            ola_thread._backup = open(BACKUP_FILE, 'wb')
            ola_thread._backup_mode = True
        elif action == 'stop':
            print "backup recording stopped"
            ola_thread._backup.close()
            ola_thread._backup = open(BACKUP_FILE, 'r')
            ola_thread._backup_data = bytearray(ola_thread._backup.read())
            ola_thread._backup_end = len(ola_thread._backup_data)
            ola_thread._backup_pos = 0
            ola_thread._backup_mode = False
            self.write('idle')
        else:
            self.write('invalid command')


class RealtimeHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        LISTENERS.append(self)
        print "new listener, now have %s listeners" % len(LISTENERS)

    def on_message(self, message):
        pass

    def on_close(self):
        LISTENERS.remove(self)


settings = {
    'auto_reload': True,
    'template_path': os.path.join(os.path.dirname(__file__), 'web')
}

application = tornado.web.Application([
                                          (r'/', OlaHandler),
                                          (r'/backup/(.*)', BackupHandler),
                                          (r'/realtime/', RealtimeHandler),
                                          (r'/(.*)', tornado.web.StaticFileHandler, {"path": os.path.join(os.path.dirname(__file__), 'web')})
                                      ], **settings)


class OlaThread(threading.Thread):
    def run(self):
        self._source = 0
        self._backup_pos = 0
        self._backup_mode = True if len(sys.argv) > 1 and sys.argv[1] == "-b" else False
        self._time_last = time.time()
        self._universe = 1

        if self._backup_mode:
            self._backup = open(BACKUP_FILE, 'wb')
            self._backup_data = bytearray()
        else:
            self._backup = open(BACKUP_FILE, 'r')
            self._backup_data = bytearray(self._backup.read())

        self._backup_end = len(self._backup_data)
        self._spidev = file(SPI_DEVICE, "wb")

        try:
            self._wrapper = ClientWrapper()
        except:
            print "Error: OLAd not running!"
            os._exit(1)

        self._client = self._wrapper.Client()
        self._client.RegisterUniverse(self._universe, self._client.REGISTER, self.Receive)
        if not self._backup_mode: self._wrapper.AddEvent(1000, self.CheckAlive)
        try:
            self._wrapper.Run()
        except:
            print "Error: Lost connection to OLAd!"
            os._exit(1)

    def Display(self, data):
        global LISTENERS, NUM_PIXELS, PIXEL_SIZE, GAMMA, MAX_BRIGHT, MAX_POWER, SOURCES

        self._spidev.flush()
        for listener in LISTENERS:
            listener.write_message(json.dumps({'source': SOURCES[self._source], 'data': list(data)}))

        pixel_values = bytearray(NUM_PIXELS * PIXEL_SIZE)

        frame_sum = 0
        for i in xrange(0, NUM_PIXELS * PIXEL_SIZE):
            pixel_values[i] = GAMMA[data[i]]
            frame_sum += pixel_values[i]

        frame_power = (frame_sum / MAX_BRIGHT) * MAX_POWER
        if frame_power > AMP_LIMIT:
            power_multiplier = 1 - ((frame_power - AMP_LIMIT) / frame_power)
            for i in xrange(0, NUM_PIXELS * PIXEL_SIZE):
                pixel_values[i] = int(pixel_values[i] * power_multiplier)

        self._spidev.write(pixel_values)
        self._spidev.flush()

    def Receive(self, data):
        self._time_last = time.time()
        if self._backup_mode:
            # if sum(data) == 0:
            #   print "Done saving."
            #   quit()
            self._backup.write(data[:NUM_PIXELS * PIXEL_SIZE])

        if sum(data) == 0:
            self._source = 1
            self.Display(self.GetBackup())
        else:
            self._source = 0
            self.Display(data)

    def GetBackup(self):
        global NUM_PIXELS, PIXEL_SIZE
        self._backup_pos += NUM_PIXELS * PIXEL_SIZE
        if self._backup_pos + NUM_PIXELS * PIXEL_SIZE >= self._backup_end: self._backup_pos = 0
        return self._backup_data[self._backup_pos:self._backup_pos + NUM_PIXELS * PIXEL_SIZE]

    # check to see if we are receiving data. if not play backup
    def CheckAlive(self):
        if time.time() - self._time_last > 5:
            self._source = 1
            self.Display(self.GetBackup())
            self._wrapper.AddEvent(1000 / 30, self.CheckAlive)
        else:
            self._wrapper.AddEvent(1000, self.CheckAlive)


if __name__ == "__main__":
    ola_thread = OlaThread()
    ola_thread.daemon = True
    ola_thread.start()
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8888)

    tornado.ioloop.IOLoop.instance().start()

