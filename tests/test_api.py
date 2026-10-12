import unittest
from app.models.schemas import CCECalculationRequest, ForecastRequest
from app.services.cce_calculator import cce_calculator
from app.services.forecast_engine import forecast_engine
from app.services.data_manager import data_manager

class TestGeoCropBackend(unittest.TestCase):
    def test_cce_calculator(self):
        # 5m x 5m plot (25 sq.m), 7.25 kg fresh grain, 15.2% moisture, 14% std
        req = CCECalculationRequest(
            freshGrainKg=7.25,
            moisturePct=15.2,
            standardMoisturePct=14.0,
            plotAreaSqM=25.0
        )
        res = cce_calculator.calculate(req)
        self.assertGreater(res.calculatedYieldTHa, 2.5)
        self.assertLess(res.calculatedYieldTHa, 3.2)
        self.assertAlmostEqual(res.calculatedYieldTHa, 2.86, places=1)

    def test_crops_data(self):
        crops = data_manager.get_crops()
        self.assertGreater(len(crops), 30)
        sali_rice = data_manager.get_crop("crop_sali_rice")
        self.assertIsNotNone(sali_rice)
        self.assertEqual(sali_rice.category, "Cereals & Grains")

    def test_districts_data(self):
        districts = data_manager.get_districts()
        self.assertEqual(len(districts), 35)
        kamrup = data_manager.get_district("dist_kamrup")
        self.assertIsNotNone(kamrup)

    def test_forecast_uncertainty_bounds(self):
        req = ForecastRequest(cropId="crop_sali_rice", leadTimeDays=30)
        fc = forecast_engine.generate_forecast(req)
        self.assertGreater(fc.totalProductionTonnes, 0)
        self.assertLess(fc.confidenceInterval90.lower, fc.totalProductionTonnes)
        self.assertGreater(fc.confidenceInterval90.upper, fc.totalProductionTonnes)
        self.assertLess(fc.confidenceInterval95.lower, fc.confidenceInterval90.lower)
        self.assertGreater(fc.confidenceInterval95.upper, fc.confidenceInterval90.upper)

if __name__ == "__main__":
    unittest.main()
