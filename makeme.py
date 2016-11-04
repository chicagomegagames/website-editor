#!/usr/bin/env python3

import argparse
import logging
import re

import markdown2 as m
import yaml

from jinja2 import Environment, FileSystemLoader
from os import makedirs, mkdir, walk
from os.path import basename, exists, getmtime, split, splitext
from shutil import copy2
from sys import exit

from app.server import run_app


l = logging.getLogger('Flourish! Makeme')

###
# Tasks
###
def generate(args):
  if not exists(args['dest']):
    l.info('Creating destination (' + args['dest'] + ") directory.")
    mkdir(args['dest'])

  generate_site(args)

###
# Generate stuffs
###
def generate_site(args):
  l.debug('Generating site.')
  env = Environment(loader=FileSystemLoader(args['src'] + '/templates'))
  site = {}
  parse_pages(args, site)
  parse_games(args, site)

  calendar_file = open(args['src'] + "calendar.yaml")
  site['calendar'] = yaml.load(calendar_file)
  calendar_file.close()

  make_site(args, site, env)


# parse out a file
def parse_file(filename):
  l.debug('Parsing file: ' + filename)
  parsed = {}

  f = open(filename)
  contents = ''
  for line in f:
    contents += line
  f.close()

  try:
    html = genHTML(contents)
    parsed['content'] = html
    parsed['config'] = html.metadata
    parsed['filename'] = basename(filename)
    parsed['changed'] = getmtime(filename)

    return parsed
  except Exception as e:
    l.critical("Couldn't parse yaml in " + filename)
    raise


# turn markdown into HTML
def genHTML(markdown):
  return m.markdown(markdown, extras=['fenced-code-blocks', 'metadata', 'smarty-pants'])

# find all files in directory `directory` and all subdirectories therein.
# using those files, parse them using `parse_fn`, and add the parsed contents
# to list `container`
def parse_dir(container, directory, parse_fn):
  for root, dirs, files in walk(directory):
    for f in files:
      if f[0] == ".":
        continue

      parsed_obj = parse_fn(root + "/" + f)
      if type(container) is list:
        container.append(parsed_obj)
      if type(container) is dict:
        container[parsed_obj["name"]] = parsed_obj

    for d in dirs:
      parse_dir(container, d, parse_fn)


###
# Page things
###

# parse all pages in a site
def parse_pages(args, site):
  pages = {}
  page_directory = args['src'] + '/pages'
  parse_dir(pages, page_directory, parse_page)

  site['pages'] = pages


# parse an individual page
def parse_page(filename):
  l.debug('Parsing page: ' + filename)
  print('Parsing page: ' + filename)

  page = parse_file(filename)
  page['title'] = page['config']['title']

  if 'layout' not in page['config']:
    page['layout'] = 'page.html'
  else:
    page['layout'] = page['config']['layout']

  if 'slug' in page['config']:
    page['slug'] = page['config']['slug']
  else:
    page['slug'] = splitext(page['filename'])[0]

  page["name"] = splitext(page['filename'])[0]

  return page


def parse_games(args, site):
  games = []
  games_directory = args["src"] + "/games"
  parse_dir(games, games_directory, parse_game)

  site["games"] = games

def parse_game(filename):
  l.debug("Parsing game: " + filename)

  game = parse_file(filename)

  game['name'] = game['config']['name']
  game['image'] = game['config']['image']
  game['blurb'] = game['content']
  game['slug'] = game['name'].lower().replace(" ", "-")

  return game

###
# The Magic
###

# start putting things together
def make_site(args, site, env):
  expand_pages(args, site, env)
  copy_assets(args, site)


# expand pages
def expand_pages(args, site, env):
  for _, page in site['pages'].items():
    #out_path = args['dest'] + page['slug']
    out_dir, out_file = split(args['dest'] + '/' + page['slug'])

    if out_file == '':
      out_file = 'index.html'
    else:
      # make sure this is really a file, and not a directory...
      # MUST HAVE `.` somewhere in name
      fname = 'index.html'

      for i in range(len(out_file) - 1, 0, -1):
        if out_file[i] == '.':
          fname = out_file
          break

      out_file = fname

    l.debug(str(exists(out_dir)) + "\t: " + out_dir)
    if not exists(out_dir):
      makedirs(out_dir)


    writer = open(out_dir + '/' + out_file, 'w')
    template = env.get_template(page['layout'])

    writer.write(template.render(site=site, page=page))
    writer.close()


# copy static assets
def copy_assets(args, site):
  if not exists(args['src'] + '/assets'):
    l.debug('no assets')
    return

  newPath = args['dest']

  for root, dirs, files in walk(args['src'] + '/assets'):
    for d in dirs:
      ndir = root + '/' + d
      ndir = ndir.replace(args['src'], newPath)

      if not exists(ndir):
        makedirs(ndir)

    for f in files:
      fPath = root + '/' + f
      nfPath = fPath.replace(args['src'], newPath)

      #if exists(nfPath):
      #  if getmtime(nfPath) > getmtime(fPath):
      #    continue

      copy2(fPath, nfPath)


def run_server(args):
  run_app()


if __name__ == '__main__':
  ###
  # Argument parsing things
  ###
  parser = argparse.ArgumentParser(description='Makeme is a simple static site generator.', prog="makeme.py")
  sub = parser.add_subparsers()

  # logging level parser.
  level = parser.add_mutually_exclusive_group()
  level.add_argument('-l', '--level', default='INFO', type=str.upper, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], help="Sets %(prog)s\'s log level.")
  level.add_argument('-q', '--quiet', action='store_const', const='ERROR', dest='level', help='Sets %(prog)s\'s log level to ERROR.')
  level.add_argument('-v', '--verbose', action='store_const', const='DEBUG', dest='level', help='Sets %(prog)\'s log level to DEBUG.')

  # generate parser
  gen = sub.add_parser('generate')
  gen.add_argument('src', nargs='?', default='./', metavar='source', help='The directory %(prog)s looks in for source files.')
  gen.add_argument('dest', nargs='?', default='./_site', metavar='destination', help='The directory %(prog)s outputs to.')
  gen.set_defaults(func=generate)

  arg_server = sub.add_parser("server")
  arg_server.set_defaults(func=run_server)

  args = vars(parser.parse_args())

  l.setLevel(logging.DEBUG)

  print(args)
  args['func'](args)
