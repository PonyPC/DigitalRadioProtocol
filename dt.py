import zlib
import binascii

SOH = b"\xFC"
EOT = b"\xFD"
ESC = b"\xFE"
FRAME_SIZE = 512 - 4 # start(1), pack number(1), pack length(1), end(1)
#max data size = 0xFB * FRAME_SIZE = 251 * 506 = 127006

def crcbin(crc):
	return crc.to_bytes(length=4, byteorder='big', signed=False)

def crcint(crc):
	return int.from_bytes(crc, byteorder='big', signed=False)

def send(data):
	zipped_data = zlib.compress(data, zlib.Z_BEST_COMPRESSION)
	zipped_data += crcbin(zlib.crc32(zipped_data))
	data = zipped_data.replace(ESC, ESC + ESC).replace(SOH, ESC + SOH).replace(EOT, ESC + EOT)
	frames = []
	index = 0
	while index < len(data):
		if index + FRAME_SIZE < len(data): # 在正确编码的情况下，如果数据结尾是ESC，那肯定会有一个前导ESC，所以不检查等于的情况
			tmp = data[index:index + FRAME_SIZE]
			index += FRAME_SIZE
			shrink = False
			for i in range(1, len(tmp) + 1):
				if tmp[-i] != ESC[0]:
					break
				shrink = not shrink
			if shrink:
				tmp = tmp[:-1]
				index -= 1
			frames.append(tmp)
		else:
			frames.append(data[index:])
			break
	frame_len = len(frames)
	if frame_len > 251:
		return []
	frame_len_byte = (frame_len - 1).to_bytes(length=1, byteorder='big', signed=False)
	for i in range(frame_len):
		frames[i] = SOH + i.to_bytes(length=1, byteorder='big', signed=False) + frame_len_byte + frames[i] + EOT
	return frames

def recv(data):
	index = 0
	starti = -1
	escaped = False
	buffer = []
	while index < len(data):
		if data[index] == ESC[0]:
			escaped = not escaped
		else:
			if not escaped:
				if data[index] == SOH[0]:
					starti = index
				elif data[index] == EOT[0]:
					if starti != -1:
						tmp = data[starti + 1:index]
						starti = -1
						if len(tmp) > 2:
							seq = tmp[0]
							count = tmp[1] + 1
							if count != len(buffer):
								buffer = []
								for i in range(count):
									buffer.append(b'')
							buffer[seq] = tmp[2:].replace(ESC + SOH, SOH).replace(ESC + EOT, EOT).replace(ESC + ESC, ESC)
							if seq + 1 == count:
								zipped = b''
								failed = False
								for x in buffer:
									if x == b'':
										failed = True
										break
									else:
										zipped += x
								if not failed:
									if len(zipped) > 4:
										crc = zipped[-4:]
										zipped = zipped[:-4]
										if zlib.crc32(zipped) == crcint(crc):
											unzipped_data = zlib.decompress(zipped)
											print(unzipped_data)
			escaped = False
		index += 1

