#imports
from Website import init_application

web_app = init_application()
if __name__ == '__main__': #Bypassing imports. Create and run app only if file is ran. 
    web_app.run(debug=True)
