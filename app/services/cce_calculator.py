from app.models.schemas import CCECalculationRequest, CCECalculationResponse

class CCECalculatorService:
    @staticmethod
    def calculate(req: CCECalculationRequest) -> CCECalculationResponse:
        """
        Standardized Crop Cutting Experiment (CCE) Yield Calculation Formula
        Used by the Directorate of Economics & Statistics (DES) & ASSAC.
        
        Formula:
          Yield (t/ha) = (GrainWeightKg * (100 - Moisture%) / (100 - StdMoisture%) / PlotAreaSqM) * 10
        """
        if req.freshGrainKg <= 0 or req.plotAreaSqM <= 0:
            return CCECalculationResponse(
                calculatedYieldTHa=0.0,
                adjustedMoistureFactor=1.0,
                dryGrainEquivalentKg=0.0
            )

        # Moisture correction factor
        std_moisture = req.standardMoisturePct
        moisture_factor = (100.0 - req.moisturePct) / (100.0 - std_moisture)
        
        # Dry grain equivalent for experimental plot
        dry_grain_kg = req.freshGrainKg * moisture_factor
        
        # Scale to tonnes per hectare (1 ha = 10,000 sq.m; 1 tonne = 1,000 kg => factor = 10)
        yield_t_ha = (dry_grain_kg / req.plotAreaSqM) * 10.0
        
        return CCECalculationResponse(
            calculatedYieldTHa=round(yield_t_ha, 2),
            adjustedMoistureFactor=round(moisture_factor, 4),
            dryGrainEquivalentKg=round(dry_grain_kg, 2)
        )

cce_calculator = CCECalculatorService()
