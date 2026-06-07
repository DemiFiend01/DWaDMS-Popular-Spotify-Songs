from flask import Flask, render_template
from os import listdir
from os.path import isfile, join

class View:
    def __init__(self, output_path: str = ""):
        self.app = Flask(__name__)
        self.app.add_url_rule("/", view_func=self.start)
        self.pictures=[]
        self.output_path = output_path

    def start(self):
        self.load_pictures(self.output_path)
        if(self.pictures.count==0):
            return render_template('index.html')
        return render_template('index.html', pictures=self.pictures)
  
    def load_pictures(self, path: str):
        try:
            fs_path = "app/flask" + path
            self.pictures = [
                {"src" : path + "/" + p }
                for p in listdir(fs_path) if isfile(join(fs_path,p)) and p.endswith(".png")
            ]
            print("Loaded pictures")
        except Exception as e:
            print(f"Failed to load pictures: {e}")

test = View(output_path="/static/output")

if __name__ == "__main__":
    test.app.run(debug="true")
    
