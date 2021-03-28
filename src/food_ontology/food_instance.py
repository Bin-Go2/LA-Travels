from food_class import slice_list
import sys, jsonlines, time, os, requests

def wikidata_qury(p,foods):
    foods = foods.split(",")
    add_str = ""
    for food in foods:
        add_str += f"{{?subclass wdt:{p} {food}}} UNION"
        
    add_str = add_str[:-6]
    url = 'https://query.wikidata.org/sparql'
    query = f"""
    SELECT ?subclass ?subclassLabel
    WHERE 
    {{
      {add_str}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    """
    #print(query)
    r = requests.get(url, params = {'format': 'json', 'query': query})
    try:
        data = r.json()
        food_record = data["results"]['bindings']
    except:
        food_record = {"errors":foods}
    return food_record

if __name__ == "__main__":
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    with open(input_file, "r",errors="replace") as input_f:
        candits = set()
        
        wr = jsonlines.Reader(input_f)
        candits.add("wd:Q2095")
        for line in wr:
            candits.add("wd:"+line["subclass"]["value"].split("/")[-1])

    try:
        os.remove(output_file)
    except OSError:
        pass

    with open(output_file, "a", errors="replace") as f:
        wr = jsonlines.Writer(f)
        count = 0
        candits = list(candits)
        while candits:
            # new candits used for next iteration
            new_candits = []
            # data write to file
            food_class = []
            count2 = 0

            sliced_candits = slice_list(candits, length = 50)
            
            for sl in sliced_candits:
                foods = ",".join(sl)

                #print(foods)
                temp = wikidata_qury("P31",foods)
                if "errors" in temp:
                    continue
                wr.write_all(temp)

                #food_class += part_food_class
                temp_candits = ["wd:"+_["subclass"]["value"].split("/")[-1] for _ in temp]

                new_candits += temp_candits

                time.sleep(3)
                count2+=1
                print("\r", count2, end="")

            candits = new_candits

            # write output data food_class to file
            
            print("\r", count, len(candits))
            count += 1
            if not candits:
                break