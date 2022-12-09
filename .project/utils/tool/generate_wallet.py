from models import WalletModel
from exts import db
from tronpy import Tron
from utils.tool.QR_code import generate_QR_code


# connect to the Tron blockchain
client = Tron()

# create a Tron wallet and print out the wallet address & private key
def create_wallet():
    wallet = client.generate_address()
    return {'address': wallet['base58check_address'], 'secret': wallet['private_key']}


def generate_wallet(wallet_num=100):
    wallet_list = []
    for i in range(wallet_num):
        wallet_obj = WalletModel()
        wallet_data = create_wallet()
        address = wallet_data['address']
        secret = wallet_data['secret']
        wallet_obj.address = address
        wallet_obj.secret = secret
        wallet_obj.network = 'tron'
        wallet_list.append(wallet_obj)

    for wallet in wallet_list:
        generate_QR_code(wallet.address)

    db.session.add_all(wallet_list)
    db.session.commit()



