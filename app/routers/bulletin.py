from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from app.services.forecast_engine import forecast_engine
from app.services.data_manager import data_manager
from app.models.schemas import ForecastRequest

router = APIRouter(prefix="/bulletin", tags=["Official Bulletins"])

@router.get("/generate", response_class=HTMLResponse, summary="Generate printable HTML official Assam Agricultural Bulletin")
def generate_bulletin(crop_id: str = "crop_sali_rice", lead_time_days: int = 30):
    fc = forecast_engine.generate_forecast(ForecastRequest(cropId=crop_id, leadTimeDays=lead_time_days))
    districts = data_manager.get_districts()[:12] # Top sample districts

    rows_html = "".join([
        f"""
        <tr>
          <td><strong>{d.name}</strong></td>
          <td>{d.zone}</td>
          <td>{d.currentCroppedAreaHa:,.0f}</td>
          <td>{d.predictedAvgYield:.2f}</td>
          <td>{(d.currentCroppedAreaHa * d.predictedAvgYield):,.0f}</td>
          <td style="color: #dc2626;">{d.floodDamagedHa:,.0f}</td>
          <td>±{d.uncertaintyMarginPct}%</td>
        </tr>
        """ for d in districts
    ])

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>Assam Agricultural Forecast Bulletin - NESFIC-D-12</title>
      <style>
        body {{ font-family: 'Segoe UI', Tahoma, sans-serif; padding: 40px; color: #1e293b; max-width: 900px; margin: 0 auto; line-height: 1.5; }}
        .header {{ text-align: center; border-bottom: 2px solid #0f172a; padding-bottom: 15px; margin-bottom: 25px; }}
        .logo {{ font-size: 20px; font-weight: bold; text-transform: uppercase; color: #1e3a8a; }}
        .sub {{ font-size: 13px; color: #475569; }}
        .badge {{ display: inline-block; padding: 4px 10px; background: #e0f2fe; color: #0369a1; border-radius: 4px; font-weight: bold; font-size: 12px; margin-top: 5px; }}
        .kpi-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 25px; }}
        .kpi-card {{ border: 1px solid #cbd5e1; border-radius: 6px; padding: 12px; background: #f8fafc; }}
        .kpi-title {{ font-size: 11px; text-transform: uppercase; color: #64748b; font-weight: bold; }}
        .kpi-value {{ font-size: 20px; font-weight: bold; color: #0f172a; margin-top: 4px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 12px; }}
        th, td {{ border: 1px solid #cbd5e1; padding: 8px 10px; text-align: left; }}
        th {{ background: #f1f5f9; font-weight: bold; }}
        .footer {{ margin-top: 40px; border-top: 1px solid #cbd5e1; padding-top: 15px; font-size: 11px; color: #64748b; display: flex; justify-content: space-between; }}
      </style>
    </head>
    <body>
      <div class="header">
        <div class="logo">GOVERNMENT OF ASSAM</div>
        <div style="font-weight: bold; font-size: 15px;">ASSAM STATE SPACE APPLICATIONS CENTRE (ASSAC)</div>
        <div class="sub">Directorate of Agriculture & Directorate of Economics & Statistics</div>
        <div class="badge">OFFICIAL ADVANCE PRE-HARVEST AGRICULTURAL BULLETIN · T-{lead_time_days} DAYS ({fc.leadTimeLabel})</div>
      </div>

      <div>
        <h3>Target Crop: {fc.crop} ({fc.season}) — Scope: {fc.scope}</h3>
        <p style="font-size: 13px; color: #334155;">
          Synthesized from <strong>Sentinel-1 SAR Radar & Optical Fusion</strong> with Bayesian confidence bounds.
        </p>
      </div>

      <div class="kpi-grid">
        <div class="kpi-card">
          <div class="kpi-title">Total Standing Acreage</div>
          <div class="kpi-value">{fc.totalAreaHa:,.0f} ha</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-title">Predicted Average Yield</div>
          <div class="kpi-value">{fc.avgYieldTHa:.2f} t/ha</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-title">Projected Production</div>
          <div class="kpi-value">{fc.totalProductionTonnes:,.0f} MT</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-title">90% Confidence Interval</div>
          <div class="kpi-value" style="font-size: 15px;">{fc.confidenceInterval90.lower:,.0f} – {fc.confidenceInterval90.upper:,.0f} MT</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-title">Flood-Affected Acreage</div>
          <div class="kpi-value" style="color: #dc2626;">{fc.floodDamagedHa:,.0f} ha</div>
        </div>
        <div class="kpi-card">
          <div class="kpi-title">Estimated Crop Loss</div>
          <div class="kpi-value" style="color: #dc2626;">{fc.estimatedLostProductionTonnes:,.0f} MT</div>
        </div>
      </div>

      <h4>District Sample Matrix</h4>
      <table>
        <thead>
          <tr>
            <th>District</th>
            <th>Agro Zone</th>
            <th>Acreage (ha)</th>
            <th>Yield (t/ha)</th>
            <th>Production (MT)</th>
            <th>Flood Loss (ha)</th>
            <th>Uncertainty</th>
          </tr>
        </thead>
        <tbody>
          {rows_html}
        </tbody>
      </table>

      <div class="footer">
        <div>Forecast Ref: <code>{fc.forecastId}</code> · Engine: GeoCrop-NE Core</div>
        <div>Authorized Signatory: ________________________ (ASSAC / Agriculture Directorate)</div>
      </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
