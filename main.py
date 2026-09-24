def bot_loop():
    global lowest, highest, history
    print("Bot SOL - MODO CARTERA REAL - $2.93")
    lowest = 99999
    highest = 0
    history = []

    while True:
        try:
            price = exchange.fetch_ticker(symbol)['last']
            history.append(price)
            if len(history) > 15: history.pop(0)

            # RSI simple
            rsi = 50
            if len(history) >= 14:
                diffs = np.diff(history)
                g = np.mean([d for d in diffs if d>0]) if any(d>0 for d in diffs) else 0
                l = abs(np.mean([d for d in diffs if d<0])) if any(d<0 for d in diffs) else 0.0001
                rsi = 100 - (100/(1+g/l)) if l!=0 else 50

            # === ESTO ES LO QUE QUERIAS: CHECA CUENTA REAL ===
            bal = exchange.fetch_balance()
            usdt = bal['USDT']['free']
            sol = bal['SOL']['free']

            # 1. Si detecta que hay USDT -> está en modo COMPRAR
            if usdt > 1.1:
                if price < lowest:
                    lowest = price
                # Si rebota 3% desde el mínimo
                if lowest < 99999 and price >= lowest * (1 + BUY_PCT) and rsi < 50:
                    cant = (usdt * 0.6) / price
                    exchange.create_market_buy_order(symbol, cant)
                    print(f"COMPRA {lowest:.2f} -> {price:.2f} con {usdt:.2f} USDT")
                    highest = price
                    lowest = 99999

            # 2. Si detecta que hay SOL -> está en modo VENDER
            if sol > 0.01:
                if price > highest or highest == 0:
                    highest = price
                # Si cae 2.5% desde el máximo
                if price <= highest * (1 - SELL_PCT) and rsi > 50:
                    exchange.create_market_sell_order(symbol, sol)
                    print(f"VENTA {highest:.2f} -> {price:.2f}")
                    lowest = price
                    highest = 0

            time.sleep(10)

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(10)
