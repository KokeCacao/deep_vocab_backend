

import argparse

print("Parsing Arguments...")
parser = argparse.ArgumentParser(prog="python app.py", description="Launch backend of DeepVocab")
parser.add_argument('--version', action='version', version='%(prog)s v0.1')
parser.add_argument('--verbose', '-v', dest='verbose', action='count', default=0) # -vvv
parser.add_argument('--database', '-b', dest='database', default='/home/ubuntu/dev/database/deep_vocab.db', type=str, nargs='?', help='database file location, default /home/ubuntu/dev/database/deep_vocab.db')
parser.add_argument('--csv', '-c', dest='csv', default='/home/ubuntu/dev/database/data.csv')

args = parser.parse_args()

if __name__ == "__main__":
    from project import app
    app.run(host='0.0.0.0', port=5000, debug=False, ssl_context=('/etc/letsencrypt/live/kokecacao.me/cert.pem', '/etc/letsencrypt/live/kokecacao.me/privkey.pem'))