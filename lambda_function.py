import json

def lambda_handler():
    """
    Simulated serverless function.
    """
    result = {
        "status": "success",
        "message": "Serverless function executed successfully"
    }
    return json.dumps(result)

if __name__ == "__main__":
    print(lambda_handler())
