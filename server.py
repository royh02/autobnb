from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
# from browser_agent import main as browser_agent_main

app = Flask(__name__)
CORS(app)

@app.route('/search', methods=['POST'])
def search():
    data = request.json
    query = data.get('query')
    
    print('hihihi', data)
    
    # if not query:
    #     return jsonify({'error': 'No query provided'}), 400
    
    # try:
    #     # Run the browser agent with the search query
    #     asyncio.run(browser_agent_main(query))
    #     return jsonify({'message': 'Search initiated successfully'}), 200
    # except Exception as e:
    #     return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
