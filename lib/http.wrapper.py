import requests

def getGlobal():
    def getWrapper(url, **kwargs):
        response = requests.get(url, **kwargs)
        return {
            "status_code": response.status_code,
            "headers": response.headers,
            "content": response.content
        }
    def postWrapper(url, data=None, json=None, **kwargs):
        response = requests.post(url, data=data, json=json, **kwargs)
        return {
            "status_code": response.status_code,
            "headers": response.headers,
            "content": response.content
        }
    def putWrapper(url, data=None, **kwargs):
        response = requests.put(url, data=data, **kwargs)
        return {
            "status_code": response.status_code,
            "headers": response.headers,
            "content": response.content
        }
    def deleteWrapper(url, **kwargs):
        response = requests.delete(url, **kwargs)
        return {
            "status_code": response.status_code,
            "headers": response.headers,
            "content": response.content
        }
    def headWrapper(url, **kwargs):
        response = requests.head(url, **kwargs)
        return {
            "status_code": response.status_code,
            "headers": response.headers
        }
    def patchWrapper(url, data=None, **kwargs):
        response = requests.patch(url, data=data, **kwargs)
        return {
            "status_code": response.status_code,
            "headers": response.headers,
            "content": response.content
        }
    return {
        "get": getWrapper,
        "post": postWrapper,
        "put": putWrapper,
        "delete": deleteWrapper,
        "head": headWrapper,
        "patch": patchWrapper
    }