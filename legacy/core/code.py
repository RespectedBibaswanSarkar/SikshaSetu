import zlib

BASE32_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"

def base32_encode(data):
    if not data:
        return ''
    result = []
    buffer = 0
    bits = 0
    for b in data:
        buffer = (buffer << 8) | (b & 0xFF)
        bits += 8
        while bits >= 5:
            bits -= 5
            idx = (buffer >> bits) & 0x1F
            result.append(BASE32_ALPHABET[idx])
    if bits > 0:
        idx = (buffer << (5 - bits)) & 0x1F
        result.append(BASE32_ALPHABET[idx])
    s = ''.join(result)
    groups = [s[i:i+4] for i in range(0, len(s), 4)]
    return ' '.join(groups)

def base32_decode(s):
    s = s.replace(' ', '').replace('-', '').upper()
    result = bytearray()
    buffer = 0
    bits = 0
    for c in s:
        if c not in BASE32_ALPHABET:
            continue
        val = BASE32_ALPHABET.index(c)
        buffer = (buffer << 5) | val
        bits += 5
        if bits >= 8:
            bits -= 8
            result.append((buffer >> bits) & 0xFF)
    return bytes(result)

def encode_mastery(mastery_vector, student_id="STU1", session_num=1, learner_speed=128):
    # mastery_vector: list of floats 0-1, 30 concepts -> 30*4 = 120 bits = 15 bytes
    bits = []
    for m in mastery_vector[:30]:
        val = int(round(max(0, min(1, float(m))) * 15))
        for i in range(3, -1, -1):
            bits.append((val >> i) & 1)
    while len(bits) < 120:
        bits.append(0)
    bits = bits[:120]
    data = bytearray()
    for i in range(0, len(bits), 8):
        byte = bits[i]*128 + bits[i+1]*64 + bits[i+2]*32 + bits[i+3]*16 + bits[i+4]*8 + bits[i+5]*4 + bits[i+6]*2 + bits[i+7]*1
        data.append(byte)
    meta = bytearray()
    sid = str(student_id)[:4].ljust(4, '0')
    for c in sid:
        meta.append(ord(c) & 0xFF)
    meta.append(session_num & 0xFF)
    meta.append(learner_speed & 0xFF)
    payload = bytes(data) + bytes(meta)
    crc = zlib.crc32(payload) & 0xFF
    final = payload + bytes([crc])
    return base32_encode(final)

def decode_mastery(code):
    try:
        data = base32_decode(code)
        if len(data) < 15 + 6 + 1:
            raise ValueError("Invalid code")
        crc = data[-1]
        payload = data[:-1]
        calc_crc = zlib.crc32(payload) & 0xFF
        if crc != calc_crc:
            raise ValueError("Checksum failed")
        mastery_bytes = payload[:15]
        meta = payload[15:21]
        try:
            student_id = meta[0:4].decode('ascii', errors='replace').strip('\x00')
        except:
            student_id = "STU1"
        session_num = meta[4]
        learner_speed = meta[5]
        bits = []
        for b in mastery_bytes:
            for i in range(7, -1, -1):
                bits.append((b >> i) & 1)
        mastery = []
        for i in range(0, 120, 4):
            if i+3 < len(bits):
                val = bits[i]*8 + bits[i+1]*4 + bits[i+2]*2 + bits[i+3]*1
            else:
                val = 0
            mastery.append(val / 15.0)
        while len(mastery) < 30:
            mastery.append(0.0)
        mastery = mastery[:30]
        return {
            'mastery': mastery,
            'student_id': student_id,
            'session_num': session_num,
            'learner_speed': learner_speed,
            'valid': True
        }
    except Exception as e:
        return {'valid': False, 'error': str(e)}
