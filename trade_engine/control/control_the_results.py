from data.bot_features import load_bot_holding, load_bot_positions, load_bot_value

def control_the_results(bot_id, results):

    minValue = 10.0 # Minimum işlem limiti usd dolar

    def get_state(pos, per):
        if per == 0:
            return "none"
        if pos < 0:
            return "short"
        elif pos > 1:
            return "long"
        elif 0 < pos <= 1:
            return "spot"
        return "none"

    def sanitize_result(result): #result içini temizleme
        new_result = result.copy()
        new_result.pop("last_positions", None)
        new_result.pop("last_percentage", None)
        return new_result

    holdings = load_bot_holding(bot_id)
    holding_dict = {h['symbol']: h['percentage'] for h in holdings}

    open_positions = load_bot_positions(bot_id)
    open_position_map = {p['symbol']: p for p in open_positions}

    current_value = load_bot_value(bot_id)

    # holdings + açık pozisyonlardaki toplam yüzde
    fulness = 0

    # Holding içindeki yüzdeleri topla
    fulness += (sum(holding_dict.values())/100)

    # Open positions içindeki yüzdeleri topla (aynı coinler olabilir, bu yüzden ayrı ayrı ekleniyor)
    for pos in open_position_map.values():
        percentage = pos.get('percentage', 0)
        fulness += float(percentage) / 100

    filtered_results = []
    
    prev_state = "none"
    curr_state = "none"

    # KAPAMA İŞLEMLERİ İÇİN KONTROL ET
    for result in results:
        last_positions = result.get('last_positions')
        last_percentage = result.get('last_percentage')
        if last_positions is None or last_percentage is None:
            continue

        prev_pos, curr_pos = float(str(last_positions[0])), float(str(last_positions[1]))
        prev_per, curr_per = float(str(last_percentage[0])), float(str(last_percentage[1]))

        if prev_pos > 100:
            prev_pos = 100
        if curr_per > 100:
            curr_per = 100
        
        if (
            not isinstance(last_positions, list) or 
            len(last_positions) != 2 or 
            last_positions[0] == last_positions[1] and
            last_percentage[0] == last_percentage[1]
        ):
            continue
        
        # STATE İSİMLENDİRMELERİNİ YAP
        prev_state = get_state(prev_pos, prev_per)
        curr_state = get_state(curr_pos, curr_per)

        symbol = result.get('coin_id')
        percentage_hold = holding_dict.get(symbol, float('0'))
        if percentage_hold == None:
            percentage_hold = 0
        try:
            percentage_pos = float(open_position_map[symbol]['percentage'])
        except KeyError:
            percentage_pos = 0.0

        #if bot_id == 56:
        #    print(f"bot_id: {bot_id}, usd: {current_value}, fulness: {fulness}")
        #    print(f"prev_pos: {prev_pos}, curr_pos: {curr_pos}, prev_per: {prev_per}, curr_per: {curr_per}")
        #    print(f"prev_state: {prev_state}, curr_state: {curr_state}")

        # KAPAMA İŞLEMLERİ İÇİN KONTROL ET
        match (prev_state, curr_state):
            case ("none", "none"):
                continue
            case ("none", "spot"):
                continue
            case ("none", "long"):
                continue
            case ("none", "short"):
                continue
            case ("spot", "none"):
                if percentage_hold != 0:
                    new_result = sanitize_result(result)
                    new_result['side'] = "sell"
                    value = percentage_hold/100
                    new_result['value'] = current_value * value
                    fulness -= value
                    filtered_results.append(new_result)
                continue
            case ("spot", "spot"):
                curr_spot = curr_pos * curr_per
                prev_spot = prev_pos * prev_per
                if curr_spot < prev_spot and percentage_hold != 0 and curr_spot < percentage_hold:
                    new_result = sanitize_result(result)
                    new_result['side'] = "sell"
                    value = (percentage_hold/100) - (curr_spot/100)
                    new_result['value'] = current_value * value
                    fulness -= value
                    filtered_results.append(new_result)
                continue
            case ("spot", "long"):
                if percentage_hold != 0:
                    new_result = sanitize_result(result)
                    new_result['side'] = "sell"
                    value = percentage_hold/100
                    new_result['value'] = current_value * value
                    fulness -= value
                    filtered_results.append(new_result)
                continue
            case ("spot", "short"):
                if percentage_hold != 0:
                    new_result = sanitize_result(result)
                    new_result['side'] = "sell"
                    value = percentage_hold/100
                    new_result['value'] = current_value * value
                    fulness -= value
                    filtered_results.append(new_result)
                continue
            case ("long", "none"):
                if percentage_pos != 0:
                    new_result = sanitize_result(result)
                    if open_position_map[symbol]['side']== "short":
                        new_result['side'] = "buy"
                        new_result['positionside'] = "short"
                    elif open_position_map[symbol]['side']== "long":
                        new_result['side'] = "sell"
                        new_result['positionside'] = "long"
                    new_result['reduceOnly'] = True
                    value = percentage_pos/100
                    new_result['value'] = current_value * value
                    fulness -= value
                    filtered_results.append(new_result)
                continue
            case ("long", "spot"):
                if percentage_pos != 0:
                    new_result = sanitize_result(result)
                    if open_position_map[symbol]['side']== "short":
                        new_result['side'] = "buy"
                        new_result['positionside'] = "short"
                    elif open_position_map[symbol]['side']== "long":
                        new_result['side'] = "sell"
                        new_result['positionside'] = "long"
                    new_result['reduceOnly'] = True
                    value = percentage_pos/100
                    new_result['value'] = current_value * value
                    fulness -= value
                    filtered_results.append(new_result)
                continue
            case ("long", "long"):
                curr_position = curr_pos * curr_per
                prev_position = prev_pos * prev_per
                if curr_position < prev_position and percentage_pos != 0 and curr_position < percentage_pos and open_position_map[symbol]['side']== "long":
                    new_result = sanitize_result(result)
                    new_result['side'] = "sell"
                    new_result['positionside'] = "long"
                    new_result['reduceOnly'] = True
                    value = (percentage_pos-curr_position)/100
                    new_result['value'] = current_value * value
                    fulness -= value
                    filtered_results.append(new_result)
                continue
            case ("long", "short"):
                if percentage_pos != 0:
                    new_result = sanitize_result(result)
                    if open_position_map[symbol]['side']== "short":
                        new_result['side'] = "buy"
                        new_result['positionside'] = "short"
                    elif open_position_map[symbol]['side']== "long":
                        new_result['side'] = "sell"
                        new_result['positionside'] = "long"
                    new_result['reduceOnly'] = True
                    value = percentage_pos/100
                    new_result['value'] = current_value * value
                    fulness -= value
                    filtered_results.append(new_result)
                continue
            case ("short", "none"):
                if percentage_pos != 0:
                    new_result = sanitize_result(result)
                    if open_position_map[symbol]['side']== "short":
                        new_result['side'] = "buy"
                        new_result['positionside'] = "short"
                    elif open_position_map[symbol]['side']== "long":
                        new_result['side'] = "sell"
                        new_result['positionside'] = "long"
                    new_result['reduceOnly'] = True
                    value = percentage_pos/100
                    new_result['value'] = current_value * value
                    fulness -= value
                    filtered_results.append(new_result)
                continue
            case ("short", "spot"):
                if percentage_pos != 0:
                    new_result = sanitize_result(result)
                    if open_position_map[symbol]['side']== "short":
                        new_result['side'] = "buy"
                        new_result['positionside'] = "short"
                    elif open_position_map[symbol]['side']== "long":
                        new_result['side'] = "sell"
                        new_result['positionside'] = "long"
                    new_result['reduceOnly'] = True
                    value = percentage_pos/100
                    new_result['value'] = current_value * value
                    fulness -= value
                    filtered_results.append(new_result)
                continue
            case ("short", "long"):
                if percentage_pos != 0:
                    new_result = sanitize_result(result)
                    new_result['side'] = "buy"
                    new_result['positionside'] = "short"
                    new_result['reduceOnly'] = True
                    value = percentage_pos/100
                    new_result['value'] = current_value * value
                    fulness -= value
                    filtered_results.append(new_result)
                continue
            case ("short", "short"):
                if curr_per < prev_per and percentage_pos != 0 and curr_per < percentage_pos:
                    new_result['side'] = "buy"
                    new_result['positionside'] = "short"
                    new_result['reduceOnly'] = True
                    value = (percentage_pos-curr_position)/100
                    new_result = sanitize_result(result)
                    new_result['value'] = current_value * value
                    fulness -= value
                    filtered_results.append(new_result)
                continue

    # AÇMA İŞLEMLERİ İÇİN KONTROL ET
    for result in results:
        last_positions = result.get('last_positions')
        last_percentage = result.get('last_percentage')

        if last_positions is None or last_percentage is None:
            continue
        
        prev_pos, curr_pos = float(str(last_positions[0])), float(str(last_positions[1]))
        prev_per, curr_per = float(str(last_percentage[0])), float(str(last_percentage[1]))

        if prev_pos > 100:
            prev_pos = 100
        if curr_per > 100:
            curr_per = 100
        
        prev_state = get_state(prev_pos, prev_per)
        curr_state = get_state(curr_pos, curr_per)
        
        symbol = result.get('coin_id')
        percentage_hold = holding_dict.get(symbol, float('0'))
        if percentage_hold == None:
            percentage_hold = 0
        try:
            percentage_pos = float(open_position_map[symbol]['percentage'])
        except KeyError:
            percentage_pos = 0

        # AÇMA İŞLEMLERİ İÇİN KONTROL ET
        match (prev_state, curr_state):
            case ("none", "none"): #TRUE
                continue
            case ("none", "spot"): #TRUE
                value = curr_pos * (curr_per/100)
                if (value*current_value) < minValue:
                    continue
                if (value < (1-fulness)):
                    new_result = sanitize_result(result)
                    new_result['side'] = "buy"
                    new_result['value'] = current_value * value
                    fulness += value
                    filtered_results.append(new_result)
                continue
            case ("none", "long"):
                value = curr_per/100
                if (value*current_value) < minValue:
                    continue
                if value < (1-fulness):
                    new_result = sanitize_result(result)
                    new_result['side'] = "buy"
                    new_result['positionside'] = "long"
                    new_result['leverage'] = curr_pos
                    new_result['value'] = current_value * value
                    fulness += value
                    filtered_results.append(new_result)
                continue
            case ("none", "short"):
                value = curr_per/100
                if (value*current_value) < minValue:
                    continue
                if value < (1-fulness):
                    new_result = sanitize_result(result)
                    new_result['side'] = "sell"
                    new_result['positionside'] = "short"
                    new_result['leverage'] = curr_pos
                    new_result['value'] = current_value * value
                    fulness += value
                    filtered_results.append(new_result)
                continue
            case ("spot", "none"):
                continue
            case ("spot", "spot"):
                curr_spot = curr_pos * curr_per
                prev_spot = prev_pos * prev_per
                value = (curr_spot-percentage_hold)/100
                if (value*current_value) < minValue:
                    continue
                if curr_spot > prev_spot and percentage_hold != 0 and curr_spot > percentage_hold and value < (1-fulness):
                    new_result = sanitize_result(result)
                    new_result['side'] = "buy"
                    new_result['value'] = current_value * value
                    fulness += value
                    filtered_results.append(new_result)
                continue
            case ("spot", "long"):
                value = curr_per/100
                if (value*current_value) < minValue:
                    continue
                if value < (1-fulness):
                    new_result = sanitize_result(result)
                    new_result['side'] = "buy"
                    new_result['positionside'] = "long"
                    new_result['leverage'] = curr_pos
                    new_result['value'] = current_value * value
                    fulness += value
                    filtered_results.append(new_result)
                continue
            case ("spot", "short"):
                value = curr_per/100
                if (value*current_value) < minValue:
                    continue
                if value < (1-fulness):
                    new_result = sanitize_result(result)
                    new_result['side'] = "sell"
                    new_result['positionside'] = "short"
                    new_result['leverage'] = curr_pos
                    new_result['value'] = current_value * value
                    fulness += value
                    filtered_results.append(new_result)
                continue
            case ("long", "none"):
                continue
            case ("long", "spot"):
                value = curr_pos * (curr_per/100)
                if (value*current_value) < minValue:
                    continue
                if value < (1-fulness):
                    new_result = sanitize_result(result)
                    new_result['side'] = "buy"
                    new_result['value'] = current_value * value
                    fulness += value
                    filtered_results.append(new_result)
                continue
            case ("long", "long"):
                curr_position = curr_pos * curr_per
                prev_position = prev_pos * prev_per
                if percentage_pos != 0 and curr_position > percentage_pos:
                    value = (percentage_pos-curr_position)/100
                    if (value*current_value) < minValue:
                        continue
                    if curr_position > prev_position and value < (1-fulness):
                        new_result = sanitize_result(result)
                        new_result['side'] = "sell"
                        new_result['positionside'] = "long"
                        new_result['reduceOnly'] = True
                        new_result['value'] = current_value * value
                        fulness += value
                        filtered_results.append(new_result)
                continue
            case ("long", "short"):
                value = curr_per/100
                if (value*current_value) < minValue:
                    continue
                if value < (1-fulness):
                    new_result = sanitize_result(result)
                    new_result['side'] = "sell"
                    new_result['positionside'] = "short"
                    new_result['leverage'] = curr_pos
                    new_result['value'] = current_value * value
                    fulness += value
                    filtered_results.append(new_result)
                continue
            case ("short", "none"):
                continue
            case ("short", "spot"):
                value = curr_pos * (curr_per/100)
                if (value*current_value) < minValue:
                    continue
                if value < (1-fulness):
                    new_result = sanitize_result(result)
                    new_result['side'] = "buy"
                    new_result['value'] = current_value * value
                    fulness += value
                    filtered_results.append(new_result)
                continue
            case ("short", "long"):
                value = curr_per/100
                if (value*current_value) < minValue:
                    continue
                if value < (1-fulness):
                    new_result = sanitize_result(result)
                    new_result['side'] = "buy"
                    new_result['positionside'] = "long"
                    new_result['leverage'] = curr_pos
                    new_result['value'] = current_value * value
                    fulness += value
                    filtered_results.append(new_result)
                continue
            case ("short", "short"):
                if percentage_pos != 0 and curr_per > percentage_pos:
                    value = (curr_per-percentage_pos)/100
                    if (value*current_value) < minValue:
                        continue
                    if value < (1-fulness):
                        new_result = sanitize_result(result)
                        new_result['side'] = "sell"
                        new_result['positionside'] = "short"
                        new_result['value'] = current_value * value
                        fulness += value
                        filtered_results.append(new_result)
                elif percentage_pos == 0:
                    value = (curr_per)/100
                    if (value*current_value) < minValue:
                        continue
                    if value < (1-fulness):
                        new_result = sanitize_result(result)
                        new_result['side'] = "sell"
                        new_result['positionside'] = "short"
                        new_result['value'] = current_value * value
                        fulness += value
                        filtered_results.append(new_result)
                continue
    return filtered_results
