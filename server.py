import serial
from websockets.sync.server import serve
import threading

websocket_server = None
websocket_list = []

ser = serial.Serial(
	port='COM4', # Change this according to connection methods, e.g. /dev/ttyACM0
	baudrate = 115200,
	parity=serial.PARITY_NONE,
	stopbits=serial.STOPBITS_ONE,
	bytesize=serial.EIGHTBITS,
	timeout=1
)








def start_websocket_server():
	def handler(websocket):
		print(websocket)
		websocket_list.append(websocket)
		for message in websocket:
			message = str(message)
			if message.startswith("M"):
				ser.write(f"{message}\n".encode('utf-8'))

	global websocket_server
	with serve(handler, "192.168.100.154", 8000) as server:
		websocket_server = server
		server.serve_forever()



#start websocket server in thread
server_thread = threading.Thread(target=start_websocket_server)
server_thread.start()

print("Starting")

try:
	ser.write("M S\n".encode('utf-8'))
	while True:
		if ser.in_waiting > 0:
			inp = ser.read_until(b'\n', 1024).decode('utf-8')[:-1]
			
			for websocket in websocket_list:
				websocket.send(inp)

			# if inp[0] == 'U':
			# 	ulF, ulB, ulL, ulR = map(float, inp.split()[1:])
			# 	print(inp)
			# 	if ulF < 150: ser.write("M F\n".encode('utf-8'))
			# 	else: ser.write("M S\n".encode('utf-8'))
except KeyboardInterrupt: pass
except Exception as e:
	print(e)
finally:
	print("Stopping")
	for w in websocket_list: w.close()
	print("shutting down serrver")
	websocket_server.shutdown()
	server_thread.join()

	print("Done")