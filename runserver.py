from flask import Flask, jsonify, request, abort, render_template, flash, redirect, url_for
from pokemon_service import PokemonService, LoginError
import json
import time

app = Flask(__name__)
app.secret_key = 'IlikeBigButtsAndICannotLie'

@app.route('/pokemon', methods=['POST'])
def pokemon():
  body = request.get_json(force=True)
  print json.dumps(body, indent=2)
  try:
    pokemon_service = PokemonService(
      body['auth_service'],
      body.get('username', ''),
      body['password'],
      float(body['lat']),
      float(body['lon']))
    return jsonify(pokemon_service.get_pokemon())
  except LoginError:
    return abort(401)


@app.route("/data_table", methods=['POST'])
def data_table():
  try:
    pokemon_service = PokemonService(
      request.form.get('auth_service', ''),
      request.form.get('username', ''),
      request.form.get('password', ''),
      float(request.form.get('lat', 0)),
      float(request.form.get('lon', 0))
    )
    time.sleep(2)
    return render_template('data_table.html',
      data=pokemon_service.get_pokemon(),
      keys=pokemon_service.get_pokemon_keys())
  except LoginError as e:
    flash(e.message)
    return redirect(url_for('index'))
  except KeyError as e:
    print str(e)
    flash(str(e))
    return redirect(url_for('index'))

@app.route("/", methods=['GET'])
def index():
  return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
