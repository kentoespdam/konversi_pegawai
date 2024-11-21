from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from multiprocessing import Manager, Pool
import random
import time
from icecream import ic


def task(d, session_id, number, repeat_count):

    success = 0
    fail = 0

    while success+fail < repeat_count:
        time.sleep(random.random()*2.0)
        if (random.random()*100) > 98.0:
            fail += 1
        else:
            success += 1

        d[session_id] = {
            "success": success,
            "fail": fail,
            "number": number,
            "repeat_count": repeat_count
        }
    return


pool = Pool()
manager = Manager()
dictionary = manager.dict()


class Server(BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200, content_type='application/json'):
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_HEAD(self):
        self._set_headers()

    def do_GET(self):
        self._set_headers()
        response = {'hello': 'world', 'received': 'ok'}
        self.wfile.write(json.dumps(response).encode('utf-8'))

    def do_POST(self):
        """Handle POST request."""
        if self.headers['Content-Type'] != 'application/json':
            self._set_headers(400)
            return

        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length).decode('utf-8')
        request_data = json.loads(body)
        request_data["status"] = ""
        request_data["started_at"] = time.ctime()
        # ic(request_data)

        if 'runtask' in request_data:
            self._handle_run_task(request_data)
        elif 'session_id' in request_data:
            self._handle_get_status(request_data)

        request_data["ended_at"] = time.ctime()
        ic(request_data["started_at"], request_data["ended_at"])
        self._set_headers()
        self.wfile.write(json.dumps(request_data).encode('utf-8'))

    def _handle_run_task(self, request_data):
        """Start a task in a separate thread."""
        session_id = request_data['session_id']
        number = 1
        repeat_count = 2
        print(f"Starting task with {session_id}, {number}, {repeat_count}")
        duration = random.random(1, 5)
        time.sleep(duration)
        self.pool.apply_async(
            task, (self.dictionary, session_id, number, repeat_count))

    def _handle_get_status(self, request_data):
        """Update the request with the current status of the task."""
        session_id = request_data['session_id']
        request_data['status'] = session_id


def run_server(port=8008):
    """Run the server."""
    server_address = ('', port)
    with HTTPServer(server_address, Server) as httpd:
        print(f"Serving on port {port}...")
        httpd.serve_forever()


if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run_server(port=int(argv[1]))
    else:
        run_server()
