"""
Claims — Excel Importer (Python) — v0.3

Delta from v0.2:
- Supports optional sheet `layer_applicability` with columns: benefit_code, layer (IL|AC|both)
- Stricter normalization for Indonesian labels; consolidated error CSV includes sheet & row
- Compatible with new DDL columns (no schema break)

Usage:
  export DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/db
  python import_plan_benefits.py --excel /path/to/import-policy-benefit.xlsx --plan-id <UUID> --effective-from 2025-01-01
"""
import argparse
import os
import sys
import uuid
import pandas as pd
from sqlalchemy import create_engine, text

LIMIT_NORM = {'per kejadian':'incident','per hari':'day','per tahun':'year'}
FACILITY_NORM = {'cashless & reimb':'both','cashless & reimburse':'both','cashless':'cashless','reimburse':'reimburse','reimb':'reimburse'}


def truthy(v):
    s = str(v).strip().lower()
    return s in ('1','true','ya','yes','y','dibayar','boleh','allow','allowed','menggunakan','use')


def load_sheet(xls, name):
    try:
        return pd.read_excel(xls, name)
    except ValueError:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--excel', required=True)
    ap.add_argument('--plan-id', required=True)
    ap.add_argument('--effective-from', required=True)
    args = ap.parse_args()

    plan_id = str(uuid.UUID(args.plan_id))
    eff_from = pd.to_datetime(args.effective_from).date()

    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print('ERROR: set DATABASE_URL')
        sys.exit(2)
    engine = create_engine(db_url)

    xls = pd.ExcelFile(args.excel)
    main_df = pd.read_excel(xls)
    main_df.columns = [c.strip().lower() for c in main_df.columns]

    alias = {
        'benefit code': 'benefit_code',
        'benefit name': 'benefit_name',
        'benefit type': 'benefit_type',
        'limitation type': 'limitation_type',
        'maximum value': 'maximum_value',
        'limitation type qty': 'limitation_type_qty',
        'maximum limitation': 'maximum_limitation',
        'multiple condition': 'multiple_condition',
        'flag expenses excess': 'flag_expenses_excess',
        'persen penggantian %': 'coins_pct',
        'flag aso': 'flag_aso',
        'flag facility': 'flag_facility',
        'layer applicability': 'layer_applicability',
    }
    main_df = main_df.rename(columns={k:v for k,v in alias.items() if k in main_df.columns})

    required = ['benefit_code','benefit_name','limitation_type','maximum_value']
    missing = [c for c in required if c not in main_df.columns]
    if missing:
        raise SystemExit(f"Missing required columns: {missing}")

    # Optional sheet: layer_applicability
    layers_df = load_sheet(xls, 'layer_applicability')
    layer_map = {}
    if layers_df is not None:
        layers_df.columns = [c.strip().lower() for c in layers_df.columns]
        for _, r in layers_df.iterrows():
            bc = str(r.get('benefit_code','')).strip()
            layer = str(r.get('layer','')).strip().upper()
            if bc:
                layer_map[bc] = layer if layer in ('IL','AC','BOTH') else 'BOTH'

    errors = []
    rows = []
    for i, r in main_df.iterrows():
        try:
            benefit_code = str(r['benefit_code']).strip()
            name = str(r.get('benefit_name','')).strip()
            lb_raw = str(r['limitation_type']).strip().lower()
            limit_basis = LIMIT_NORM.get(lb_raw)
            if not limit_basis:
                raise ValueError(f"Invalid limitation_type: {r['limitation_type']}")
            limit_value = float(r['maximum_value'] or 0)
            qty_value = int(r.get('limitation_type_qty', 0) or 0)
            max_count = int(r.get('maximum_limitation', 0) or 0)
            group = r.get('multiple_condition')
            limit_group_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(group))) if pd.notna(group) and str(group).strip() else None
            coins_pct = float(r.get('coins_pct', 0) or 0)
            if coins_pct < 0 or coins_pct > 100:
                raise ValueError('coins_pct must be 0..100')
            fac = FACILITY_NORM.get(str(r.get('flag_facility','both')).strip().lower(), 'both')
            allow_excess_draw = truthy(r.get('flag_expenses_excess', ''))
            aso_applicable = truthy(r.get('flag_aso',''))
            layer_app = layer_map.get(benefit_code, str(r.get('layer_applicability','both')).strip().upper() or 'BOTH')

            rows.append({
                'plan_id': plan_id,
                'benefit_code': benefit_code,
                'name': name,
                'type': str(r.get('benefit_type','') or ''),
                'limit_basis': limit_basis,
                'limit_value': limit_value,
                'qty_value': qty_value,
                'max_count': max_count,
                'limit_group_id': limit_group_id,
                'coins_pct': coins_pct,
                'facility_mode': fac,
                'allow_excess_draw': allow_excess_draw,
                'aso_applicable': aso_applicable,
                'tpa_route': None,
                'effective_from': eff_from,
                'layer_applicability': layer_app
            })
        except Exception as e:
            errors.append({'sheet':'main','row_index': int(i), 'error': str(e)})

    if errors:
        pd.DataFrame(errors).to_csv(args.excel + '.errors.csv', index=False)

    if not rows:
        print('No valid rows to import')
        return

    with create_engine(db_url).begin() as conn:
        # Ensure column exists (layer_applicability on plan_benefit)
        conn.execute(text("""
          DO $$ BEGIN
            IF NOT EXISTS (
              SELECT 1 FROM information_schema.columns 
              WHERE table_schema='claims' AND table_name='plan_benefit' AND column_name='layer_applicability') THEN
              ALTER TABLE claims.plan_benefit ADD COLUMN layer_applicability TEXT;
            END IF;
          END $$;
        """))
        for r in rows:
            sql = text('''
                INSERT INTO claims.plan_benefit (
                  plan_id, benefit_code, name, type, limit_basis, limit_value, qty_value, max_count,
                  limit_group_id, coins_pct, facility_mode, allow_excess_draw, aso_applicable, tpa_route,
                  effective_from, layer_applicability
                ) VALUES (
                  :plan_id, :benefit_code, :name, :type, :limit_basis, :limit_value, :qty_value, :max_count,
                  :limit_group_id, :coins_pct, :facility_mode, :allow_excess_draw, :aso_applicable, :tpa_route,
                  :effective_from, :layer_applicability
                )
                ON CONFLICT (plan_id, benefit_code, effective_from)
                DO UPDATE SET
                  name = EXCLUDED.name,
                  type = EXCLUDED.type,
                  limit_basis = EXCLUDED.limit_basis,
                  limit_value = EXCLUDED.limit_value,
                  qty_value = EXCLUDED.qty_value,
                  max_count = EXCLUDED.max_count,
                  limit_group_id = EXCLUDED.limit_group_id,
                  coins_pct = EXCLUDED.coins_pct,
                  facility_mode = EXCLUDED.facility_mode,
                  allow_excess_draw = EXCLUDED.allow_excess_draw,
                  aso_applicable = EXCLUDED.aso_applicable,
                  tpa_route = EXCLUDED.tpa_route,
                  layer_applicability = EXCLUDED.layer_applicability
            ''')
            conn.execute(sql, r)
    print(f"Imported/updated {len(rows)} plan_benefit rows (v0.3)")

if __name__ == '__main__':
    main()
