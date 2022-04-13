# script to translate binance transaction to reportable transaction with price
import argparse
import csv
import sys
import logging
import requests
import time
import json
from datetime import datetime

# ENUM
ACCOUNT = "Account"
TIME_UTC = "UTC_Time"
OPERATION = "Operation"
SYMBOL = "Coin"
CHANGE = "Change"
SPOT = "Spot"
COIN_FUTURES = "Coin-Futures"
USDT_FUTURES = "USDT-Futures"


# Futures Enum
FEE = "Fee"
FUNDING = "Funding Fee"
PROFIT_LOSS = "Realize profit and loss"
INSURANCE_FEE = "Insurance fund compensation"
fees = [
    FEE,
    FUNDING,
    INSURANCE_FEE
]
IN = "transfer_in"

DEPOSIT = "Deposit"
MARKET_DATA_URL = "https://api.binance.com/api/v3/aggTrades"
USDT = "USDT"
AND = "&"

# SPOT Operation
BUY = "Buy"
SELL = "Sell"
SPOT_SELL = "Transaction Related"
VALID_SPOT_OPERATION = [
    BUY,
    FEE,
    SPOT_SELL
]

VALID_USDT_FUTURES_OPERATION = [
    FEE,
    FUNDING,
    PROFIT_LOSS,
    INSURANCE_FEE
]

# output column
# TIME, SYMBOL, PNL
TIME = "Time"
PRICE = "Price"

class Translator:

    def __init__(self, log):
        logging.basicConfig(filename=log,
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)

    def translate(self, input_file, output_file):
        usdt_futures_output = []
        prev_date = None
        prev_time = None
        net = 0

        with open(input_file, 'r', encoding='latin-1') as input:
            rows = csv.DictReader(input)
            try:
                for r in rows:
                    type = r[ACCOUNT]
                    operation = r[OPERATION]
                    time_utc = r[TIME_UTC]
                    symbol = r[SYMBOL]

                    if type == USDT_FUTURES and operation in VALID_USDT_FUTURES_OPERATION:
                            change = float(r[CHANGE])
                            curr_date = self.get_date(time_utc)
                            if not prev_date:
                                prev_date = self.get_date(time_utc)
                                prev_time = time_utc
                            if prev_date != curr_date:
                                type = "realized gain" if net > 0 else "realized lost"
                                usdt_futures_output.append([prev_time, net, symbol, type])
                                net = 0
                                prev_date = curr_date
                                prev_time = time_utc
                                continue
                            net += change
                            prev_time = time_utc


            except Exception as e:
                logging.error(e)

        self.export_output(usdt_futures_output, ["Koinly Date", "Amount", "Currency", "Label"], output_file)

    def get_date(self, time_utc):
        dt_obj = datetime.strptime(time_utc,
                                   "%Y-%m-%d %H:%M:%S")
        if dt_obj:
            return dt_obj.date()
        else:
            return False

    def get_price(self, symbol, time_utc):
        try:
            price_url = self.build_price_url(symbol, time_utc)
            response = requests.get(price_url)
            content = json.loads(response.content)
            return content[0]["p"]
        except Exception as e:
            logging.error(e)
            logging.error("Unable to get price for %s, %s" % (symbol, time_utc))
            return False

    def build_price_url(self, symbol, time):
        startTime = self.get_unix_time(time)
        endTime = startTime + 10000
        param = "symbol=" + symbol + USDT + AND + "startTime=" + str(startTime) + AND + "endTime=" + str(endTime) + AND + "limit=1"
        return MARKET_DATA_URL + "?" + param

    def get_unix_time(self, utc_time):
        dt_obj = datetime.strptime(utc_time,
                                   "%Y-%m-%d %H:%M:%S")
        millisec_timestamp = dt_obj.timestamp() * 1000
        return int(millisec_timestamp)

    def export_output(self, result, header, output_file):
        logging.info("writing to output")
        with open(output_file, 'w', newline='') as output:
            row_count = 0
            writer = csv.writer(output, delimiter=',')
            writer.writerow(header)
            for r in result:
                row_count += 1
                logging.info("%s" % r)
                writer.writerow(r)
        logging.info("complete")


    @staticmethod
    def add_parser_args(parser):
        parser.add_argument("-l", "--log", required=True)
        parser.add_argument("-i", "--input", required=True)
        parser.add_argument("-o", "--output", required=True)

def main():
    try:
        parser = argparse.ArgumentParser()
        Translator.add_parser_args(parser)
        args = parser.parse_args()

        translator = Translator(args.log)
        translator.translate(args.input, args.output)
    except Exception as e:
        print(e)
        return 1

if __name__ == '__main__':
    sys.exit(main())
