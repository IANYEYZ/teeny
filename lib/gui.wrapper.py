import webview

def getGlobal():
    def createWindowWrapper(title, url = "", **kwargs):
        window = webview.create_window(title, url, **kwargs)
        return window

    def startWrapper(gui='tkinter', debug=False, **kwargs):
        webview.start(gui=gui, debug=debug, **kwargs)

    def destroyWindowWrapper(window):
        webview.destroy_window(window)

    return {
        "createWindow": createWindowWrapper,
        "start": startWrapper,
        "destroyWindow": destroyWindowWrapper
    }