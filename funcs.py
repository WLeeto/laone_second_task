import json
from pprint import pprint
from exeptions import LostItemError


def merge_stock(assort_path: str, stock_path: str) -> list or False:
    """
    Tackes data from stock.json, merges it with assortiment.json and return list, ready to download to Gsheets
    :param assort_path: path to an assortiment.json
    :param stock_path: path to a stock.json
    :return:
    """
    with open(assort_path, encoding="utf-8") as assortiment:
        result_assortiment = json.load(assortiment)

    with open(stock_path, encoding="utf-8") as stock:
        result_stock = json.load(stock)

    final_result = {}
    count = 0

    for stock_item in result_stock["rows"]:
        for assort_item in result_assortiment:
            if stock_item["externalCode"] == assort_item["externalCode"]:
                count += 1
                name = stock_item["name"]
                if stock_item.get("image"):
                    image = stock_item['image']['miniature']['downloadHref']
                else:
                    image = None
                price_1 = assort_item["salePrices"][0]["value"]
                price_5 = assort_item["salePrices"][1]["value"]
                price_15 = assort_item["salePrices"][2]["value"]
                price_100 = assort_item["salePrices"][3]["value"]

                temp_search = stock_item['folder']['pathName'].split("/")

                val = {
                    "Наименование": name,
                    "Изображение": image,
                    "Розница": price_1,
                    "от 5 т.р.": price_5,
                    "от 15 т.р.": price_15,
                    "от 100 т.р.": price_100
                }

                if len(temp_search) > 1:
                    if temp_search[1] == "Ресницы":
                        brand = temp_search[2]
                        if temp_search[1] in final_result.keys():
                            final_result[f"{temp_search[1]}_{temp_search[2]}"].append(val)
                        else:
                            final_result[f"{temp_search[1]}_{temp_search[2]}"] = [val]
                    elif temp_search[1] == "Расходные материалы":
                        if len(temp_search) > 2:
                            type = temp_search[2]
                            if temp_search[1] in final_result.keys():
                                if temp_search[2] in final_result[temp_search[1]]:
                                    final_result[temp_search[1]][temp_search[2]].append(val)
                                else:
                                    final_result[temp_search[1]][temp_search[2]] = [val]
                            else:
                                final_result[temp_search[1]] = {type: [val]}
                        else:
                            if temp_search[1] in final_result.keys():
                                if "Other" in final_result[temp_search[1]]:
                                    final_result[temp_search[1]]["Other"].append(val)
                                else:
                                    final_result[temp_search[1]]["Other"] = [val]
                            else:
                                final_result[f"{temp_search[1]}"] = {"Other": [val]}
                    else:
                        try:
                            final_result[f"{temp_search[1]}"].append(val)
                        except KeyError:
                            final_result[f"{temp_search[1]}"] = [val]
                else:
                    try:
                        final_result["Other"].append(val)
                    except KeyError:
                        final_result["Other"] = [val]

    if len(result_stock["rows"]) == count:
        return final_result
    else:
        raise LostItemError(len(result_stock["rows"]), len(final_result))


if __name__ == "__main__":
    res = merge_stock("temp/assortment.json", "temp/stocks.json")
    pprint(res)

