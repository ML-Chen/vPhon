from flask import Flask, render_template, request, jsonify, Response
from flask_restful import reqparse
import subprocess

app = Flask(__name__)

@app.route('/')
def home() -> Response:
    return render_template('index.html')

@app.route('/convert', methods=['GET'])
def convert() -> Response:
    parser = reqparse.RequestParser(bundle_errors=True)
    parser.add_argument('text', type=str, required=True)
    parser.add_argument('dialect', choices=('n', 'c', 's'), required=True)
    parser.add_argument('tones', choices=('6', '8', 'tl'))
    parser.add_argument('palatals', type=bool)
    parser.add_argument('glottal', type=bool)
    parser.add_argument('tokenize', type=bool)
    parser.add_argument('delimit', type=str)
    args = parser.parse_args()

    print(f'Converting {args}…')

    try:
        output = _convert(args['text'], args['dialect'], args['tone'], args['palatals'], args['glottal'], args['tokenize'], args['delimit'])
        return output, 200
    except Exception as e:
        message = 'Unknown error: ' + repr(e)
        print('Error: ' + message)
        return {'message': message}, 400

def _convert(text: str, dialect: str, tones: str = '', palatals: bool = False, glottal: bool = False, tokenize: bool = False, delimit: str = '') -> str:
    pipe = subprocess.Popen(["echo", text], stdout = subprocess.PIPE)
    output = subprocess.check_output([f"""
        ../vPhon.py
        -d {dialect}
        {'-{tones}' if tones else ''}
        {'-p' if palatals else ''}
        {'-g' if glottal else ''}
        {'-t' if tokenize else ''}
        {'-m {delimit}' if delimit else ''}
        """], stdin=pipe.stdout)
    print('_convert:' + output)
    return output

if __name__ == '__main__':
    app.run(debug=True)