from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/", methods=["POST"])
def echo():
    try:
        data = request.json
        data[
            "context"
        ] = """For example, for 'Hello' you should return 'やあ！(Ya!)'. For 'How are you?' you should return '元気?' (Genki?) """
        return jsonify(data)
    except Exception as exception:
        return jsonify(error=f"{exception}"), 400


if __name__ == "__main__":
    app.run(debug=True)
