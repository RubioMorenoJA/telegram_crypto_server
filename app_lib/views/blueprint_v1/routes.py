from flask import Blueprint
from app_lib.views.blueprint_v1.coin_data import general_page


blueprint = Blueprint('api_v1', __name__, url_prefix='/api/v1')


@blueprint.route('/bitcoin', methods=['GET'])
def bitcoin_data():
    return general_page('BTC', 'Bitcoin', 'bitcoin')


@blueprint.route('/ethereum', methods=['GET'])
def ethereum_data():
    return general_page('ETH', 'Ethereum', 'ethereum')


@blueprint.route('/cardano', methods=['GET'])
def cardano_data():
    return general_page('ADA', 'Cardano', 'cardano')


@blueprint.route('/tron', methods=['GET'])
def tron_data():
    return general_page('TRX', 'Tron', 'tron')