x = send(b'fudiovu8f7ag89e7a8r93ng88a97f97b7kf0z80-3890241k.3rjl.erkjfdsguvfd900bgfdua89g7nf8d7abvf678d7v89d7f89ga7ed89g9fhda6g876d78f6h78dh06a6fd780bhv0jfz8b7g0fd6j8b7j6fg78j6f7d8jbn6f7fs89bm7f8907sg897fn0ga78rn07a8g90789fk709s8a79rf7gan987ra8n907t98m7c489n7c5q8923n789c57nq890dj7r98ew78vt678ea6jt78ve6jv7qt87ew897qrck89e7q89njv7t89erq78r9n78we9n7qcr8ew89qtn7b9vjt7r8ewb6y78jre6w78t7v89er7m8n95tv734n89q57890qm7b897r89qw07bt80rje678t9jv78q9rej7t8b97q98n7v74859nq839fm758943q5t89vj7r8q9t7j9rje7a8r93ng88a97f97b7kf0z80-3890241k.3rjl.erkjfdsguvfd900bgfdua89g7nf8d7abvf678d7v89d7f89ga7ed89g9fhda6g876d78f6h78dh06a6fd780bhv0jfz8b7g0fd6j8b7j6fg78j6f7d8jbn6f7fs89bm7f8907sg897fn0ga78rn07a8g90789fk709s8a79rf7gan987ra8n907t98m7c489n7c5q8923n789c57nq890dj7r98ew78vt678ea6jt78ve6jv7qt87ew897qrck89e7q89njv7t89erq78r9n78we9n7qcr8ew89qtn7b9vjt7r8ewb6y78jre6w78t7v89er7m8n95tv734n89q57890qm7b897r89qw07bt80rje678t9jv78q9rej7t8b97q98n7v74859nq839fm758943q5t89vj7r8q9t7j9rje7a8r93ng88a97f97b7kf0z80-3890241k.3rjl.erkjfdsguvfd900bgfdua89g7nf8d7abvf678d7v89d7f89ga7ed89g9fhda6g876d78f6h78dh06a6fd780bhv0jfz8b7g0fd6j8b7j6fg78j6f7d8jbn6f7fs89bm7f8907sg897fn0ga78rn07a8g90789fk709s8a79rf7gan987ra8n907t98m7c489n7c5q8923n789c57nq890dj7r98ew78vt678ea6jt78ve6jv7qt87ew897qrck89e7q89njv7t89erq78r9n78we9n7qcr8ew89qtn7b9vjt7r8ewb6y78jre6w78t7v89er7m8n95tv734n89q57890qm7b897r89qw07bt80rje678t9jv78q9rej7t8b97q98n7v74859nq839fm758943q5t89vj7r8q9t7j9rje7a8r93ng88a97f97b7kf0z80-3890241k.3rjl.erkjfdsguvfd900bgfdua89g7nf8d7abvf678d7v89d7f89ga7ed89g9fhda6g876d78f6h78dh06a6fd780bhv0jfz8b7g0fd6j8b7j6fg78j6f7d8jbn6f7fs89bm7f8907sg897fn0ga78rn07a8g90789fk709s8a79rf7gan987ra8n907t98m7c489n7c5q8923n789c57nq890dj7r98ew78vt678ea6jt78ve6jv7qt87ew897qrck89e7q89njv7t89erq78r9n78we9n7qcr8ew89qtn7b9vjt7r8ewb6y78jre6w78t7v89er7m8n95tv734n89q578vt678ea6jt78ve6jv7qt87ew897qrckej7t8b97q98n7v74859nq839fm758943q5t89vj7r8q9t7j9rje7a8r93ng88a97f97b7kf0z80-3890241k.3rjl.erkjfdsguvfd900bgfdua89g7nf8d7abvf678d7v89d7f89ga7ed89g9fhda6g876d78f6h78dh06a6fd780bhv0jfz8b7g0fd6j8b7j6fg78j6f7d8jbn6f7fs89bm7f8907sg897fn0ga78rn07a8g90789fk709s8a79rf7gan987ra8n907t98m7c489n7c5q8923n789c57nq890dj7r98ew78vt678ea6jt78ve6jv7qt87ew897qrck89e7q89njv7t89erq78r9n78we9n7qcr8ew89qtn7b9vjt7r8ewb6y78jre6w78t7v89er7m8n95tv734n89q578vt678ea6jt78ve6jv7qt87ew897qrck89e7q89njv7t89erq78r9n78we9n7qcr8ew89qtn7b9vjt7r8ewb6y78jre6w78t7v89er7m8n95tv734n89q57890qm7b897r89qw07bt80rje678t9jv78q9rej7t8b97q98n7v74859nq839fm758943q5t89vj7r8q9t7j9rje7a8r93ng88a97f97b7kf0z80-3890241k.3rjl.erkjfdsguvfd900bgfdua89g7nf8d7abvf678d7v89d7f89ga7ed89g9fhda6g876d78f6h78dh06a6fd780bhv0jfz8b7g0fd6j8b7j6fg78j6f7d8jbn6f7fs89bm7f8907sg897fn0ga78rn07a8g90789fk709s8a79rf7gan987ra8n907t98m7c489n7c5q8923n789c57nq890dj7r98ew78vt678ea6jt78ve6jv7qt87ew897qrck89e7q89njv7t89erq78r9n78we9n7qcr8ew89qtn7b9vjt7r8ewb6y78jre6w78t7v89er7m8n95tv734n89q578vt678ea6jt78ve6jv7qt87ew897qrck89e7q89njv7t89erq78r9n78we9n7qcr8ew89qtn7b9vjt7r8ewb6y78jre6w78t7v89er7m8n95tv734n89q57890qm7b897r89qw07bt80rje678t9jv78q9rej7t8b97q98n7v74859nq839fm758943q5t89vj7r8q9t7j9rje7a8r93ng88a97f97b7kf0z80-3890241k.3rjl.erkjfdsguvfd900bgfdua89g7nf8d7abvf678d7v89d7f89ga7ed89g9fhda6g876d78f6h78dh06a6fd780bhv0jfz8b7g0fd6j8b7j6fg78j6f7d8jbn6f7fs89bm7f8907sg897fn0ga78rn07a8g90789fk709s8a79rf7gan987ra8n907t98m7c4n7c5q8923n789c57nq890dj7r98ew78vt678ea6jt78ve6jv7qt87ew897qrck89e7q89njv7t89erq78r9n78we9n7qcr8ew89qtn7b9vjt7r8ewb6y78jre6w78t7v89er7m8n95tv734n89q578vt678ea6jt78ve6jv7qt87ew897qrck89e7q89njv7t89erq78r9n78we9n7qcr8ew89qtn7b9vjt7r8ewb6y78jre6w78t7v89er7m8n95tv734n89q57890qm7b897r89qw07bt80rje678t9jv78q9rej7t8b97q98n7v74859nq839fm758943q5t89vj7r8q9t7j9rje7a8r93ng88a97f97b7kf0z80-3890241k.3rjl.erkjfdsguvfd900bgfdua89g7nf8d7abvf678d7v89d7f89ga7ed89g9fhda6g876d78f6h78dh06a6fd780bhv0jfz8b7g0fd6j8b7j6fg78j6f7d8jbn6f7fs89bm7f8907sg897fn0ga78rn07a8g90789fk709s8a79rf7gan987ra8n907t98m7c4n7c5q8923n789c57nq890dj7r98ew78vt678ea6jt78ve6jv7qt87ew897qrck89e7q89njv7t89erq78r9n78we9n7qcr8ew89qtn7b9vjt7r8ewb6y78jre6w78t7v89er7m8n95tv734n89q578vt678ea6jt78ve6jv7qt87ew897qrck89e7q89njv7t89erq78r9n78we9n7qcr8ew89qtn7b9vjt7r8ewb6y78jre6w78t7v89er7m8n95tv734n89q57890qm7b897r89qw07bt80rje678t9jv78q9rej7t8b97q98n7v74859nq839fm758943q5t89vj7r8q9t7j9rje7a8r93ng88a97f97b7kf0z80-3890241k.3rjl.erkjfdsguvfd900bgfdua89g7nf8d7abvf678d7v89d7f89ga7ed89g9fhda6g876d78f6h78dh06a6fd780bhv0jfz8b7g0fd6j8b7j6fg78j6f7d8jbn6f7fs89bm7f8907sg897fn0ga78rn07a8g90789fk709s8a79rf7gan987ra8n907t98m7c4n7c5q8923n789c57nq890dj7r98ew78vt678ea6jt78ve6jv7qt87ew897qrck89e7q89njv7t89erq78r9n78we9n7qcr8ew89qtn7b9vjt7r8ewb6y78jre6w78t7v89er7m8n95tv734n89q578vt678ea6jt78ve6jv7qt87ew897qrck89e7q89njv7t89erq78r9n78we9n7qcr8ew89qtn7b9vjt7r8ewb6y78jre6w78t7v89er7m8n95tv734n89q57890qm7b897r89qw07bt80rje678t9jv78q9rej7t8b97q98n7v74859nq839fm758943q5t89vj7r8q9t7j9rje7a8r93ng88a97f97b7kf0z80-3890241k.3rjl.erkjfdsguvfd900bgfdua89g7nf8d7abvf678d7v89d7f89ga7ed89g9fhda6g876d78f6h78dh06a6fd780bhv0jfz8b7g0fd6j8b7j6fg78j6f7d8jbn6f7fs89bm7f8907sg897fn0ga78rn07a8g90789fk709s8a79rf7gan987ra8n907t98m7c489n7c5q8923n789c57nq890dj7r98ew78vt678ea6jt78ve6jv7qt87ew897qrck89e7q89njv7t89erq78r9n78we9n7qcr8ew89qtn7b9vjt7r8ewb6y78jre6w78t7v89er7m8n95tv734n89q57890qm7b897r89qw07bt80rje678t9jv78q9rej7t8b97q98n7v74859nq839fm758943q5t89vj7r8q9t7j9rje7a8r93ng88a97f97b7kf0z80-3890241k.3rjl.erkjfdsguvfd900bgfdua89g7nf8d7abvf678d7v89d7f89ga7ed89g9fhda6g876d78f6h78dh06a6fd780bhv0jfz8b7g0fd6j8b7j6fg78j6f7d8jbn6f7fs89bm7f8907sg897fn0ga78rn07a8g90789fk709s8a79rf7gan987ra8n907t98m7c489n7c5q8923n789c57nq890dj7r98ew78vt678ea6jt78ve6jv7qt87ew897qrck89e7q89njv7t89erq78r9n78we9n7qcr8ew89qtn7b9vjt7r8ewb6y78jre6w78t7v89er7m8n95tv734n89q57890qm7b897r89qw07bt80rje678t9jv78q9rej7t8b97q98n7v74859nq839fm758943q5t89vj7r8q9t7j9rje7wqv8t9rj7b8qn437589n32b89n8vq9nt89ena7v89t7e89a7t8bj789a7e97tdj67g98j7f89ag79e87tr8e067nq85bn374628n678154n3859n7t8347ytgr7a89ng7r89a-n7g8-8fag[z[asfu8d97vg89nf89g7r8q0ny4897nt89buf89ds8g97dfab08e7ch7nt89er7av8t9n7r89at789rej7ft8j60ert69c7r8e9n798n378q4b7nfc70ar8e7v89t0je8ra90vj7t8ewj708a90r7v3vn0873289n75849n7a8bnt8r9ea7vn9t8red70ang7f98a0-7r987tq849n8t97agn907r897nag89rn7a8t979w49nq7y8r97nesh89n7gt8d9xh78tg97hn6c78n6hk6cnghf5h678567fd85g678rg7heotuiq34h6ut4h3uiothoheurgyhr[gur0fdzsg0f9du89h789fs7g8hr7a8n78wn979m3c798qn547v8n7tq984n7qc89tm7r89nqw7b8964n37q6980n748930q5743n9b68437nq86n4387q7nb89547n8q9n-849n-qc79-427g')
d = b''
for i in x:
	d += i
recv(d)