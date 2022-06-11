from app import app, args, ssl_context

if __name__ == "__main__":
    # load_dotenv=False because we want to load earlier than this
    app.run(host=args.host, port=args.port, debug=False, load_dotenv=False, ssl_context=ssl_context)