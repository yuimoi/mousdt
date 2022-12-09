from flask import Flask
import click
from models import AdminModel, WalletModel
from utils.function import bordered_text
from exts import db
import os
import shutil
import csv
import datetime


def register_cli(app: Flask):
    @app.cli.command('admin', with_appcontext=True)
    @click.option('--username', type=str, default='admin', help='Amin username')
    @click.option('--password', type=str, required=True, help='Amin password')
    def admin(username, password):
        if password == 'admin':
            print(bordered_text(' Please change a stronger password! '))
            return 0
        admin = AdminModel.query.filter(AdminModel.id == 1).first()
        admin.username = username
        admin.password = password
        db.session.commit()

        print(bordered_text(f'   success\nusername:{username} \npassword:{password} '))

    @app.cli.command('clear_data')
    def clear_data():
        current_dir = os.path.dirname(os.path.realpath(__file__))
        runtime_path = os.path.join(current_dir, 'runtime')
        sqlite_path = os.path.join(current_dir, 'database.db')
        QR_code_path = os.path.abspath(os.path.join(current_dir,"..","static","QR_code"))


        try:
            os.remove(sqlite_path)
            print(f"successfully delete: {sqlite_path}")
        except:
            print(f"fail to delete: {sqlite_path}")

        try:
            shutil.rmtree(runtime_path)
            print(f"successfully delete: {runtime_path}")
        except:
            print(f"fail to delete: {runtime_path}")

        try:
            shutil.rmtree(QR_code_path)
            print(f"successfully delete: {QR_code_path}")
        except:
            print(f"fail to delete: {QR_code_path}")

    @app.cli.command('dump_wallet', with_appcontext=True)
    def dump_wallet():
        output_basename = datetime.datetime.now().strftime("%Y%m%d%H%M%S_dumpwallet.csv")
        output_dir = os.path.join('runtime', 'dump_wallet')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        output_path = os.path.join(output_dir, output_basename)

        wallet_list = WalletModel.query.all()
        if not wallet_list:
            print(bordered_text(' no wallet in database '))
            exit()

        with open(output_path, 'w', newline='', encoding='UTF8') as f:
            wr = csv.writer(f)
            header = ['address', 'secret', 'balance']
            wr.writerow(header)
            for wallet in wallet_list:
                wr.writerow([wallet.address, wallet.secret, wallet.balance])
        print(bordered_text(f'successfully save to: {output_path} '))

