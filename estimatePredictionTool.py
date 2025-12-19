# class with method calls that will help estimate rooms and garage epoxy floors
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

class PaintEstimator:
    def __init__(self):
        self.wall_cost = 0.0
        self.ceiling_cost = 0.0
        self.trim_cost = 0.0
        self.square_footage = 0.0

    # -------------------------
    # Walls
    # -------------------------
    def estimate_walls(
        self,
        length: float,
        width: float,
        height: float,
        full_repaint: bool
    ):
        self.square_footage = length * width

        base_rate = 2.50
        coats = 3 if full_repaint else 1

        height_adjustment = 0.0
        if height > 10:
            height_adjustment = 0.25 * (height - 10)
        elif height < 8:
            height_adjustment = -0.15 * (8 - height)

        self.wall_cost = (
            base_rate + height_adjustment
        ) * self.square_footage * coats

    # -------------------------
    # Ceiling
    # -------------------------
    def estimate_ceiling(
        self,
        paint_ceiling: bool,
        full_repaint: bool
    ):
        if not paint_ceiling:
            return

        rate = 1.50
        coats = 2 if full_repaint else 1
        self.ceiling_cost = rate * self.square_footage * coats

    # -------------------------
    # Trim
    # -------------------------
    def estimate_trim(
        self,
        baseboards: bool,
        crown: bool
    ):
        if baseboards:
            self.trim_cost += 150.0
        if crown:
            self.trim_cost += 200.0

    # -------------------------
    # Total
    # -------------------------
    def total(self) -> float:
        return round(
            self.wall_cost + self.ceiling_cost + self.trim_cost,
            2
        )

# Class for epoxy flooring
class EpoxyEstimator:
    def __init__(self):
        self.square_footage = 0.0
        self.epoxy_cost = 0.0

    def estimate_floor(
        self,
        length: float,
        width: float,
        epoxy_type: str
    ):
        self.square_footage = length * width

        rates = {
            "solid": 5.00,
            "chip": 6.00,
            "metallic": 7.50
        }

        rate = rates.get(epoxy_type, 5.00)
        self.epoxy_cost = self.square_footage * rate

    def total(self) -> float:
        return round(self.epoxy_cost, 2)
