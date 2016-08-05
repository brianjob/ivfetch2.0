from pgoapi import PGoApi
import json

def _prefix_dicts(dictionaries, prefix):
  """ loops through list of dictionaries and adds a prefix to each key """
  for dictionary in dictionaries:
    keys = dictionary.keys()
    for key in keys:
      if key:
        dictionary[prefix + key] = dictionary[key]
        del dictionary[key]


with open('lookups/basic_attacks.json') as basic_attack_file:
  basic_attacks = json.load(basic_attack_file)
  _prefix_dicts(basic_attacks, "Basic ")

with open('lookups/charged_attacks.json') as charged_attack_file:
  charged_attacks = json.load(charged_attack_file)
  _prefix_dicts(charged_attacks, "Charged ")

with open('lookups/species_data.json') as species_data_file:
  species_data = json.load(species_data_file)

with open('lookups/battle_ranks.json') as battle_ranks_file:
  battle_ranks = json.load(battle_ranks_file)


def _add_pokemon_lookup_data(pokemons):
  for pokemon in pokemons:
    _add_species_data(pokemon)
    _add_basic_attack_data(pokemon)
    _add_charged_attack_data(pokemon)
    _add_battle_ranks_data(pokemon)

  return pokemon


def _add_species_data(pokemon):
  pokemon.update(_filter_by_field(species_data, '#', pokemon['pokemon_id']))
  return pokemon


def _add_basic_attack_data(pokemon):
  pokemon.update(_filter_by_field(basic_attacks, "Basic ID", pokemon['move_1']))
  return pokemon


def _add_charged_attack_data(pokemon):
  pokemon.update(_filter_by_field(charged_attacks, "Charged ID", pokemon['move_2']))
  return pokemon


def _add_battle_ranks_data(pokemon):
  pokemon.update(_filter_by_2_fields(battle_ranks, "Basic Atk", pokemon["Basic Name"], "Charge Atk", pokemon["Charged Name"]))
  return pokemon


def _filter_by_field(collection, field_name, value):
  """ searches collection for dictionary with field_name key equal to value and returns it
  returns an empty dictionary if no results found """
  results = filter(lambda x: x.get(field_name, None) == value, collection)
  if (len(results) > 0):
    return results[0]
  else: return {}


def _filter_by_2_fields(collection, field1_name, value1, field2_name, value2):
  """ searches collection for dictionary with field1_name key equal to value1 and field2_name key equal to value2
  returns an empty dictionary if no results found """
  results = filter(lambda x: x.get(field1_name, None) == value1 and x.get(field2_name, None) == value2, collection)
  if (len(results) > 0):
    return results[0]
  else: return {}


class PokemonService:
  def __init__(self, auth_service, username, password, lat, lon):
    self.api = PGoApi()
    self.login(auth_service, username, password, lat, lon)


  def login(self, auth_service, username, password, lat, lon):
    self.api.set_position(lat, lon, 0)
    self.api.login(auth_service, username, password)


  def get_player(self):
    return self.api.get_player()


  def get_inventory(self):
    return [x['inventory_item_data'] for x in self.api.get_inventory() \
                   .get('responses', {}).get('GET_INVENTORY', {}) \
                   .get('inventory_delta', {}).get('inventory_items', {}) if 'inventory_item_data' in x]


  def get_pokemon(self):
    pokemons = [x['pokemon_data'] for x in self.get_inventory() if 'pokemon_data' in x and 'is_egg' not in x['pokemon_data']]
    _add_pokemon_lookup_data(pokemons)
    return pokemons


  def get_candy(self):
    """ returns a dictionary where keys are the candy family id
    and values are candy count """
    candies = {}
    for inventory_item in [x['candy'] for x in self.get_inventory() if 'candy' in x]:
      candies[inventory_item['family_id']] = inventory_item['candy']
    return candies
