#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from typing import Optional, List
import numpy as np
import pandas as pd

# ⬇️ backend امن برای محیط‌های IDE/سِروِر (جلوگیری از خطای FigureCanvasInterAgg)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from astroquery.ipac.nexsci.nasa_exoplanet_archive import NasaExoplanetArchive as NEO

METHOD_PALETTE = {
    'Transit': '#1f77b4',
    'Radial Velocity': '#ff7f0e',
    'Imaging': '#2ca02c',
    'Microlensing': '#d62728',
    'Timing': '#9467bd',
    'Astrometry': '#8c564b',
    'Other': '#7f7f7f'
}
PROJECT_MARKERS = {'Kepler/K2': 'o', 'TESS': 's', 'Other': '^'}

def pick_col(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
    for c in candidates:
        if c in df.columns:
            return c
    return None

def norm_method(raw: Optional[str]) -> str:
    if not isinstance(raw, str): return 'Other'
    t = raw.lower()
    if 'transit' in t: return 'Transit'
    if 'radial' in t or 'rv' in t: return 'Radial Velocity'
    if 'imaging' in t or 'direct' in t: return 'Imaging'
    if 'microlens' in t: return 'Microlensing'
    if 'timing' in t or 'pulsar' in t: return 'Timing'
    if 'astrom' in t: return 'Astrometry'
    return 'Other'

def norm_project(row, fac_col, host_col, name_col) -> str:
    fac  = str(row[fac_col])  if fac_col  and pd.notna(row.get(fac_col))  else ''
    host = str(row[host_col]) if host_col and pd.notna(row.get(host_col)) else ''
    name = str(row[name_col]) if name_col and pd.notna(row.get(name_col)) else ''
    txt = (fac + ' ' + host + ' ' + name).lower()
    if ('kepler' in txt) or (' k2 ' in txt) or host.startswith('Kepler-') or host.startswith('K2-'):
        return 'Kepler/K2'
    if ('tess' in txt) or ('toi' in host.lower()) or ('toi' in name.lower()) or ('tic ' in host.lower()):
        return 'TESS'
    return 'Other'

def apply_filters(df: pd.DataFrame, args) -> pd.DataFrame:
    out = df.copy()
    if args.year_min is not None or args.year_max is not None:
        year_col = pick_col(out, ['disc_year', 'discyear', 'disc_yearnum'])
        if year_col:
            out[year_col] = pd.to_numeric(out[year_col], errors='coerce')
            if args.year_min is not None: out = out[out[year_col] >= args.year_min]
            if args.year_max is not None: out = out[out[year_col] <= args.year_max]
    if args.method:  out = out[out['_method'].isin(args.method)]
    if args.project: out = out[out['_project'].isin(args.project)]
    return out

def load_and_prepare():
    tab = NEO.query_criteria(table="pscomppars", select="*")
    df = tab.to_pandas()

    ra_col   = pick_col(df, ['ra', 'ra_str', 'rastr'])
    dec_col  = pick_col(df, ['dec', 'dec_str', 'decstr'])
    name_col = pick_col(df, ['pl_name', 'planet_name'])
    meth_col = pick_col(df, ['discoverymethod', 'disc_method', 'method'])
    fac_col  = pick_col(df, ['disc_facility', 'pl_facility', 'facility', 'discoveryfacility'])
    host_col = pick_col(df, ['hostname', 'host_name'])
    if not ra_col or not dec_col or not name_col:
        raise SystemExit("RA/Dec/Name columns not found in pscomppars.")

    df = df.dropna(subset=[ra_col, dec_col]).copy()
    df['RAdeg'] = pd.to_numeric(df[ra_col], errors='coerce')
    df['DEdeg'] = pd.to_numeric(df[dec_col], errors='coerce')
    df = df.dropna(subset=['RAdeg', 'DEdeg'])

    if 'pl_rade' in df.columns:
        df['_size'] = 10 + 3 * df['pl_rade'].clip(upper=20).fillna(1)
    else:
        df['_size'] = 12.0

    df['_method']  = df[meth_col].apply(norm_method) if meth_col else 'Other'
    df['_color']   = df['_method'].map(METHOD_PALETTE).fillna('#7f7f7f')
    df['_project'] = df.apply(lambda r: norm_project(r, fac_col, host_col, name_col), axis=1)

    ra = np.radians(df['RAdeg'].values)
    dec = np.radians(df['DEdeg'].values)
    ra = np.remainder(ra + 2*np.pi, 2*np.pi); ra[ra > np.pi] -= 2*np.pi
    df['_ra_rad'] = -ra
    df['_dec_rad'] = dec

    cols_info = dict(ra='RAdeg', dec='DEdeg', name=name_col, method=meth_col, facility=fac_col, host=host_col)
    return df, cols_info

def open_with_default_viewer(path: str):
    """فایل تصویر ذخیره‌شده را با برنامهٔ پیش‌فرض سیستم باز می‌کند."""
    import os, sys, subprocess
    try:
        if sys.platform.startswith('win'):
            os.startfile(path)  # ویندوز
        elif sys.platform == 'darwin':
            subprocess.run(['open', path], check=False)  # مک
        else:
            subprocess.run(['xdg-open', path], check=False)  # لینوکس
    except Exception as e:
        print(f"[WARN] Could not auto-open image: {e}")

def plot_aitoff(df: pd.DataFrame, png_path: str, title_extra: str = ''):
    plt.figure(figsize=(11, 7))
    ax = plt.subplot(111, projection="aitoff")
    ax.grid(True, alpha=0.4)
    title = "Confirmed Exoplanets — Aitoff Map\nColor = Discovery Method, Shape = Project (Kepler/TESS/Other)"
    if title_extra: title += f"\n{title_extra}"
    plt.title(title)

    artists_color_legend = {}
    artists_shape_legend = {}

    for project, marker in PROJECT_MARKERS.items():
        sel_p = (df['_project'] == project).values
        for method, color in METHOD_PALETTE.items():
            sel = sel_p & (df['_method'] == method).values
            if not np.any(sel): continue
            ax.scatter(df.loc[sel, '_ra_rad'], df.loc[sel, '_dec_rad'],
                       s=df.loc[sel, '_size'], c=df.loc[sel, '_color'],
                       marker=marker, alpha=0.75, edgecolors='none')
            if method not in artists_color_legend:
                artists_color_legend[method] = plt.Line2D([0],[0], marker='o', color='none',
                                                          markerfacecolor=color, markersize=8, label=method)
        artists_shape_legend[project] = plt.Line2D([0],[0], marker=marker, color='k',
                                                   markerfacecolor='white', markersize=8,
                                                   linestyle='None', label=project)

    leg1 = ax.legend(handles=list(artists_color_legend.values()),
                     title="Discovery Method", loc="lower left",
                     bbox_to_anchor=(0.0, -0.15), ncol=3, frameon=True)
    ax.add_artist(leg1)
    leg2 = ax.legend(handles=list(artists_shape_legend.values()),
                     title="Project", loc="lower right",
                     bbox_to_anchor=(1.0, -0.15), ncol=3, frameon=True)

    plt.tight_layout()
    plt.savefig(png_path, dpi=180, bbox_inches='tight')
    plt.close()
    print(f"Saved PNG: {png_path}")
    open_with_default_viewer(png_path)  # ← تصویر را با برنامهٔ پیش‌فرض سیستم باز می‌کند

def save_snapshot(df: pd.DataFrame, cols_info: dict, tag: str):
    cols = [c for c in [cols_info.get('name'), 'RAdeg', 'DEdeg',
                        cols_info.get('method'), cols_info.get('facility'), cols_info.get('host'),
                        '_method', '_project']
            if (c in df.columns) or (c in ['RAdeg','DEdeg','_method','_project'])]
    snap = df[cols].copy()
    csv_path = f"exoplanets_snapshot_{tag}.csv"
    xlsx_path = f"exoplanets_snapshot_{tag}.xlsx"
    snap.to_csv(csv_path, index=False)
    with pd.ExcelWriter(xlsx_path, engine='openpyxl') as w:
        snap.to_excel(w, sheet_name='exoplanets', index=False)
    print(f"Saved CSV : {csv_path}")
    print(f"Saved XLSX: {xlsx_path}")

def parse_args():
    p = argparse.ArgumentParser(description="Aitoff sky map of confirmed exoplanets. Color=method, Shape=project.")
    p.add_argument('--year-min', type=int, default=None)
    p.add_argument('--year-max', type=int, default=None)
    p.add_argument('--method', nargs='*', default=None)
    p.add_argument('--project', nargs='*', default=None)
    p.add_argument('--tag', default='all')
    return p.parse_args()

def main():
    args = parse_args()
    df, cols_info = load_and_prepare()
    n_all = len(df)
    df = apply_filters(df, args)
    print(f"Rows: {len(df)} (from {n_all} total)")
    title_extra = " | ".join(filter(None, [
        f"Year: {args.year_min or '—'}–{args.year_max or '—'}" if (args.year_min or args.year_max) else "",
        ("Method: " + ", ".join(args.method)) if args.method else "",
        ("Project: " + ", ".join(args.project)) if args.project else "",
    ]))
    plot_aitoff(df, png_path=f"exoplanets_aitoff_{args.tag}.png", title_extra=title_extra)
    save_snapshot(df, cols_info, args.tag)

if __name__ == "__main__":
    main()
