from django import template
register = template.Library()

try:
    from Crypto.Cipher import AES
    import base64
    from rek import settings

    BLOCK_SIZE = 16


    secret = settings.SECRET_KEY[:BLOCK_SIZE]
    cipher = AES.new(secret)

    PADDING = '{'
    pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING

    EncodeAES = lambda c, s: base64.urlsafe_b64encode(c.encrypt(pad(s)))
    DecodeAES = lambda c, e: c.decrypt(base64.urlsafe_b64decode(e)).rstrip(PADDING)

    @register.simple_tag
    def aes_code(something):
        something = str(something)
        return EncodeAES(cipher, something)[:-2]

    @register.simple_tag
    def aes_decode(encoded):
        return DecodeAES(cipher, str(encoded + '=='))

except Exception:
    @register.simple_tag
    def aes_code(something):
        return something

    @register.simple_tag
    def aes_decode(encoded):
        return encoded


