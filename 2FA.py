from flask import Flask, render_template_string, request
import pyotp, qrcode, io, base64

app = Flask(__name__)
secret_store = {}
HTML='''<!doctype html><html><body><h2>2FA Flask App</h2><form method="post">Username:<input name="username"><button type="submit">Generate</button></form>{% if qr %}<img src="data:image/png;base64,{{qr}}"><p>Secret: {{secret }}</p><form method="post" action="/verify"><input type="hidden" name="secret" value="{{secret}}"><input name="otp" placeholder="Enter OTP"><button type="submit">Verify</button></form>{% endif %}<p>{{msg}}</p></body></html>'''
@app.route('/', methods=['GET','POST'])
def home():
    qr=None; secret=''; msg=''
    if request.method=='POST':
        username=request.form['username']
        secret=pyotp.random_base32()
        uri=pyotp.TOTP(secret).provisioning_uri(name=username, issuer_name='YourApp')
        img=qrcode.make(uri)
        buf=io.BytesIO(); img.save(buf, format='PNG')
        qr=base64.b64encode(buf.getvalue()).decode()
    return render_template_string(HTML, qr=qr, secret=secret, msg=msg)
@app.route('/verify', methods=['POST'])
def verify():
    secret=request.form['secret']; otp=request.form['otp']
    ok=pyotp.TOTP(secret).verify(otp)
    return render_template_string(HTML, qr=None, secret='', msg='Verified Successfully' if ok else 'Invalid OTP')
if __name__=='__main__':
    app.run(host='0.0.0.0', port=5000)
