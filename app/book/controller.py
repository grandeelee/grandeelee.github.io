from book import book
from flask import request, render_template
from flask_login import login_required

from book.model import Package, PromotionPackage, Promotion, all_packages

@book.route('/packages', methods=['GET', 'POST'])
def packages():
    if request.method == 'POST':
        lower = request.form.get('lower')
        high = request.form.get('upper')
        packages = Package.getPackageFromPrice(lower, high)
    else:
        packages = PromotionPackage.getAllPackages()
        if not packages:
            for package in all_packages:
                our_package = Package.createPackage(package["hotel_name"].strip('"'), int(package["duration"]), float(package["packageCost"]), package['image_url'], package['description'].strip('"'))
                our_promotion = Promotion.createPromotion(package["promo_period_1"], package['promo_period_2'], 100)

                PromotionPackage.createPackages(our_package, [our_promotion], package["discount"], package["hotel_name"].strip('"'))
            packages = PromotionPackage.getAllPackages()

    return render_template('packages.html', data=packages)


@book.route("/book/<hotel_name>", methods=['POST', 'GET'])
@login_required
def book(hotel_name):
    if request.method == 'POST':
        idx = request.form.get('select')
        hotel_name = request.form.get('package_id')
        return f"index {idx} is selected for {hotel_name}"
    # get the package detail

    package = PromotionPackage.getPackage(hotel_name)
    # get check in/out date
    return render_template("book.html", package=package)

