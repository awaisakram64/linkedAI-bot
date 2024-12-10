from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def about():
    return 'Hello!'

@app.route('/create_post')
def home():
    author_id = request.args.get('author_id')
    is_page = request.args.get('is_page')
    emojies = request.args.get('emojies')
    state = request.args.get('state', 'PUBLISHED')
    # print(emojies)
    is_page = True if is_page == 'true' else False
    from src.linkedin_posting_bot.main import post_engine
    post_engine(author_id, is_page, emojies, state)
    
    return 'Post created'