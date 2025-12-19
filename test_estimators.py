import unittest

from estimatePredictionTool import PaintEstimator, EpoxyEstimator

class TestPaintEstimator(unittest.TestCase):

    def setUp(self):
        self.paint = PaintEstimator()

    def test_wall_estimate_refresh_coat(self):
        self.paint.estimate_walls(
            length=10,
            width=10,
            height=9,
            full_repaint=False
        )

        # square footage = 100
        # base rate = 2.50
        # 1 coat
        self.assertAlmostEqual(self.paint.wall_cost, 250.00)

    def test_wall_estimate_full_repaint(self):
        self.paint.estimate_walls(
            length=10,
            width=10,
            height=9,
            full_repaint=True
        )

        # 3 coats
        self.assertAlmostEqual(self.paint.wall_cost, 750.00)

    def test_ceiling_painted(self):
        self.paint.estimate_walls(
            length=10,
            width=10,
            height=9,
            full_repaint=False
        )

        self.paint.estimate_ceiling(
            paint_ceiling=True,
            full_repaint=False
        )

        # ceiling rate = 1.50 * 100 sqft
        self.assertAlmostEqual(self.paint.ceiling_cost, 150.00)

    def test_trim_baseboards_only(self):
        self.paint.estimate_trim(
            baseboards=True,
            crown=False
        )

        self.assertEqual(self.paint.trim_cost, 150.00)

    def test_total_paint_cost(self):
        self.paint.estimate_walls(10, 10, 9, True)
        self.paint.estimate_ceiling(True, False)
        self.paint.estimate_trim(True, True)

        total = self.paint.total()

        # walls: 750
        # ceiling: 150
        # trim: 350
        self.assertAlmostEqual(total, 1250.00)

class TestEpoxyEstimator(unittest.TestCase):

    def setUp(self):
        self.epoxy = EpoxyEstimator()

    def test_solid_epoxy(self):
        self.epoxy.estimate_floor(
            length=20,
            width=20,
            epoxy_type="solid"
        )

        # 400 sqft * $5.00
        self.assertAlmostEqual(self.epoxy.total(), 2000.00)

    def test_chip_epoxy(self):
        self.epoxy.estimate_floor(
            length=10,
            width=10,
            epoxy_type="chip"
        )

        # 100 sqft * $6.00
        self.assertAlmostEqual(self.epoxy.total(), 600.00)

    def test_metallic_epoxy(self):
        self.epoxy.estimate_floor(
            length=10,
            width=10,
            epoxy_type="metallic"
        )

        # 100 sqft * $7.50
        self.assertAlmostEqual(self.epoxy.total(), 750.00)

    def test_default_epoxy_type(self):
        self.epoxy.estimate_floor(
            length=10,
            width=10,
            epoxy_type="unknown"
        )

        # fallback to solid rate
        self.assertAlmostEqual(self.epoxy.total(), 500.00)
