from SPARQLWrapper import SPARQLWrapper, JSON

def search_comment(food_uri, related_token):
    # add "" to token
    _ = related_token.split(",")
    _ = ['"'+item.strip()+'"' for item in _]
    related_token = ",".join(_)
    print(related_token)
    sparql_ = SPARQLWrapper("http://localhost:3030/rest_hotel/query")
    sparql_.setQuery(f"""
        PREFIX my_ns: <http://dsci558.org/myfakenamespace#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
        PREFIX wd: <http://www.wikidata.org/entity/> 
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> 

        SELECT ?food_name ?sentence
        {{ {food_uri} a my_ns:restaurant;
        my_ns:hasFood [my_ns:name ?food_name;
        my_ns:hasSent ?sentence]
        FILTER (?food_name in ({related_token}))
        }}
    """)
    sparql_.setReturnFormat(JSON)
    results = sparql_.query().convert()

    list_food_sent = []

    _ = related_token.split(",")
    _ = [item.strip()+'@en' for item in _]
    related_token = ",".join(_)
    print(related_token)


    for line in results["results"]["bindings"]:
        temp = {}
        temp["food_name"] = line["food_name"]["value"]
        temp["sentence"] = "\n".join([_+"." for _ in line["sentence"]["value"].split(". ")])
        list_food_sent.append(temp)
    
    sparql = SPARQLWrapper("http://localhost:3030/food/query")
    sparql.setQuery(f"""
        PREFIX my_ns: <http://dsci558.org/myfakenamespace#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
        PREFIX wd: <http://www.wikidata.org/entity/> 
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> 

        SELECT ?food_name (max(?foodclass) as ?class)
        WHERE
        {{?any my_ns:hasFood [rdfs:label ?food_name;
        a ?foodclass]
        FILTER (?food_name in ({related_token}))}} group by ?food_name
        """)
    
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    food_id = {}
    for line in results["results"]["bindings"]:
        food_id[line['food_name']["value"]] = line['class']["value"]

    for idx in range(len(list_food_sent)):
        list_food_sent[idx]["wiki_id"] = food_id[list_food_sent[idx]["food_name"]]        
    return list_food_sent

if __name__ == "__main__":
    food_uri = "<https://www.tripadvisor.com/Restaurant_Review-g32655-d3800202-Reviews-or130-Tsujita_LA-Los_Angeles_California.html>"
    related_token =  'tsukemen, ramen, japanese noodle'
    print(search_comment(food_uri, related_token))