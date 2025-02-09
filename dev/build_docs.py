#!/usr/bin/env python3
from local.notebook.export2html import convert_nb
from local.core.script import *
from local.torch_basics import *
import yaml, os, sys
from pathlib import Path

from sidebar_data import sidebar_d

def _leaf(k,v):
    url = 'external_url' if "http" in v else 'url'
    if url=='url': v=v+'.html'
    return {'title':k, url:v, 'output':'web,pdf'}

_k_names = ['folders', 'folderitems', 'subfolders', 'subfolderitems']
def _side_dict(title, data, level=0):
    k_name = _k_names[level]
    level += 1
    res = [(_side_dict(k, v, level) if isinstance(v,dict) else _leaf(k,v))
        for k,v in data.items()]
    return ({k_name:res} if not title
            else res if title.startswith('empty')
            else {'title': title, 'output':'web', k_name: res})

def _make_sidebar():
    "Making sidebar..."
    res = _side_dict('Sidebar', sidebar_d)
    res = {'entries': [res]}
    res_s = yaml.dump(res, default_flow_style=False)
    res_s = res_s.replace('- subfolders:', '  subfolders:').replace(' - - ', '   - ')
    res_s = """
#################################################
### THIS FILE WAS AUTOGENERATED! DO NOT EDIT! ###
#################################################
# Instead edit sidebar_d inside sidebar_data.py
"""+res_s
    open('../docs/_data/sidebars/home_sidebar.yml', 'w').write(res_s)

def convert_one(fname, dest_path, force_all):
    time.sleep(random.random())
    if fname.name.startswith('_'): return
    fname_out = Path(dest_path)/'.'.join(fname.with_suffix('.html').name.split('_')[1:])
    if not force_all and fname_out.exists() and os.path.getmtime(fname) < os.path.getmtime(fname_out): return
    print(f"converting: {fname} => {fname_out}")
    try: convert_nb(fname, dest_path=dest_path)
    except Exception as e: print(e)

def convert_all(path='.', dest_path='../docs', force_all=False):
    path = Path(path)
    #for fname in path.glob("[0-9]*.ipynb"): convert_one(fname, dest_path, force_all)
    parallel(convert_one, list(path.glob("[0-9]*.ipynb")), dest_path=dest_path, force_all=force_all)
    #convert_one(fname, dest_path, force_all)

@call_parse
def main(force_all:Param("Rebuild even notebooks that haven't changed", bool)=False):
    convert_all(dest_path='../docs', force_all=force_all)
    _make_sidebar()

