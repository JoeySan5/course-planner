from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/', methods=['POST'])
def receive_data():
    # JSON 데이터 수신
    data = request.json
    print("Received Data:", data)
    
    # 성공 메시지 응답
    return jsonify({"message": "Data received successfully!"}), 200

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
