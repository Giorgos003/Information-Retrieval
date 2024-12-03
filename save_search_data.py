import json
from http.server import BaseHTTPRequestHandler, HTTPServer


class SimpleRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Get the content length and read the data
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        # Parse the JSON data from the request
        try:
            data = json.loads(post_data.decode('utf-8'))
            search_query = data.get('search_query', '').strip()


            if search_query:
                # Append the search query to the file
                with open('searchBarData.txt', 'a') as file:
                    file.write(search_query + '\n')
                print(f"Saved query: {search_query}")  # Debugging print statement

                # Respond with a success message
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"Search query saved successfully!")
            else:
                # If there's no search query, respond with an error
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"Bad Request: No search query provided")

        except Exception as e:
            # In case of JSON parsing error or any other exception, respond with an error
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(f"Error: {str(e)}".encode())


def run(server_class=HTTPServer, handler_class=SimpleRequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()


if __name__ == '__main__':
    run()
