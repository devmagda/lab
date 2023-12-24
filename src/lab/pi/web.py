from math import sqrt

from flask import Flask, render_template, request, jsonify

from electronics import TrackController

app = Flask(__name__)

tank_controller = TrackController.from_config()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tank/steering', methods=['POST'])
def tank_steering():
    data = request.get_json()

    if 'x' not in data or 'y' not in data or 'direction' not in data:
        return jsonify({'error': 'Invalid input. Ensure x, y, and direction are provided.'}), 400

    try:
        x = float(data['x'])
        y = float(data['y'])
    except ValueError:
        return jsonify({'error': f'Invalid input. Either {x} or {y} is not numeric.'})
    direction = data['direction']

    tank_controller.directions(x, y, direction)

    app.logger.info(f'X: {x} Y: {y} Direction: {direction}')

    # Process the input as needed (e.g., control the tank based on x, y, and direction)

    # Return a response (you can customize this based on your application's logic)
    return jsonify({'message': 'Tank steering command received successfully'})


# @app.route('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
