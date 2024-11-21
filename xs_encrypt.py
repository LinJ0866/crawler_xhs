# https://github.com/Cloxl/xhshow/blob/master/encrypt/xs_encrypt.py

import base64
import hashlib
import json
import struct

# pip install pycryptodome
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

words = [1735160886, 1748382068, 1631021929, 1936684855]
key_bytes = b''.join(struct.pack('>I', word) for word in words)
iv = b'4hrivgw5s342f9b2'

def encrypt_text(text: str) -> str:
    """
    根据传入的text生成AES加密后的内容，并将其转为base64编码

    :param text: 需要加密的字符串
    :return: 加密后的base64编码字符串
    """
    text_encoded = base64.b64encode(text.encode())

    cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(text_encoded, AES.block_size))
    ciphertext_base64 = base64.b64encode(ciphertext).decode()

    return ciphertext_base64

def encrypt_payload(payload: str, platform: str) -> str:
    """
    把小红书加密参数payload转16进制 再使用base64编码

    :param payload: 要加密处理的payload内容
    :param platform: 登录平台
    :return: 加密后并进行base64编码的字符串
    """
    obj = {
        "signSvn": "55",
        "signType": "x2",
        "appID": platform,
        "signVersion": "1",
        "payload": base64_to_hex(payload)
    }
    return base64.b64encode(json.dumps(obj, separators=(',', ':')).encode()).decode()

def base64_to_hex(encoded_data):
    """
    把加密后的payload转为16进制

    :param encoded_data: 加密后的payload
    :return:
    """
    decoded_data = base64.b64decode(encoded_data)
    hex_string = ''.join([format(byte, '02x') for byte in decoded_data])
    return hex_string

def encrypt_xs(url: str, a1: str, ts: str, platform: str = 'xhs-pc-web') -> str:
    """
    将传入的参数加密为小红书的xs

    :param url: API请求的URL
    :param a1: 签名参数a1
    :param ts: 时间戳
    :param platform: 登录平台 默认为xhs-pc-web
    :return: 最终的加密签名字符串，前缀为“XYW_”
    """
    x1 = hashlib.md5(('url=' + url).encode('utf-8')).hexdigest()
    text = (f'x1={x1};'
            f'x2=0|0|0|1|0|0|1|0|0|0|1|0|0|0|0|1|0|0|0;'
            f'x3={a1};'
            f'x4={ts};')
    return 'XYW_' + encrypt_payload(encrypt_text(text), platform=platform)