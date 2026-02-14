def lambda_handler():
    import json   # moved inside function to reduce load time
    
    result = {
        "status": "success",
        "message": "Optimized serverless execution"
    }
    return json.dumps(result)

if __name__ == "__main__":
    print(lambda_handler())
