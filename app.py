from project import app

if __name__ == "__main__":
    # if you want to use 80, see: https://gist.github.com/justinmklam/f13bb53be9bb15ec182b4877c9e9958d
    app.run(host="0.0.0.0", port=5000, debug=True)

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