#!/usr/bin/env python
import os, os.path, subprocess

# TODO: more libraries could be tried (could just iterate over /System/Library/Frameworks)

# Paths that dump_syms has to look at
paths = [
  "/usr/lib/libSystem.B.dylib",
  "/usr/lib/libobjc.dylib",
  "/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation",
  "/System/Library/Frameworks/AppKit.framework/AppKit",
  "/System/Library/Frameworks/Foundation.framework/Foundation",
  "/System/Library/Frameworks/Cocoa.framework/Cocoa",
  "/System/Library/Frameworks/Carbon.framework/Carbon",
  "/System/Library/Frameworks/Carbon.framework/Frameworks/HIToolbox.framework/HIToolbox",
  "/System/Library/Frameworks/QuartzCore.framework/QuartzCore",
  "/System/Library/Frameworks/CoreServices.framework/Frameworks/AE.framework/AE",
  "/System/Library/Frameworks/CoreServices.framework/Frameworks/CFNetwork.framework/CFNetwork",
  "/System/Library/Frameworks/CoreServices.framework/Frameworks/CarbonCore.framework/CarbonCore",
  "/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/LaunchServices",
  "/System/Library/Frameworks/CoreServices.framework/Frameworks/OSServices.framework/OSServices",
  "/System/Library/Frameworks/CoreServices.framework/Frameworks/SearchKit.framework/SearchKit",
  "/System/Library/PrivateFrameworks/DesktopServicesPriv.framework/DesktopServicesPriv",
]

g_script_dir = None
def script_dir():
    global g_script_dir
    if g_script_dir is None:
        g_script_dir = os.path.dirname(os.path.realpath(__file__))
    return g_script_dir

# bin directory, where dump_syms is present
def bin_dir():
  return os.path.join(os.path.dirname(script_dir()), "bin")

# path to dump_syms executable
def dump_syms_path():
  path = os.path.join(bin_dir(), "dump_syms")
  assert os.path.exists(path)
  return path

def crashdumps_base_dir(): return os.path.realpath(os.path.expanduser("~/src/maccrashdumps"))
def symbols_dir(): return os.path.join(crashdumps_base_dir(), "symbols")

def ensure_dir_exists(path):
  if os.path.exists(path):
    if os.path.isdir(path): return
    raise Exception, "Path %s already exists but is not a directory"
  os.makedirs(path)

def write_to_file(path, txt):
  fo = open(path, "wb")
  fo.write(txt)
  fo.close()

def run_cmd_throw(*args):
  cmd = " ".join(args)
  print("Running '%s'" % cmd)
  cmdproc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  res = cmdproc.communicate()
  errcode = cmdproc.returncode
  if 0 != errcode:
    print "Failed with error code %d" % errcode
    print "Stdout:"
    print res[0]
    print "Stderr:"
    print res[1]
    raise Exception("'%s' failed with error code %d" % (cmd, errcode))
  return (res[0], res[1])

# minidump_stackwalk requires symbol files conform to strict
# file layout hierarchy:
# $root/${module_name}/${module_id}/${module_name}.sym
# This can be extracted from the first line in dump file, which looks like:
# MODULE mac x86 294DFE5737329F65A13AAD2FBC08E1670 uTorrent
# i.e. $module_id is 4th element and $module_name is 5th. We pass $root as argument
def save_symbols(data, root_dir):
  lines = data.split("\n")
  l = lines[0]
  parts = l.split()
  module_id = parts[3]
  module_name = parts[4]
  assert len(module_id) == 33
  symbol_file_dir = os.path.join(root_dir, module_name, module_id)
  ensure_dir_exists(symbol_file_dir)
  symbol_file_path = os.path.join(symbol_file_dir, module_name + ".sym")
  write_to_file(symbol_file_path, data)
  print("Wrote symbols file %s" % symbol_file_path)

def dump_symbols(path):
  # create human-readable version of crashdump
  try:
    (out, err) = run_cmd_throw(dump_syms_path(), path)
  except:
    print "Failed to dump symbols for %s" % path
    #raise
  save_symbols(out, symbols_dir())

def main():
  for p in paths:
    dump_symbols(p)

if __name__ == "__main__":
  main()
