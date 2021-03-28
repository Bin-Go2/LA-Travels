import requests
import time
import jsonlines
import os, sys

def wikidata_qury(p,foods):
    url = 'https://query.wikidata.org/sparql'
    query = f"""
    SELECT ?subclass ?subclassLabel ?class ?classLabel
    WHERE 
    {{
      ?subclass wdt:{p} ?class.
      Filter (?class IN ({foods}) )
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    """
    #print(query)
    r = requests.get(url, params = {'format': 'json', 'query': query})
    data = r.json()
    food_record = data["results"]['bindings']
    return food_record

def slice_list(l, length = 350):
    l_len = len(l)
    
    if l_len < 350:
        return [l]
    a, b = divmod(l_len,length)
    
    return [ l[i*length:(i+1)*length] for i in range(a+1)]

if __name__ == "__main__":
    filename = sys.argv[1]
    
    try:
        os.remove(filename)
    except OSError:
        pass

    with open(filename, "a", errors="replace") as f:
        candits = ["wd:Q2095"]
        count = 0
        wr = jsonlines.Writer(f)
        while candits:
            # new candits used for next iteration
            new_candits = []
            # data write to file
            food_class = []
            count2 = 0

            sliced_candits = slice_list(candits, length = 350)
            
            for sl in sliced_candits:

                foods = ",".join(sl)
                temp = wikidata_qury("P279",foods)
                
                wr.write_all(temp)

                #food_class += part_food_class
                temp_candits = ["wd:"+_["subclass"]["value"].split("/")[-1] for _ in temp]

                new_candits += temp_candits

                time.sleep(2)
                count2+=1
                print("\r", count2, end="")

            candits = new_candits

            # write output data food_class to file
            #wr.write_all(food_class)
            
            print("\r", count, len(candits))
            count += 1
            if not candits:
                break