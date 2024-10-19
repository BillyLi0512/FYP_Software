import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GObject

class RTSPMediaFactory(GstRtspServer.RTSPMediaFactory):
    def __init__(self, **properties):
        super(RTSPMediaFactory, self).__init__(**properties)
        self.num_clients = 0

    def on_client_connected(self, factory, client):
        self.num_clients += 1
        print(f"Client connected, total clients: {self.num_clients}")

    def on_client_disconnected(self, factory, client):
        self.num_clients -= 1
        print(f"Client disconnected, total clients: {self.num_clients}")

def main():
    Gst.init(None)

    server = GstRtspServer.RTSPServer.new()
    factory = RTSPMediaFactory()
    factory.set_shared(True)
    factory.set_launch('( filesrc location=./1.mp4 ! qtdemux ! h264parse ! rtph264pay name=pay0 pt=96 )')
    server.get_mount_points().add_factory("/test", factory)

    factory.connect("client-connected", factory.on_client_connected)
    factory.connect("client-disconnected", factory.on_client_disconnected)

    server.attach(None)

    print("RTSP server started at rtsp://127.0.0.1:8554/test")
    GObject.MainLoop().run()

if __name__ == "__main__":
    main()