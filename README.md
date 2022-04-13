# binance-usdt-futures-aggregator
Aggreagtes all USDT futures transactions (including fees etc) from the same day into one

- uses executed time for the last order of the day as the timestamp for the aggregated trade
- expected input to be default exported history from Binance
- output will have headers of ["Koinly Date", "Amount", "Currency", "Label"] (minimum required for simple custom Koinly form)

Sample Input:
* headers = [User_ID, UTC_Time, Account, Operation, Coin, Change]
* account need to be USDT-Futures
* ![image](https://user-images.githubusercontent.com/71180448/163087697-65448ca6-8f7c-4299-b132-76f6a5e2cae2.png)


Sample Output from input above:
* headers = [Koinly Date, Amount, Currency, Label]
* ![image](https://user-images.githubusercontent.com/71180448/163087860-d375fc67-8bc7-43c3-ab53-1d33bc53e1eb.png)

Parameter:
* -l path of where the log file should be stored
* -i absolute path of the input file
* -i absolute path of the expected output file

Sample Run Config:
* python3 /binance-usdt-futures-translator.py -l /Users/jiingzheng/Documents/tax/2021/crypto-transactions/binance-translation.log -i /Users/jiingzheng/Documents/tax/2021/crypto-transactions/2021-binance.csv -o /Users/jiingzheng/Documents/tax/2021/crypto-transactions/binance-2021-usdt-output-test.csv

* <img width="760" alt="image" src="https://user-images.githubusercontent.com/71180448/163088603-9c6ab280-b892-4bd8-a6df-880bb2e4451d.png">
