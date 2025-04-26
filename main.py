# server.py
import yaml
from mcp.server.fastmcp import FastMCP
import requests

# Create an MCP server
mcp = FastMCP("getCanonicalNameAndCUI")

with open("config.yaml", "r") as stream:
    try:
        PARAM = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

@mcp.tool()
def get_the_canonical_name_and_id(term: str) -> str:
    """Query the UMLS API to get the canonical name and CUI id of a term. The canonical name and CUI id are used in the DrugDB database. Use this tool to get the canonical name and CUI id of a term before querying the DrugDB."""
    umls_token = PARAM["umls_token"]
    amount_of_results = 5
    url = f"https://uts-ws.nlm.nih.gov/rest/search/current?string={term}&apiKey={umls_token}"

    response = requests.get(url).json()

    if "status" in response and str(response["status"]) == "404":
        return []
    
    else:
        
        if "result" in response and "results" in response["result"]:
            result = []

            for r in response["result"]["results"]:
                if len(result) < amount_of_results and "ui" in r and "name" in r:
                    temp = {}
                    temp["id"] = r["ui"]
                    temp["name"] = r["name"]
                    result.append(temp)
            return result
        else:    
            return []


@mcp.prompt()
def get_canonical_names_and_cui_prompt() -> str:
    """
    Provide instruction for the umls get_the_canonical_name_and_id function
    to help Claude write better handle the task.
    """
    return """
When the user question contains medical terms, please extract that term and use the get_the_canonical_name_and_id function to get the canonical name and CUI id of the term.

For each get_the_canonical_name_and_id call, the function returns up to five candidate results. Based on the context of the user question, you sort them and try to query the database from the most appropriate to the least. When the database query is successful, you can stop running down the list. Normally, the first candidate is the most appropriate one. However, if the first candidate is not appropriate, you can try the second or third candidate.

If the user question contains multiple medical terms, please extract each term and call the get_the_canonical_name_and_id function for each term.

Example:
--Show me the drugs whose MOA is GLP-1 Receptor.
Extract "GLP-1" and call get_the_canonical_name_and_id("GLP-1 Receptor") to get the candidates name and CUI ids of the term. They are
[{'id': 'C2917359', 'name': 'GLP-1 Receptor Agonist [EPC]'}, {'id': 'C2267163', 'name': 'Glucagon-like Peptide-1 (GLP-1) Receptor Interactions'}, {'id': 'C3658192', 'name': 'GLP1R protein, human'}, {'id': 'C0378073', 'name': 'Glucagon-Like Peptide-1 Receptor'}, {'id': 'C1562104', 'name': 'Glucagon-Like Peptide-1 Receptor Agonists'}]
Then "{'id': 'C2267163', 'name': 'Glucagon-like Peptide-1 (GLP-1) Receptor Interactions'}" should be your first guess, because that is an MOA term and EPC in the first one means endothelial progenitor cells. Then use that information to query the DrugDB database. The database should return the drugs whose MOA is GLP-1 Receptor. But {'id': 'C1562104', 'name': 'Glucagon-Like Peptide-1 Receptor Agonists'} is also a valid candidate, so you can try that one too.


--What drug may treat type 2 diabetes? Give me 5 results
Extract "type 2 diabetes" and call get_the_canonical_name_and_id("type 2 diabetes") to get the canonical name and CUI id of the term. They are:
[{'id': 'C0011860', 'name': 'Diabetes Mellitus, Non-Insulin-Dependent'}, {'id': 'C4015183', 'name': 'TYPE 2 DIABETES 5'}, {'id': 'C2733146', 'name': 'Uncontrolled type 2 diabetes mellitus'}, {'id': 'C2919802', 'name': 'Brittle type 2 diabetes mellitus'}, {'id': 'C0342295', 'name': 'Ketoacidosis due to type 2 diabetes mellitus'}]
Then use the first one to query the DrugDB database, because it is the official name of type 2 diabetes.


--What disorder can 1,1-Dimethylbiguanide treat?
Extract "1,1-Dimethylbiguanide" and call get_the_canonical_name_and_id("1,1-Dimethylbiguanide") to get the canonical name and CUI id of the term. They are
[{'id': 'C0025598', 'name': 'metformin'}, {'id': 'C0770893', 'name': 'metformin hydrochloride'}]
Then use the first one to query the DrugDB database because that is synonymous with ,1-Dimethylbiguanide

--Do tolbutamide and glucose share a same ATC ancestor?
Extract "tolbutamide" and call get_the_canonical_name_and_id("tolbutamide"); extract "glucose" and call get_the_canonical_name_and_id("glucose") to get the canonical name and CUI id of the term. They are
[{'id': 'C0040374', 'name': 'tolbutamide'}, {'id': 'C0724709', 'name': 'tolbutamide sodium'}, {'id': 'C0524285', 'name': 'Tolbutamide measurement'}, {'id': 'C0591914', 'name': 'Orabet Tolbutamide'}, {'id': 'C0430190', 'name': 'Tolbutamide tolerance test'}]

[{'id': 'C0017725', 'name': 'glucose'}, {'id': 'C0337438', 'name': 'Glucose measurement'}, {'id': 'C5781949', 'name': 'Glucose^1.5H post dose glucagon'}, {'id': 'C0765796', 'name': 'glucose-mannose-glucose'}, {'id': 'C0490221', 'name': 'GLUCOSE OXIDASE, GLUCOSE'}]

Then take the first ones to query the DrugDB database because they both are identical to the user inputs.

"""


if __name__ == "__main__":
    print("Starting server...")
    # Initialize and run the server

    # print (get_the_canonical_name_and_id("type 2 diabetes"))

    # print (get_the_canonical_name_and_id("1,1-Dimethylbiguanide"))

    # print (get_the_canonical_name_and_id("tolbutamide"))
    # print (get_the_canonical_name_and_id("glucose"))
    mcp.run(transport="stdio")