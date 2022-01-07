
import argparse

print("Parsing Arguments...")
parser = argparse.ArgumentParser(prog="python app.py", description="Launch backend of DeepVocab")
parser.add_argument('--version', action='version', version='%(prog)s v0.1')
parser.add_argument('--verbose', '-v', dest='verbose', action='count', default=0) # -vvv
parser.add_argument('--port', '-p', dest='port', default=5000, type=int, nargs='?', help='port number, default 5000')
parser.add_argument('--host', dest='host', default='0.0.0.0', type=str, nargs='?', help='host address, default 0.0.0.0')
parser.add_argument('--database', '-b', dest='database', default='/home/koke_cacao/Documents/Koke_Cacao/Database/deep_vocab.db', type=str, nargs='?', help='database file location, default /home/koke_cacao/Documents/Koke_Cacao/Database/deep_vocab.db')
parser.add_argument('--csv', '-c', dest='csv', default='/home/koke_cacao/Documents/Koke_Cacao/Python/WorkSpace/Barron3500/巴郎Sat3500-excel-original版(Linux).csv', type=str, nargs='?', help='csv file location, default /home/koke_cacao/Documents/Koke_Cacao/Python/WorkSpace/Barron3500/巴郎Sat3500-excel-original版(Linux).csv')

args = parser.parse_args()

if __name__ == "__main__":

    from project import app
    
    print("You are in DEBUG mode! Don't use it as production!")
    # if you want to use 80, see: https://gist.github.com/justinmklam/f13bb53be9bb15ec182b4877c9e9958d
    app.run(host=args.host, port=args.port, debug=True)

# TO RUN THIS PROJECT
# > conda activate web
# > python app.py

# TO RUN ANDROID APP
# sudo javaconfig
# (and choose 0, java 11)
# android-studio
# (use command prompt (zsh) to open android studio)

# TO CREATE DATABASE
# send this to http://127.0.0.1:5000/graphql
# mutation {
#     test(key: "Koke_Cacao 's secret key", action: "add to db") {
#         success
#     }
# }
# and you should recieve
# {
#     "data": {
#         "test": {
#             "success": true
#         }
#     },
#     "extensions": {},
#     "errors": null
# }