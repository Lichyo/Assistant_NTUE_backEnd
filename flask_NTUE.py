from flask import Flask, request
import download_NTUE as dl
app = Flask(__name__)

@app.route('/')
def my_program():
    arg1 = request.args.get('account')
    arg2 = request.args.get('password')
    result = dl.download(arg1, arg2)
    return result

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5001, threaded=False)