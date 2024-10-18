from app import app
from flask import request, redirect, url_for, render_template, flash
from book.model import Package


@app.route('/')
@app.route('/index')
@app.route('/homepage')
def home():
    return redirect(url_for("auth.login"))



@app.route("/upload", methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        file = request.files.get("uploadFile")
        data = file.read().decode("utf-8").split("\n")
        file.close()
        datatype = request.form.get("dataType")
        if datatype == "packages":
            n = 0
            for line in data[1:]:
                hotel_name,duration,unit_cost,image_url,description = line.split(",")
                package = Package.getPackage(hotel_name.strip('"'))
                if package:
                    flash(f"Package {hotel_name} already exist")
                    continue
                Package.createPackage(hotel_name.strip('"'), int(duration), float(unit_cost), image_url, description.strip('"'))
                flash(f"Packages {hotel_name} created successfully")
                n += 1
            # here we store the data in the database
            flash(f"{n} packages uploaded successfully")

        
    return render_template("upload.html")

@app.route("/demo", methods=['POST', 'GET'])
def demo():
    if request.method == 'GET':
        return render_template("ajax_demo.html")
    if request.method == 'POST':
        
        return request.form['input']