import cPickle as pickle

from traits.api import HasTraits, Instance, Dict, Str, Int, Property, WeakRef
from pyface.gui import GUI

import zmq


class ZmqProvider(HasTraits):

    application = WeakRef

    host = Str('127.0.0.1')
    data_port = Int(9001)
    handshake_port = Int(9002)
    poll_period = Int(500)
    poll_timeout = Int(250)

    data_string = Property
    handshake_string = Property

    _zmq_context = Instance('zmq.Context')

    _poller = Instance('zmq.Poller')

    _handshake_socket = Instance('zmq.Socket')

    _data_socket = Instance('zmq.Socket')

    _pid_mapping = Dict(Int, WeakRef)

    def _get_handshake_string(self):
        return 'tcp://{0}:{1}'.format(self.host, self.handshake_port)

    def _get_data_string(self):
        return 'tcp://{0}:{1}'.format(self.host, self.data_port)

    def start(self):
        self._zmq_context = zmq.Context()
        self._poller = zmq.Poller()

        self._handshake_socket = self._zmq_context.socket(zmq.REP)
        self._handshake_socket.bind(self.handshake_string)
        self._data_socket = self._zmq_context.socket(zmq.SUB)
        self._data_socket.setsockopt(zmq.SUBSCRIBE, '')
        self._data_socket.connect(self.data_string)

        self._poller.register(self._handshake_socket, zmq.POLLIN)
        self._poller.register(self._data_socket, zmq.POLLIN)

        GUI.invoke_after(self.poll_period, self._wait_for_data)

    def stop(self):
        self._pid_mapping = {}
        if self._data_socket is not None:
            self._data_socket.close()
        if self._handshake_socket is not None:
            self._handshake_socket.close()
        if self._zmq_context is not None:
            self._zmq_context.term()

    def _add_view(self, pid, profile, fields):
        from pikos.live.utils import get_model_for_profile
        model_class = get_model_for_profile(profile)
        model = model_class(pid=pid, profile=profile, fields=fields)
        self._pid_mapping[pid] = model
        # FIXME?
        self.application.active_window.central_pane.add_tab(model)

    def _handle_data(self):
        data = pickle.loads(self._data_socket.recv())
        if not isinstance(data, tuple) or len(data) != 3:
            return 0
        pid = data[0]
        if pid not in self._pid_mapping:
            return 0
        model = self._pid_mapping[pid]
        model.add_data(data)
        return 0

    def _handle_connection(self):
        handshake = pickle.loads(self._handshake_socket.recv())
        pid, profile, fields = handshake
        self._handshake_socket.send(pickle.dumps(True))
        self._add_view(pid, profile, fields)

    def _wait_for_data(self):
        next_poll = self.poll_period
        socks = dict(self._poller.poll(timeout=self.poll_timeout))
        if self._data_socket in socks and \
                socks[self._data_socket] == zmq.POLLIN:
            next_poll = self._handle_data()
        if self._handshake_socket in socks and \
                socks[self._handshake_socket] == zmq.POLLIN:
            self._handle_connection()
        GUI.invoke_after(next_poll, self._wait_for_data)
