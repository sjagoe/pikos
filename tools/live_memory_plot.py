import cPickle as pickle

import zmq

from traits.api import HasTraits, Str, Any, Int, Instance

from pikos.recorders.zeromq_recorder import RecordingStopped


class LivePlot(HasTraits):

    context = Instance(zmq.Context, args=())
    prepare_socket = Any
    data_socket = Any

    poller = Any

    host = Str('127.0.0.1')
    port = Int(9001)

    def _prepare_socket_default(self):
        return self.context.socket(zmq.REQ)

    def _data_socket_default(self):
        return self.context.socket(zmq.SUB)

    def _poller_default(self):
        poller = zmq.Poller()
        poller.register(self.data_socket, zmq.POLLIN)
        return poller

    def init(self, info):
        self.data_socket.connect('tcp://{0}:{1}'.format(self.host, self.port))
        self.data_socket.setsockopt(zmq.SUBSCRIBE, '')
        self.prepare_socket.connect(
                'tcp://{0}:{1}'.format(self.host, self.port+1))
        ready = False
        while not ready:
            self.prepare_socket.send(pickle.dumps(True))
            ready = pickle.loads(self.prepare_socket.recv())
        self.prepare_socket.close()


if __name__ == '__main__':
    live_plot = LivePlot()
    live_plot.init(None)

    while True:
        socks = dict(live_plot.poller.poll(timeout=0))
        data = None
        if live_plot.data_socket in socks and \
                socks[live_plot.data_socket] == zmq.POLLIN:
            data = pickle.loads(live_plot.data_socket.recv())
            if isinstance(data, RecordingStopped):
                break
            print data
