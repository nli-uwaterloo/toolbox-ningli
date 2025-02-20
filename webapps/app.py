from flask import Flask, request, render_template

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        user_input = request.form.get("input_data")
        result = process_data(user_input)  # Call your existing function
        return render_template("index.html", result=result)

    return render_template("index.html", result=None)

def process_data(user_input):
    return f"Processed: {user_input}"  # Replace with your actual logic

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=8000)
