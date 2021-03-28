from SPARQLWrapper import SPARQLWrapper, JSON
import spacy, jsonlines, rltk
from spacy.matcher import Matcher

nlp = spacy.load('en_core_web_sm')
matcher = Matcher(nlp.vocab)
pattern = [{"POS":"ADJ","OP":"*"},{"POS":{"IN": ["PROPN", "NOUN"]}, "OP":"+"}]
matcher.add("NOUN_COMPOUND", None, pattern)

with open("./src/food_class.jl",errors="ignore") as f:
    wr = jsonlines.Reader(f)
    
    food_class_dict = dict()
    idx_name = dict()
    for item in wr:
        id_1 = item["subclass"]["value"].split("/")[-1]
        name1 = item["subclassLabel"]["value"]
        
        id_2 = item["class"]["value"].split("/")[-1]
        name2 =item["classLabel"]["value"]
        if id_1 != name1 and id_2 != name2:
            food_class_dict[name1.lower()] = id_1
            food_class_dict[name2.lower()] = id_2
            idx_name[id_1] = name1.lower()
            idx_name[id_2] = name2.lower()

# token count
fre_tokens = dict()
for food in food_class_dict:
    tokens = food.split(" ")
    
    for token in tokens:
        temp = fre_tokens.get(token,set())
        temp.add(food_class_dict[food])
        fre_tokens[token] = temp
        
# remove stop word
stopword = nlp.Defaults.stop_words
for key in list(fre_tokens.keys()):
    if key in nlp.Defaults.stop_words:
        del fre_tokens[key]

def greedy_compound(matches, nlp_sent):
    tokens = []
    sent = len(nlp_sent)*[False]
    for _, start, end in matches:
        sent[start:end] = [True]*(end-start)
    print(sent)
    
    hold = []
    for status, token in zip(sent, nlp_sent):
        if status:
            hold.append(token.lemma_)
        elif status or hold:
            tokens.append(" ".join(hold))
            hold = []
        elif not (status or hold):
            continue
    if hold:
        tokens.append(" ".join(hold))
    # tokens is greedy token
    return tokens

def check_food(token, food_name, fre_tokens, threshod = 10):
    if token in food_name:
        return True
    
    words = token.split(" ")
    
    words_score = [fre_tokens.get(word,0) for word in words]
    if sum(words_score)/len(words_score)>threshod:
        return True
    
    return False

def hybrid_similarity(m ,n):
    similarity = rltk.levenshtein_similarity(m,n)
    
    if similarity > 0.7:
        similarity = 1
        return similarity
    else:
        return similarity

def search_food(id_):
    # search food by the id of class in food ontology 
    id_ = "wd:"+id_

    sparql = SPARQLWrapper("http://localhost:3030/food/query")
    sparql.setQuery(f"""
        PREFIX my_ns: <http://dsci558.org/myfakenamespace#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
        PREFIX wd: <http://www.wikidata.org/entity/> 
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> 

        SELECT ?rest (group_concat(distinct(?name); separator=", ") as ?f)
        WHERE {{
        {{
        {{?food rdfs:subClassOf {id_} .}}
        UNION
        {{?food rdfs:subClassOf/rdfs:subClassOf {id_} .}}
        UNION
        {{?food rdfs:subClassOf/rdfs:subClassOf/rdfs:subClassOf {id_} .}}
        UNION
        {{?food rdfs:subClassOf/rdfs:subClassOf/rdfs:subClassOf/rdfs:subClassOf {id_} .}}
        UNION
        {{?food rdfs:subClassOf/rdfs:subClassOf/rdfs:subClassOf/rdfs:subClassOf/rdfs:subClassOf {id_} .}}
        }}
        {{?rest my_ns:hasFood [a ?food;
        rdfs:label ?name]}}
        UNION
        {{?rest my_ns:hasFood [a {id_};
        rdfs:label ?name]}}
         }} group by ?rest order by desc(count(?name))
         limit 200
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    
    combine = dict()
    
    combine = [ (_["rest"]["value"],_["f"]["value"]) for _ in results["results"]["bindings"]]
    return combine

def search_res_with_food(food_uri):

    sparql_ = SPARQLWrapper("http://localhost:3030/rest_hotel/query")
    sparql_.setQuery(f"""
        PREFIX my_ns: <http://dsci558.org/myfakenamespace#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
        PREFIX wd: <http://www.wikidata.org/entity/> 
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> 

        SELECT ?name ?rate ?price ?location (max(?value) as ?v)
        {{ {food_uri} my_ns:name ?name ;
        my_ns:rating ?rate ;
        my_ns:price ?price ;
        my_ns:location ?location ;
        a my_ns:restaurant ;
        my_ns:hasFood [my_ns:name ?food_name;
        rdf:value ?value]
        FILTER (?food_name != "food")
        }}
        group by ?name ?rate ?price ?location limit 100
    """)
    sparql_.setReturnFormat(JSON)
    results = sparql_.query().convert()
    
    count = results["results"]["bindings"][0]["v"]["value"]
    
    sparql_.setQuery(f"""
        PREFIX my_ns: <http://dsci558.org/myfakenamespace#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
        PREFIX wd: <http://www.wikidata.org/entity/> 
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> 

        SELECT ?food_name
        {{ {food_uri} 
        my_ns:hasFood [my_ns:name ?food_name;
        rdf:value {count}]
        }}
        limit 1
    """)
    
    sparql_.setReturnFormat(JSON)
    results2 = sparql_.query().convert()
    
    data = results["results"]["bindings"][0]
    data["food"] = results2["results"]["bindings"][0]["food_name"]
    
    res = dict()
    
    for item in data:
        res[item] = data[item]["value"]
    
    del res["v"]
    return res
#######################################
input_sent = "I want to have Japanese noodle and pepperoni"
sent_nlp= nlp(input_sent)
matches = matcher(sent_nlp)
couple = greedy_compound(matches, sent_nlp)

foods = []
for item in couple:
    if item in food_class_dict:
        foods.append(item)
        continue
    
    food_token = item.split(" ")
    
    candits = set()
    for token in food_token:
        if token in fre_tokens:
            for _ in fre_tokens[token]:
                candits.add(idx_name[_])
            
    highest = (0,"")
    for candit in candits:
        s1 = food_token
        s2 = candit.split(" ")
        similarity = rltk.hybrid_jaccard_similarity(set(s1), set(s2),function=hybrid_similarity)
        
        if similarity > highest[0]:
            highest = (similarity, candit)
            
    if highest[-1]:
        foods.append(highest[-1])

print(foods)

id_s = []

for food in foods:
    id_s.append(food_class_dict[food])


count = 0
output = dict()
print(id_s)
for id_ in id_s:
    combine = search_food(id_)

    count += 1
    print("\r", "search_food:", count, end="")

    for url, food_combo in combine:
        temp = output.get(url, "")
        if temp:
            temp = food_combo
        else:
            temp = temp + "," + food_combo
        
        output[url] = temp

res = []

count = 0
for url in output:
    #print(url)
    temp = search_res_with_food("<"+url+">")
    temp["related_tokens"] = output[url].strip(",")
    temp["url"] = url
    count += 1
    print("\r", "resteraunt:", count, end="")
    res.append(temp)

print(res)