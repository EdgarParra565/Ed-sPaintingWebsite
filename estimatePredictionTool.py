

#TODO: class with method calls that will will help estimate rooms and garage epoxy floors
# METHOD 1: Basic estimator for room:
# - will take in three parameters length1, length2, height
# - second prompt for refresh by adding one coat, or repaint entire room (3 coats)
# - parameter is always true for room estimators, false for garage estimates
# + use length1 and length2 to the square footage of room
# + if height is over or under a certain parameter price adjusted
# Method 2: Ceiling method call:
# - boolean if ceiling will be painted or not
# + if yes, second prompt for repainted or just fresh coat
# Method 3: Trims method call:
# - boolean if trims will be painted or not
# + if yes, second prompt to check base molding and/or ceiling trims
# Method 4: Render mini room:
# - room design unknow but a mini render so user can get feel for room, and what is being painted
# - figure out if this method call should be in class ??
# Method 5: epoxy method call:
# - takes in length1 and length2 of room
# - parameter is always true for garage estimators, false for room estimators
# - prompts user on different types of epoxy flooring, chip choice or no just solution
# Method 6: Display total method call:
# - takes stored parameters and gets summation of all parameters if boolean for parameter is true.\


def estimate_price(service_type, square_feet, interior, epoxy_type=None):
    base_rate = 0

    if service_type == "painting":
        base_rate = 2.50 if interior else 3.25

    elif service_type == "epoxy":
        if epoxy_type == "metallic":
            base_rate = 7.50
        else:
            base_rate = 5.00

    return round(base_rate * square_feet, 2)


