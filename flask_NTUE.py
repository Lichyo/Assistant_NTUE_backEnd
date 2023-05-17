from flask import Flask, request
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/done')
def my_program():
    arg1 = request.args.get('account')
    arg2 = request.args.get('password')
    import download_NTUE as dl
    result = dl.download(arg1, arg2)
    return result


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000, threaded=False)