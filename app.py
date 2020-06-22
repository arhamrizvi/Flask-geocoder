import pandas as pd
from flask import Flask, render_template, request, send_file
import numpy as np
from geopy.geocoders import ArcGIS, Nominatim
import datetime




def preprocessing(file):
    df = pd.read_csv(file)

    colNames = list(df.columns.values) #put column names in a list

    colNames = np.array([a.lower() for a in colNames]) #lower column names

    if "address" not in colNames:
        return False

    df.columns = colNames #reassign column names

    return df

#df = preprocessing('Supermarkets.csv')

#print(df)


app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/success-table", methods=['POST'])
def success_table():
    global filename
    if request.method == "POST":
        file= request.files['file']
        try:
            df = preprocessing(file)
            gc = Nominatim()
            df["coordinates"]=df["address"].apply(gc.geocode)
            df['Latitude']=df['coordinates'].apply(lambda x: x.latitude if x!=None else None)
            df['Longitude']=df['coordinates'].apply(lambda x: x.longitude if x!=None else None)
            df=df.drop("coordinates",1)
            filename = datetime.datetime.now().strftime("geocoded_"+"%Y-%m-%d-%H-%M-%S-%f"+".csv")
            df.to_csv(filename,index=None)
            return render_template("index.html",text=df.to_html(),btn='download.html')
        except:
            return render_template("index.html",text="Please make sure you have the correct CSV file.")
    
@app.route("/download-file/")
def download():
    return send_file(filename,attachment_filename='yourfile.csv',as_attachment=True)

if __name__=='__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True)